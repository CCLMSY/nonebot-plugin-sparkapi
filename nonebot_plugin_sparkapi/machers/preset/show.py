# 事件响应器：显示人物预设
from nonebot.adapters.onebot.v11 import MessageEvent as ME, PrivateMessageEvent as PME # type: ignore
from nonebot.adapters.onebot.v11 import Message, MessageSegment as MS # type: ignore

from nonebot.rule import to_me
from nonebot.plugin.on import on_message
from nonebot.params import CommandArg
from nonebot.params import ArgPlainText

from ..data import presets, sessions, spname
from ... import funcs, storage, info

from nonebot import get_plugin_config
from ...config import Config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["preset_show"]
priority = conf.sparkapi_priority + 1

rule_preset_show = to_me() & funcs.trans_command(command)
matcher_preset_show = on_message(
    rule = rule_preset_show,
    priority = priority,
    block = True
)

@matcher_preset_show.handle()
async def preset_show_handle_function(event:ME):
    session_id = funcs.get_session_id(event)
    custom_presets = storage.f_preset_load(session_id)

    msg = info.get_preset_lst(info.presets_default,custom_presets)
    msg += f"\n当前预设为：{spname.get(session_id,'智能助手')}"
    await matcher_preset_show.finish(MS.text(msg))
