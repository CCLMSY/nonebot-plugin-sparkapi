import asyncio
import base64
import hashlib
import hmac
from datetime import datetime
from typing import TYPE_CHECKING, Any
from wsgiref.handlers import format_date_time

import httpx
from nonebot.log import logger
from yarl import URL

from ..config import conf

IG_url = URL("https://spark-api.cn-huabei-1.xf-yun.com/v2.1/tti")
IG_domain = "general"


def b64_sha256(key: str, msg: str) -> str:
    return base64.b64encode(
        hmac.new(
            key.encode("utf-8"),
            msg.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
    ).decode(encoding="utf-8")


def create_url() -> str:
    if TYPE_CHECKING:
        assert IG_url.host is not None

    # 生成RFC1123格式的时间戳
    date = format_date_time(datetime.now().timestamp())

    # 拼接字符串
    signature_origin = f"host: {IG_url.host}\n"
    signature_origin += f"date: {date}\n"
    signature_origin += f"POST {IG_url.path} HTTP/1.1"

    # 进行hmac-sha256进行加密
    signature = b64_sha256(conf.api_secret.get_secret_value(), signature_origin)
    auth_origin = (
        f'api_key="{conf.api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    auth = base64.b64encode(auth_origin.encode("utf-8")).decode("utf-8")

    # 拼接鉴权参数，生成url
    return str(
        IG_url.with_query(
            authorization=auth,
            date=date,
            host=IG_url.host,
        )
    )


def parse_response(data: dict[str, Any]) -> str:
    code: int = data["header"]["code"]
    if code != 0:
        logger.error(f"请求错误: {code=}, {data}")
        # TODO: 抛出特定的错误类型
        raise Exception(data["header"]["message"])

    choices = data["payload"]["choices"]
    status = choices["status"]
    content = choices["text"][0]["content"]
    if status == 2:
        logger.success("Image Generation: OK!")
    return content


def gen_params(content: str) -> dict[str, Any]:
    return {
        "header": {"app_id": conf.app_id, "uid": "nonebot_plugin_sparkapi"},
        "parameter": {
            "chat": {
                "domain": IG_domain,
                "width": conf.IG_size[0],
                "height": conf.IG_size[1],
            }
        },
        "payload": {"message": {"text": [{"role": "user", "content": content}]}},
    }


async def request_image_generate(content: str) -> bytes:
    url = create_url()
    params = gen_params(content)
    async with httpx.AsyncClient(timeout=None) as client:  # noqa: S113
        logger.info("Image Generation: Got Request, Generating...")
        st = asyncio.get_event_loop().time()
        response = await client.post(url, json=params)
        ed = asyncio.get_event_loop().time()
    logger.info(f"Time Consumed: {ed - st:.2f}s")
    result = parse_response(response.json())
    return base64.b64decode(result.encode())
