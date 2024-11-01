from nonebot.params import ArgPlainText
from nonebot.typing import T_State

from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import solve_at

from .base import SessionID, cmd_session, session_save

command = conf.sparkapi_commands["session_save"]

matcher_session_save = cmd_session.command(command)


@matcher_session_save.got("title", prompt="请为当前会话命名，回复“取消”取消保存")
async def _(state: T_State, title=ArgPlainText()):
    if title == "取消":
        await solve_at("已取消保存").finish()
    else:
        state["title"] = title


@matcher_session_save.handle()
async def _(session_id: SessionID, state: T_State):
    title = state["title"]
    try:
        session_save(session_id, title)
    except Exception as e:
        msg = f"保存失败！请联系开发者。\n错误信息：{type(e)}: {e}"
    else:
        msg = "会话保存成功！"

    await solve_at(msg).finish()
