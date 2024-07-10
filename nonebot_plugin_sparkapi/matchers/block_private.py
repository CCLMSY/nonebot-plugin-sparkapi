from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.rule import is_type
from nonebot.plugin.on import on_message

from nonebot import get_plugin_config
from nonebot_plugin_sparkapi.config import Config
conf = get_plugin_config(Config)
fl_private_chat = conf.sparkapi_fl_private_chat
priority = conf.sparkapi_priority

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
    await matcher_blockprivate.finish(MS.text("私聊功能已关闭！如有需要，请联系管理员。" ))