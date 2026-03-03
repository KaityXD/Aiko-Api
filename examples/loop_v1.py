from aiko_api.http_curl import HTTP
import time

TOKEN = ""

CHANNEL_ID = 1269345574159908945
PROXY = None  # e.g., "http://user:pass@proxy:8080"

http = HTTP(token=TOKEN, proxy=PROXY)

print("Starting message loop...")
print(f"Will send messages to channel {CHANNEL_ID}")

while True:
    msg = http.send_message(CHANNEL_ID, f"spam")
    print(msg)
