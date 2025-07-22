from nonebot_plugin_alconna import UniMessage

from ..api.image import request_image_generate
from ..utils import ParamOrPrompt, catch_exc
from .alc import matcher


@matcher.assign("~image")
async def assign_image(
    content: str = ParamOrPrompt(
        param="content",
        prompt_msg="请输入生成图片内容，回复“取消”取消生成",
        cancel_msg="已取消生成图片",
    ),
) -> None:
    receipt = await UniMessage.text(
        "已收到请求，正在生成中...\n过程大约需要30s，请耐心等待"
    ).send()

    async with catch_exc("图片生成失败", receipt):
        img = await request_image_generate(content)
    await UniMessage.image(raw=img).finish()
