from nonebot.plugin.on import on_message
from nonebot.rule import Rule
from nonebot_plugin_alconna.uniseg import MsgTarget, UniMessage

from nonebot_plugin_sparkapi.config import conf

fl_private_chat = conf.sparkapi_fl_private_chat
priority = conf.sparkapi_priority


async def fl_blockprivate(target: MsgTarget) -> bool:
    return target.private and not fl_private_chat


rule = Rule(fl_blockprivate)
matcher_blockprivate = on_message(rule=rule, priority=priority, block=True)


@matcher_blockprivate.handle()
async def _():
    await UniMessage("私聊功能已关闭！如有需要，请联系管理员。").finish()
