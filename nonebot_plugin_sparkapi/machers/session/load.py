# 事件响应器：加载对话记录
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
command = conf.sparkapi_commands["session_load"]
priority = conf.sparkapi_priority + 1

rule_session_load = to_me() & funcs.trans_command(command)
matcher_session_load = on_message(
    rule = rule_session_load,
    priority=priority,
    block=True
)

@matcher_session_load.handle()
async def session_load_handle_function(event: ME):
    session_id = funcs.get_session_id(event)
    session, pname = storage.f_session_load(session_id)

    if session:
        sessions[session_id] = session
        spname[session_id] = pname
        await matcher_session_load.finish(MS.text("已加载上次保存的对话记录！"))
    else:
        await matcher_session_load.finish(MS.text("未保存对话记录"))

