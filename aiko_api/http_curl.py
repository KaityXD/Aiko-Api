import json
import time
from curl_cffi import requests
from .katlog import get_logger
from .common.errors import HTTPException, Forbidden, NotFound, DiscordServerError
from .common.constants import DISCORD_API
from .core.headers import HeaderBuilder

log = get_logger("aiko_api", level="DEBUG")


class HTTP:
    def __init__(
        self, token: str = None, impersonate: str = "chrome120", proxy: str = None
    ):
        self.token = token
        self.impersonate = impersonate
        self.proxy = proxy
        self._session = None
        self.header_builder = HeaderBuilder(token)

    def _get_session(self):
        if not self._session:
            self._session = requests.Session(
                impersonate=self.impersonate,
                proxies={"http": self.proxy, "https": self.proxy} if self.proxy else None,
            )
        return self._session

    def request(self, method: str, endpoint: str, **kwargs):
        session = self._get_session()
        url = DISCORD_API + endpoint

        headers = self.header_builder.build(context=kwargs.pop("context", None))
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        # Extract files, data, and json to handle them for multipart if needed
        files = kwargs.pop("files", None)
        data = kwargs.pop("data", None)
        json_payload = kwargs.pop("json", None)

        # If files are present, remove Content-Type to let requests set it for multipart/form-data
        if files and "Content-Type" in headers:
            headers.pop("Content-Type")

        tries = 0
        max_retries = 5

        while tries < max_retries:
            mp = None
            # Use local kwargs for this specific request attempt
            attempt_kwargs = kwargs.copy()
            
            if files:
                from curl_cffi import CurlMime
                mp = CurlMime()
                
                # Add data fields to multipart
                if data:
                    if isinstance(data, dict):
                        for k, v in data.items():
                            mp.addpart(name=k, data=str(v))
                    else:
                        mp.addpart(name="data", data=str(data))
                
                # If json is provided with files, Discord expects it in payload_json field
                if json_payload and not data:
                    mp.addpart(name="payload_json", data=json.dumps(json_payload, separators=(",", ":")))
                elif json_payload:
                    # If both data and json are provided (unusual), just add json as a field?
                    mp.addpart(name="json", data=json.dumps(json_payload, separators=(",", ":")))

                for name, file_info in files.items():
                    filename = None
                    if isinstance(file_info, tuple):
                        filename, fp = file_info
                    else:
                        fp = file_info
                    
                    if isinstance(fp, str):
                        mp.addpart(name=name, filename=filename, local_path=fp)
                    elif hasattr(fp, "read"):
                        if hasattr(fp, "seek"):
                            fp.seek(0)
                        content = fp.read()
                        if not isinstance(content, bytes):
                            content = str(content).encode()
                        mp.addpart(name=name, filename=filename, data=content)
                    else:
                        content = fp
                        if not isinstance(content, bytes):
                            content = str(content).encode()
                        mp.addpart(name=name, filename=filename, data=content)
                
                attempt_kwargs["multipart"] = mp
            else:
                if data: attempt_kwargs["data"] = data
                if json_payload: attempt_kwargs["json"] = json_payload

            try:
                resp = session.request(
                    method, url, headers=headers, **attempt_kwargs
                )

                try:
                    content = resp.json()
                except:
                    content = resp.text

                if resp.status_code == 429:
                    retry_after = (
                        content.get("retry_after", 1)
                        if isinstance(content, dict)
                        else 1
                    )
                    log.warn(f"Rate limited. Retrying after {retry_after}s")
                    time.sleep(retry_after)
                    continue

                if 200 <= resp.status_code < 300:
                    return content

                if resp.status_code >= 500:
                    delay = 1 + (tries * 2)
                    log.error(
                        f"Server error {resp.status_code}. Retrying after {delay}s"
                    )
                    time.sleep(delay)
                    tries += 1
                    continue

                # Prepare a dummy response object for HTTPException compatibility
                class DummyResponse:
                    def __init__(self, status, text):
                        self.status = status
                        self.text = text

                dummy = DummyResponse(resp.status_code, content)

                if resp.status_code == 403:
                    raise Forbidden(dummy, content)
                elif resp.status_code == 404:
                    raise NotFound(dummy, content)
                else:
                    raise HTTPException(dummy, content)

            except (Forbidden, NotFound, HTTPException):
                raise
            except Exception as e:
                log.error(f"Request failed: {type(e).__name__}: {e}")
                time.sleep(1 + tries * 2)
                tries += 1
                continue
            finally:
                if mp:
                    mp.close()

        raise HTTPException(None, "Max retries exceeded")

    def get(self, endpoint: str, **kwargs):
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs):
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs):
        return self.request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs):
        return self.request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        return self.request("DELETE", endpoint, **kwargs)

    def login(self):
        return self.get("/users/@me")

    def create_dm(self, recipient_id: int):
        return self.post(
            "/users/@me/channels", json={"recipient_id": str(recipient_id)}
        )

    def send_message(
        self,
        channel_id: int,
        content: str,
        message_reference: dict = None,
        files: list = None,
    ):
        payload = {"content": content}
        if message_reference:
            payload["message_reference"] = message_reference

        if files:
            file_data = {}
            for i, item in enumerate(files):
                if isinstance(item, tuple):
                    filename, fp = item
                    file_data[f"file{i}"] = (filename, fp)
                else:
                    file_data[f"file{i}"] = item
            
            return self.post(
                f"/channels/{channel_id}/messages",
                json=payload,
                files=file_data
            )

        return self.post(f"/channels/{channel_id}/messages", json=payload)

    def reply(self, channel_id: int, message_id: int, content: str, **kwargs):
        return self.send_message(
            channel_id,
            content,
            message_reference={"message_id": str(message_id)},
            **kwargs,
        )

    def get_messages(
        self, channel_id: int, limit: int = 50, before: str = None, after: str = None
    ):
        params = {"limit": limit}
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return self.get(f"/channels/{channel_id}/messages", params=params)

    def edit_message(self, channel_id: int, message_id: int, content: str):
        return self.patch(
            f"/channels/{channel_id}/messages/{message_id}", json={"content": content}
        )

    def delete_message(self, channel_id: int, message_id: int):
        return self.delete(f"/channels/{channel_id}/messages/{message_id}")

    def add_reaction(self, channel_id: int, message_id: int, emoji: str):
        from urllib.parse import quote

        emoji = quote(emoji)
        return self.put(
            f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"
        )

    def remove_reaction(self, channel_id: int, message_id: int, emoji: str):
        from urllib.parse import quote

        emoji = quote(emoji)
        return self.delete(
            f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"
        )

    def get_gateway(self):
        return self.get("/gateway")

    def get_bot_gateway(self):
        return self.get("/gateway/bot")

    def edit_profile(self, payload: dict):
        return self.patch("/users/@me", json=payload)

    def edit_settings(self, payload: dict):
        return self.patch("/users/@me/settings", json=payload)

    def get_relationships(self):
        return self.get("/users/@me/relationships")

    def add_relationship(self, user_id: int, type: int = None):
        payload = {}
        if type is not None:
            payload["type"] = type
        return self.put(f"/users/@me/relationships/{user_id}", json=payload)

    def remove_relationship(self, user_id: int):
        return self.delete(f"/users/@me/relationships/{user_id}")

    def leave_guild(self, guild_id: int):
        """Leaves a guild."""
        return self.delete(f"/users/@me/guilds/{guild_id}")
