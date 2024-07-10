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

from nonebot_plugin_sparkapi import funcs
from nonebot_plugin_sparkapi.config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
top_k = conf.sparkapi_model_top_k
temperature = conf.sparkapi_model_temperature
maxlength = conf.sparkpai_model_maxlength

app_id = conf.sparkapi_app_id
api_key = conf.sparkapi_api_key
api_secret = conf.sparkapi_api_secret

model_version = funcs.unify_model_version(conf.sparkapi_model_version)
Spark_url = funcs.get_Spark_url(model_version)
domain = funcs.get_domain(model_version)

answer = dict()

class Ws_Param(object):
    # 初始化
    def __init__(self, Spark_url):
        self.APPID = app_id
        self.APIKey = api_key
        self.APISecret = api_secret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url
        self.session_id = ""

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

        # 确认参数
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
        err = f'请求错误: Code:{code}, Data:{data}'
        await ws.close()
        raise Exception(err)
    else:
        session_id = ws.session_id # type:ignore
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        global answer
        answer[session_id] += content
        # print('get_res:',content)
        if status == 2:
            await ws.close()

async def connect_ws(url, domain, content, session_id):
    wsParam = Ws_Param(url)
    ws_url = wsParam.create_url()

    ssl_context = ssl._create_unverified_context()
    async with websockets.connect(ws_url,ssl=ssl_context) as ws:
        ws.appid = app_id # type:ignore
        ws.domain = domain # type:ignore
        ws.content = content # type:ignore
        ws.session_id = session_id # type:ignore
        params = json.dumps(gen_params(domain, content))
        # print(params)
        await ws.send(params)
        async for message in ws:
            await on_message(ws, message)

def gen_params(domain, content):
    data = {
        "header": {
            "app_id": app_id,
            "uid": "CCLMSY"
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": temperature,
                "max_tokens": maxlength ,
                "top_k": top_k,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": content
            }
        }
    }
    return data

# ---------------------------API Request---------------------------
from nonebot_plugin_sparkapi.matchers.session.base import(
    session_select,
    add_msg
)

async def request_chat(session_id, question):
    global answer
    answer[session_id] = ""
    add_msg(session_id,"user",question)
    current = session_select(session_id)
    content = current.content
    await connect_ws(Spark_url, domain, content, session_id)
    res = answer[session_id]
    add_msg(session_id,"assistant",res)
    return res