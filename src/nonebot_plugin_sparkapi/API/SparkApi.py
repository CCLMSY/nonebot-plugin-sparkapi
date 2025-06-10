import base64
import hashlib
import hmac
import json
import ssl
from datetime import datetime
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time

import websockets

from nonebot_plugin_sparkapi import funcs
from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.matchers.session.base import add_msg, session_select

model_version = funcs.unify_model_version(conf.sparkapi_model_version)
Spark_url = funcs.get_Spark_url(model_version)
domain = funcs.get_domain(model_version)

top_k = conf.sparkapi_model_top_k
temperature = conf.sparkapi_model_temperature
maxlength = conf.sparkpai_model_maxlength
if model_version == "v1.5":
    maxlength = min(4000, maxlength)

app_id = conf.sparkapi_app_id
api_key = conf.sparkapi_api_key
api_secret = conf.sparkapi_api_secret


def b64_sha256(key: str, msg: str) -> str:
    return base64.b64encode(
        hmac.new(
            key.encode("utf-8"),
            msg.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
    ).decode(encoding="utf-8")


def create_url(spark_url: str):
    parsed = urlparse(spark_url)
    host = parsed.netloc
    path = parsed.path

    # 生成RFC1123格式的时间戳
    date = format_date_time(datetime.now().timestamp())

    # 拼接字符串
    signature_origin = f"host: {host}\n"
    signature_origin += f"date: {date}\n"
    signature_origin += f"GET {path} HTTP/1.1"

    # 使用hmac-sha256进行加密
    signature = b64_sha256(api_secret, signature_origin)
    auth_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    auth = base64.b64encode(auth_origin.encode("utf-8")).decode("utf-8")

    # 将请求的鉴权参数组合为字典
    v = {"authorization": auth, "date": date, "host": host}
    # 拼接鉴权参数，生成url
    url = spark_url + "?" + urlencode(v)

    return url


async def connect_ws(url: str, domain: str, content: list[dict[str, str]]) -> str:
    ws_url = create_url(url)
    ssl_context = ssl._create_unverified_context()
    answer = ""

    async with websockets.connect(ws_url, ssl=ssl_context) as ws:
        params = json.dumps(gen_params(domain, content))
        await ws.send(params)
        async for message in ws:
            data = json.loads(message)
            code = data["header"]["code"]
            if code != 0:
                await ws.close()
                raise Exception(f"请求错误: {code=}, {data=}")

            choices = data["payload"]["choices"]
            answer += choices["text"][0]["content"]

            if choices["status"] == 2:
                await ws.close()

    return answer


def gen_params(domain: str, content: list[dict[str, str]]):
    return {
        "header": {"app_id": app_id, "uid": "CCLMSY"},
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": temperature,
                "max_tokens": maxlength,
                "top_k": top_k,
                "auditing": "default",
            }
        },
        "payload": {"message": {"text": content}},
    }


# ---------------------------API Request---------------------------


async def request_chat(session_id: str, question: str):
    add_msg(session_id, "user", question)
    session = session_select(session_id)
    res = await connect_ws(Spark_url, domain, session.content)
    add_msg(session_id, "assistant", res)
    return res
