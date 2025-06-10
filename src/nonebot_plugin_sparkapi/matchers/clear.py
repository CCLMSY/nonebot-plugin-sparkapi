from nonebot import logger
from nonebot_plugin_alconna import UniMessage

from ..session import UserSession
from .alc import matcher


@matcher.assign("~clear")
async def assign_clear(user_session: UserSession) -> None:
    try:
        user_session.clear_current()
    except Exception as e:
        msg = f"清空对话失败！请联系开发者。\n错误信息：{type(e)}: {e}"
        logger.exception("清空对话失败")
    else:
        msg = "清空对话成功！"

    await UniMessage.text(msg).finish()
