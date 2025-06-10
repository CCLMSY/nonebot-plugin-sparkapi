import base64
import hashlib
import hmac
import time
from typing import Any

import httpx
from nonebot.log import logger

from ..config import conf


def _md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()  # noqa: S324


class AIPPT:
    def __init__(self, text: str) -> None:
        self.text = text
        self.headers = self.sign_headers()

    def hmac_sha1_encrypt(self, encrypt_text: str, encrypt_key: str) -> str:
        return base64.b64encode(
            hmac.new(
                encrypt_key.encode("utf-8"),
                encrypt_text.encode("utf-8"),
                digestmod=hashlib.sha1,
            ).digest()
        ).decode("utf-8")

    def sign_headers(self) -> dict[str, str]:
        timestamp = str(int(time.time()))
        try:
            auth = _md5(conf.app_id + timestamp)
            signature = self.hmac_sha1_encrypt(auth, conf.api_secret)
        except Exception as e:
            logger.debug(f"AIPPT 签名获取失败: {e}")
            raise ValueError("AIPPT 签名获取失败") from e
        return {
            "appId": conf.app_id,
            "timestamp": timestamp,
            "signature": signature,
            "Content-Type": "application/json; charset=utf-8",
        }

    async def create_task(self) -> int:
        url = "https://zwapi.xfyun.cn/api/aippt/create"
        body = {"query": self.text}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url,
                json=body,
                headers=self.headers,
            )

        resp: dict[str, Any] = response.json()
        if resp["code"] == 0:
            logger.success("创建PPT任务成功")
            return resp["data"]["sid"]

        logger.error("创建PPT任务失败")
        # TODO: 抛出特定的错误类型
        raise Exception("创建PPT任务失败")

    async def get_process(self, sid: int) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://zwapi.xfyun.cn/api/aippt/progress?sid={sid}",
                headers=self.headers,
            )
            logger.debug(f"AIPPT.get_process({sid=}): {response.text}")
            return response.json()

    async def get_result(self) -> str:
        task_id = await self.create_task()
        while True:
            resp = await self.get_process(task_id)
            if resp["data"]["process"] == 100:
                ppt_url = resp["data"]["pptUrl"]
                break
        return ppt_url


# ---------------------------API Request---------------------------


async def request_ppt(content: str) -> str:
    return await AIPPT(content).get_result()
