import contextlib

from nonebot import logger
from nonebot.exception import ActionFailed
from nonebot_plugin_alconna import UniMessage

from ..api.ppt import request_ppt
from ..utils import ParamOrPrompt
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

    try:
        ppt = await request_ppt(content)
    except Exception as e:
        msg = f"PPT生成失败！请联系开发者。\n错误信息：{type(e)}: {e}"
        logger.exception("PPT生成失败")
    else:
        msg = f"生成成功！\n复制链接前往浏览器下载：\n{ppt}"

    if receipt.recallable:
        with contextlib.suppress(ActionFailed):
            await receipt.recall()

    await UniMessage.text(msg).finish()
