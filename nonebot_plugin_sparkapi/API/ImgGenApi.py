import asyncio
import base64
import hashlib
import hmac
from datetime import datetime
from time import mktime
from typing import Any
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time

import httpx
from nonebot.log import logger
from nonebot_plugin_alconna.uniseg.utils import fleep

from nonebot_plugin_sparkapi.config import DATA_PATH, conf

width, height = conf.sparkapi_IG_size
app_id = conf.sparkapi_app_id
api_key = conf.sparkapi_api_key
api_secret = conf.sparkapi_api_secret

IG_url = "https://spark-api.cn-huabei-1.xf-yun.com/v2.1/tti"
IG_domain = "general"
IG_host = urlparse(IG_url).netloc
IG_path = urlparse(IG_url).path


def b64_sha256(key: str, msg: str) -> str:
    return base64.b64encode(
        hmac.new(
            key.encode("utf-8"),
            msg.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
    ).decode(encoding="utf-8")


def create_url():
    # 生成RFC1123格式的时间戳
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))

    # 拼接字符串
    signature_origin = f"host: {IG_host}\n"
    signature_origin += f"date: {date}\n"
    signature_origin += f"POST {IG_path} HTTP/1.1"

    # 进行hmac-sha256进行加密
    signature = b64_sha256(api_secret, signature_origin)
    auth_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    auth = base64.b64encode(auth_origin.encode("utf-8")).decode("utf-8")

    # 将请求的鉴权参数组合为字典
    v = {"authorization": auth, "date": date, "host": IG_host}
    # 拼接鉴权参数，生成url
    url = f"{IG_url}?{urlencode(v)}"

    return url


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


async def connect_hs(content: str) -> str:
    url = create_url()

    params = gen_params(content)
    async with httpx.AsyncClient(timeout=None) as client:
        logger.info("Image Generation: Got Request, Generating...")
        st = asyncio.get_event_loop().time()
        response = await client.post(url, json=params)
        ed = asyncio.get_event_loop().time()
    logger.info(f"Time Consumed: {ed-st:.2f}s")
    return parse_response(response.json())


def gen_params(content: str) -> dict[str, Any]:
    return {
        "header": {"app_id": app_id, "uid": "CCLMSY"},
        "parameter": {"chat": {"domain": IG_domain, "width": width, "height": height}},
        "payload": {"message": {"text": [{"role": "user", "content": content}]}},
    }


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
import base64
from pathlib import Path


def save_base64img(base64_data: str, session_id: str) -> Path:
    user_path = DATA_PATH / session_id / "images"
    user_path.mkdir(parents=True, exist_ok=True)
    img_data = base64.b64decode(base64_data)  # base64解码
    ext = fleep.get(img_data).extensions[0]
    filepath = user_path / datetime.now().strftime(f"%Y%m%d_%H%M%S.{ext}")
    filepath.write_bytes(img_data)  # 保存图片
    logger.debug(f"Saved image: {filepath}")
    return filepath


async def request_IG(session_id: str, content: str):
    result = await connect_hs(content)
    return save_base64img(result, session_id)
