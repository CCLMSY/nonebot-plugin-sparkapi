import contextlib
from typing import Annotated

from nonebot import logger
from nonebot.adapters import Message
from nonebot.exception import ActionFailed
from nonebot.params import CommandArg, EventMessage
from nonebot.plugin.on import on_message
from nonebot.rule import Rule, command, to_me
from nonebot_plugin_alconna import UniMessage

from ..api.spark import request_chat
from ..config import conf
from ..utils import SessionID

matcher = on_message(
    rule=(
        Rule()
        & (to_me() if conf.require_at else None)
        & (command(conf.command_chat) if conf.command_chat else None)
    ),
    priority=conf.priority + 2,
    block=True,
)


@matcher.handle()
async def _(
    session_id: SessionID,
    arg: Annotated[Message, CommandArg() if conf.command_chat else EventMessage()],
):
    question = arg.extract_plain_text().strip()
    if not question:
        await UniMessage.text("内容不能为空！").finish()
    receipt = conf.fl_notice and await UniMessage.text("正在思考中...").send()

    try:
        answer = await request_chat(session_id, question)
    except Exception as e:
        answer = f"对话请求失败！请联系开发者。\n错误信息：{type(e)}: {e}"
        logger.exception("对话请求失败")

    if receipt and receipt.recallable:
        with contextlib.suppress(ActionFailed):
            await receipt.recall()
    await UniMessage.text(answer).finish()
