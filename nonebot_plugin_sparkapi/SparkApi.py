#type: ignore
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from urllib.parse import urlparse, urlencode

import hmac
import hashlib
import base64
import json
import websockets
import ssl

from .config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
model_top_k = conf.sparkapi_model_top_k
model_temperature = conf.sparkapi_model_temperature
maxlength = conf.sparkpai_model_maxlength

answer = ""

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc 
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url
        self.sid = ""

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

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
        url = self.Spark_url + '?' + urlencode(v)

        # print("APPID: " + self.APPID)
        # print("APIKey: " + self.APIKey)
        # print("APISecret: " + self.APISecret)
        # print("signature_origin: " + signature_origin)
        # print(url)
        return url

# 收到websockets消息的处理
async def on_message(ws, message):
    # print(message)
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        err = f'请求错误: {code}, {data}'
        print(err)
        await ws.close()
    else:
        # global sid
        # sid = data["header"]["sid"]
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        # print(content,end ="")
        global answer
        answer += content
        # print(1)
        if status == 2:
            await ws.close()

async def connect_ws(appid, api_key, api_secret, Spark_url, domain, question, sid):
    wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
    ws_url = wsParam.create_url()

    ssl_context = ssl.create_default_context()
    async with websockets.connect(ws_url,ssl=ssl_context) as ws:
        ws.appid = appid
        ws.question = question
        ws.domain = domain
        ws.sid = sid
        await ws.send(json.dumps(gen_params(appid, domain, question)))
        async for message in ws:
            await on_message(ws, message)

def gen_params(appid, domain, question):
    data = {
        "header": {
            "app_id": appid,
            "uid": "1234"
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": model_temperature,
                "max_tokens": maxlength // 2,
                "top_k": model_top_k,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }
    return data

async def main(appid, api_key, api_secret, Spark_url, domain, question, sid):
    await connect_ws(appid, api_key, api_secret, Spark_url, domain, question, sid)
    