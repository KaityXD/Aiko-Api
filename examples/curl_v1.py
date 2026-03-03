from aiko_api.http_curl import HTTP

TOKEN = ""
PROXY = None  # e.g., "http://user:pass@proxy:8080"

http = HTTP(token=TOKEN)
user = http.login()
print(f"Logged in as: {user['username']}#{user['discriminator']}")
channel_id = 1477219637899956305
while True:
    message = str(input("Your Message here: "))
    m = http.send_message(channel_id, message, files=["t.txt"])
    print(f"Sent message: {m['id']}")
