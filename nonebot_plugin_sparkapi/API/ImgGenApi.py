from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from urllib.parse import urlencode, urlparse

import hmac
import hashlib
import base64
import httpx
import asyncio

res = ""

class Hs_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, IG_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(IG_url).netloc
        self.path = urlparse(IG_url).path
        self.IG_url = IG_url
        self.sid = ""
    
    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "POST " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.IG_url + '?' + urlencode(v)

        # print("APPID: " + self.APPID)
        # print("APIKey: " + self.APIKey)
        # print("APISecret: " + self.APISecret)
        # print("signature_origin: " + signature_origin)
        # print(url)
        return url

def gen_params(appid, domain, content):
    data = {
        "header": {
            "app_id": appid,
            "uid": "1234"
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "width": 1280,
                "height": 720
            }
        },
        "payload": {
            "message": {
                "text": [
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            }
        }
    }
    return data

def parse_response(data):
    code = data['header']['code']
    if code != 0:
        err = f'请求错误: {code}, {data}'
        print(err)
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        global res
        res += content
        if status == 2:
            print("Image Generation: OK!")

async def connect_hs(appid, api_key, api_secret, IG_url, domain, content):
    hs_param = Hs_Param(appid, api_key, api_secret, IG_url)
    url = hs_param.create_url()
    params = gen_params(appid, domain, content)
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("Image Generation: Got Request, Generating...")
        st = asyncio.get_event_loop().time()
        response = await client.post(url, json=params, headers={'content-type': "application/json"})
        ed = asyncio.get_event_loop().time()
        parse_response(response.json())
        print(f"Time Consumed: {ed-st:.2f}s")
    return res

async def main(appid, api_key, api_secret, IG_url, domain, content):
    await connect_hs(appid, api_key, api_secret, IG_url, domain, content)
    return res

# ---------------------- Test ----------------------
# import base64
# from PIL import Image
# from io import BytesIO
# from pathlib import Path

# def save_base64img(base64_data, filename):
#     img_data = base64.b64decode(base64_data) # base64解码
#     img = Image.open(BytesIO(img_data)) # 读取图片
#     img.save(filename) # 保存图片

# if __name__ == "__main__":
#     IG_url = "https://spark-api.cn-huabei-1.xf-yun.com/v2.1/tti"
#     domain = "general"
#     content = input("")
#     # asyncio.run(main("your_appid", "your_api_key", "your_api_secret", "https://your_ig_url", "your_domain", "your_content"))
#     save_base64img(res, "test.jpg")


# ---------------------------API Request---------------------------
IG_url = "http://spark-api.cn-huabei-1.xf-yun.com/v2.1/tti"
IG_domain = "general"

from ..config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)

appid = conf.sparkapi_app_id
api_secret = conf.sparkapi_api_secret
api_key = conf.sparkapi_api_key

async def request_IG(content):
    global res
    res = ""
    await main(appid,api_key,api_secret,IG_url,IG_domain,content)
    return res