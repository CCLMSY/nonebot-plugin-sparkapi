from nonebot.params import ArgPlainText

from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import solve_at

from .base import SessionID, cmd_session, get_sessions_list, session_select

command = conf.sparkapi_commands["session_show"]

matcher_session_show = cmd_session.command(command)


@matcher_session_show.handle()
async def _(session_id: SessionID):
    session_list = get_sessions_list(session_id)
    msg = f"{session_list}\n\n输入序号显示会话内容，回复其他内容取消显示"
    await solve_at(msg).send()


@matcher_session_show.got("index")
async def _(session_id: SessionID, index=ArgPlainText()):
    if not index.isdigit():
        await solve_at("已取消显示").finish()

    idx = int(index)
    session_list = get_sessions_list(session_id)
    if idx <= 0 or idx >= len(session_list):
        msg = await solve_at("序号不合法，请重新输入").export()
        await matcher_session_show.reject(msg)

    session = session_select(session_id, index=idx)
    await solve_at(session.get_info()).finish()
