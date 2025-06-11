from ..session import UserSession
from ..utils import catch_exc
from .alc import matcher


@matcher.assign("~clear")
async def assign_clear(user_session: UserSession) -> None:
    async with catch_exc("清空对话失败"):
        user_session.clear_current()
    await matcher.finish("清空对话成功！")
