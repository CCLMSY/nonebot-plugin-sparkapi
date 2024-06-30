# 事件响应器：保存对话记录
from nonebot.adapters.onebot.v11 import MessageEvent as ME, PrivateMessageEvent as PME # type: ignore
from nonebot.adapters.onebot.v11 import Message, MessageSegment as MS # type: ignore

from nonebot.rule import to_me
from nonebot.plugin.on import on_message
from nonebot.params import CommandArg

from ..data import presets, sessions, spname
from ... import funcs, storage, info

from nonebot import get_plugin_config
from ...config import Config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["session_save"]
priority = conf.sparkapi_priority + 1

rule = to_me() & funcs.trans_command(command)
matcher_session_save = on_message(
    rule = rule,
    priority=priority,
    block=True
)

@matcher_session_save.handle()
async def session_save_handle_function(event: ME):
    session_id = funcs.get_session_id(event)

    if session_id in sessions:
        storage.f_session_save(sessions[session_id], spname[session_id], session_id)
        await matcher_session_save.finish(MS.text("当前对话记录已保存！"))
    else:
        await matcher_session_save.finish(MS.text("当前无对话记录"))