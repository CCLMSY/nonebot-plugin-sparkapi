from nonebot.plugin.on import on_message
from nonebot_plugin_alconna.uniseg import MsgTarget

from nonebot_plugin_sparkapi.config import conf

if not conf.sparkapi_fl_private_chat:

    async def fl_blockprivate(target: MsgTarget) -> bool:
        return target.private

    matcher_blockprivate = on_message(
        rule=fl_blockprivate,
        priority=conf.sparkapi_priority,
    )

    @matcher_blockprivate.handle()
    async def _():
        await matcher_blockprivate.finish("私聊功能已关闭！如有需要，请联系管理员。")
