from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from urllib.parse import urlencode, urlparse

import hmac
import hashlib
import base64
import httpx
import asyncio

from ..config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
width = conf.sparkapi_IG_size[0]
height = conf.sparkapi_IG_size[1]

app_id = conf.sparkapi_app_id
api_key = conf.sparkapi_api_key
api_secret = conf.sparkapi_api_secret

IG_url = "https://spark-api.cn-huabei-1.xf-yun.com/v2.1/tti"
IG_domain = "general"
    
res = dict()

class Hs_Param(object):
    # 初始化
    def __init__(self):
        self.APPID = app_id
        self.APIKey = api_key
        self.APISecret = api_secret
        self.host = urlparse(IG_url).netloc
        self.path = urlparse(IG_url).path
        self.IG_url = IG_url
    
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

        # 确认参数
        # print("APPID: " + self.APPID)
        # print("APIKey: " + self.APIKey)
        # print("APISecret: " + self.APISecret)
        # print("signature_origin: " + signature_origin)
        # print(url)
        return url

def parse_response(data,session_id):
    code = data['header']['code']
    if code != 0:
        err = f'请求错误: {code}, {data}'
        print(err)
        return data['header']['message']
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        global res
        res[session_id] += content
        if status == 2:
            print("Image Generation: OK!")
    return ""

async def connect_hs(content, session_id):
    hs_param = Hs_Param()
    url = hs_param.create_url()

    params = gen_params(content)
    async with httpx.AsyncClient(timeout=None) as client:
        print("Image Generation: Got Request, Generating...")
        st = asyncio.get_event_loop().time()
        response = await client.post(url, json=params, headers={'content-type': "application/json"})
        ed = asyncio.get_event_loop().time()
        err_msg = parse_response(response.json(),session_id)
        print(f"Time Consumed: {ed-st:.2f}s")
    return err_msg

def gen_params(content):
    data = {
        "header": {
            "app_id": app_id,
            "uid": "CCLMSY"
        },
        "parameter": {
            "chat": {
                "domain": IG_domain,
                "width": width,
                "height": height
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
from pathlib import Path 
from PIL import Image
from io import BytesIO
import base64

PATH = Path(".") / "SparkApi"

def save_base64img(base64_data, session_id:str):
    user_path = PATH / session_id / "images"
    if not user_path.exists():
        user_path.mkdir(parents=True)
    img_data = base64.b64decode(base64_data) # base64解码
    img = Image.open(BytesIO(img_data)) # 读取图片
    filename = user_path / (get_time()+".png")
    print(filename)
    img.save(filename) # 保存图片
    return filename
def get_time():
    return datetime.now().strftime('%Y%m%d_%H%M%S')

async def request_IG(session_id, content):
    global res
    res[session_id] = ""
    err_msg = await connect_hs(content, session_id)
    if err_msg:
        return err_msg
    return save_base64img(res[session_id], session_id)