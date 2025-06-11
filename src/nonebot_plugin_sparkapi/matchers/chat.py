from typing import Annotated

from nonebot.adapters import Message
from nonebot.params import CommandArg, EventMessage
from nonebot.plugin.on import on_message
from nonebot.rule import Rule, command, to_me
from nonebot_plugin_alconna import UniMessage

from ..api.spark import request_chat
from ..config import conf
from ..utils import SessionID, catch_exc

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
    if not (question := arg.extract_plain_text().strip()):
        await matcher.finish("内容不能为空！")
    receipt = conf.fl_notice and await UniMessage.text("正在思考中...").send()

    async with catch_exc("对话请求失败", receipt or None):
        answer = await request_chat(session_id, question)
    await matcher.finish(answer)
