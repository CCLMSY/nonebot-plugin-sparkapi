from nonebot_plugin_alconna import UniMessage

from ..api.ppt import request_ppt
from ..utils import ParamOrPrompt, catch_exc
from .alc import matcher


@matcher.assign("~ppt")
async def assign_ppt(
    content: str = ParamOrPrompt(
        param="content",
        prompt_msg="请输入生成PPT内容，回复“取消”取消生成",
        cancel_msg="已取消生成PPT",
    ),
) -> None:
    receipt = await UniMessage.text(
        "已收到请求，正在生成中...\n过程大约需要60s，请耐心等待"
    ).send()

    async with catch_exc("PPT生成失败", receipt):
        ppt = await request_ppt(content)
    await matcher.finish(f"生成成功！\n复制链接前往浏览器下载：\n{ppt}")
