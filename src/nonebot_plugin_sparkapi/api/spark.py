import base64
import hashlib
import hmac
import json
import ssl
from datetime import datetime
from typing import Any
from wsgiref.handlers import format_date_time

import websockets
from nonebot.compat import model_dump
from yarl import URL

from ..config import conf
from ..session import SessionContent, UserSessionData
from ..utils import get_model_info

model_info = get_model_info(conf.version)
if model_info.version == "v1.5":
    conf.maxlength = min(4000, conf.maxlength)


def b64_sha256(key: str, msg: str) -> str:
    return base64.b64encode(
        hmac.new(
            key.encode("utf-8"),
            msg.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
    ).decode(encoding="utf-8")


def create_url() -> str:
    spark_url = URL(model_info.url)
    assert spark_url.host is not None

    # 生成RFC1123格式的时间戳
    date = format_date_time(datetime.now().timestamp())

    # 拼接字符串
    signature_origin = (
        f"host: {spark_url.host}\ndate: {date}\nGET {spark_url.path} HTTP/1.1"
    )

    # 使用hmac-sha256进行加密
    signature = b64_sha256(conf.api_secret.get_secret_value(), signature_origin)
    auth_origin = (
        f'api_key="{conf.api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    auth = base64.b64encode(auth_origin.encode("utf-8")).decode("utf-8")

    # 组合鉴权参数生成url
    return str(
        spark_url.with_query(
            authorization=auth,
            date=date,
            host=spark_url.host,
        )
    )


def construct_params(content: list[SessionContent]) -> dict[str, Any]:
    return {
        "header": {"app_id": conf.app_id, "uid": "nonebot_plugin_sparkapi"},
        "parameter": {
            "chat": {
                "domain": model_info.domain,
                "temperature": conf.temperature,
                "max_tokens": conf.maxlength,
                "top_k": conf.top_k,
                "auditing": "default",
            }
        },
        "payload": {"message": {"text": [model_dump(i) for i in content]}},
    }


async def connect_ws(content: list[SessionContent]) -> str:
    ws_url = create_url()
    ssl_context = ssl._create_unverified_context()  # noqa: S323, SLF001
    answer = ""
    params = json.dumps(construct_params(content))

    async with websockets.connect(ws_url, ssl=ssl_context) as ws:
        await ws.send(params)
        async for message in ws:
            data = json.loads(message)
            code = data["header"]["code"]
            if code != 0:
                raise Exception(f"请求错误: {code=}, {data=}")

            choices = data["payload"]["choices"]
            answer += choices["text"][0]["content"]

            if choices["status"] == 2:
                break

    return answer


async def request_chat(session_id: str, question: str) -> str:
    session = UserSessionData.load(session_id)
    session.add_msg("user", question)
    res = await connect_ws(session.current.content)
    session.add_msg("assistant", res)
    return res
