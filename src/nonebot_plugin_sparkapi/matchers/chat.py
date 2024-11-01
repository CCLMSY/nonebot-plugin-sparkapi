import contextlib
from typing import Annotated
from nonebot.adapters import Message
from nonebot.exception import ActionFailed
from nonebot.params import CommandArg, EventMessage
from nonebot.plugin.on import on_message
from nonebot.rule import command, to_me

from nonebot_plugin_sparkapi.API.SparkApi import request_chat
from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import SessionID, solve_at

command_chat = conf.sparkapi_command_chat
priority = conf.sparkapi_priority + 2
max_length = conf.sparkpai_model_maxlength
fl_notice = conf.sparkapi_fl_notice

rule = (to_me() & command(command_chat)) if command_chat else to_me()
matcher_chat = on_message(rule=rule, priority=priority, block=True)
Arg = Annotated[Message, CommandArg() if command_chat else EventMessage()]


@matcher_chat.handle()
async def _(session_id: SessionID, arg: Arg):
    question = arg.extract_plain_text().strip()
    if not question:
        await solve_at("内容不能为空！").finish()

    receipt = await solve_at("正在思考中...").send() if fl_notice else None

    try:
        answer = await request_chat(session_id, question)
    except Exception as e:
        answer = f"对话请求失败！请联系开发者。\n错误信息：{type(e)}: {e}"

    if receipt is not None and receipt.recallable:
        with contextlib.suppress(ActionFailed):
            await receipt.recall()
    await solve_at(answer).finish()
