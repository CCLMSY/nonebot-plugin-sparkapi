# 事件响应器：清空对话
from nonebot.adapters.onebot.v11 import MessageEvent as ME, PrivateMessageEvent as PME # type: ignore
from nonebot.adapters.onebot.v11 import Message, MessageSegment as MS # type: ignore

from nonebot.rule import to_me
from nonebot.plugin.on import on_message
from nonebot.params import CommandArg

from ... import funcs, storage, info
from ..data import presets, sessions, spname
from ...API.SparkApi import request

from nonebot import get_plugin_config
from ...config import Config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["session_clear"]
priority = conf.sparkapi_priority + 1

rule_session_clear = to_me() & funcs.trans_command(command)
matcher_session_clear = on_message(
    rule = rule_session_clear,
    priority=priority,
    block=True
)

@matcher_session_clear.handle()
async def session_clear_handle_function(event: ME):
    session_id = funcs.get_session_id(event)

    if session_id in sessions:
        del sessions[session_id]
        del spname[session_id]
        await matcher_session_clear.finish(MS.text("对话已清空"))
    else:
        await matcher_session_clear.finish(MS.text("当前无对话记录"))

