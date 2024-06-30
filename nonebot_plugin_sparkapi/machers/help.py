# 事件响应器：显示帮助信息
from nonebot.adapters.onebot.v11 import MessageEvent as ME, PrivateMessageEvent as PME # type: ignore
from nonebot.adapters.onebot.v11 import Message, MessageSegment as MS # type: ignore

from nonebot.rule import to_me
from nonebot.plugin.on import on_message
from nonebot.params import CommandArg

from .. import funcs, storage, info

from nonebot import get_plugin_config
from ..config import Config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["help"]
priority = conf.sparkapi_priority + 1

rule = to_me() & funcs.trans_command(command)
matcher_help = on_message(
    rule = rule,
    priority = priority,
    block = True
)

@matcher_help.handle()
async def sparkhelp_handle_function():
    await matcher_help.finish(MS.text(info.help_info))