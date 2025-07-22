from nonebot.plugin.on import on_message
from nonebot_plugin_alconna.uniseg import MsgTarget

from ..config import conf

if not conf.fl_private_chat:

    async def is_private(target: MsgTarget) -> bool:
        return target.private

    matcher = on_message(rule=is_private, priority=conf.priority, block=True)

    @matcher.handle()
    async def _():
        await matcher.finish("私聊功能已关闭！\n如有需要，请联系管理员。")
