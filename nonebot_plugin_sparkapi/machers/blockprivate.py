# 事件响应器：私聊阻断
from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PME # type: ignore
from nonebot.adapters.onebot.v11 import MessageSegment as MS # type: ignore

from nonebot.rule import is_type
from nonebot.plugin.on import on_message

from nonebot import get_plugin_config
from ..config import Config
conf = get_plugin_config(Config)
fl_private_chat = conf.sparkapi_fl_private_chat
priority = conf.sparkapi_priority
message = conf.sparkapi_message_blockprivate

async def fl_blockprivate() -> bool:
    return not fl_private_chat
rule = is_type(PME) & fl_blockprivate
matcher_blockprivate = on_message(
    rule = rule,
    priority = priority,
    block = True
)

@matcher_blockprivate.handle()
async def blockprivate_handle_function():
    await matcher_blockprivate.finish(MS.text(message))