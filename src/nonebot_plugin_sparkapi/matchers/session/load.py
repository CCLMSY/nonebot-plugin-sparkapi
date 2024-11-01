from nonebot.params import ArgPlainText
from nonebot.typing import T_State

from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import solve_at

from .base import (
    SessionID,
    cmd_session,
    get_sessions_list,
    session_load,
    session_select,
)

command = conf.sparkapi_commands["session_load"]

matcher_session_load = cmd_session.command(command)


@matcher_session_load.handle()
async def _(session_id: SessionID):
    session_list = get_sessions_list(session_id)
    msg = f"{session_list}\n\n输入序号选择会话，回复其他内容取消加载"
    await solve_at(msg).send()


@matcher_session_load.got("index")
async def _(session_id: SessionID, state: T_State, index: str = ArgPlainText()):
    if not index.isdigit():
        await solve_at("已取消加载").finish()

    session_list = get_sessions_list(session_id)
    idx = int(index)

    if idx <= 0 or idx >= len(session_list):
        msg = await solve_at("序号不合法，请重新输入").export()
        await matcher_session_load.reject(msg)

    session = session_select(session_id, index=idx)
    msg = f"{session.get_info()}\n\n确认加载该会话？\n回复“确认”确认加载，回复其他内容取消加载"
    await solve_at(msg).send()
    state["index"] = idx


@matcher_session_load.got("check")
async def _(session_id: SessionID, state: T_State, check=ArgPlainText()):
    if check != "确认":
        await solve_at("已取消加载").finish()

    index = state["index"]
    try:
        session_load(session_id, index=index)
    except Exception as e:
        msg = f"加载失败！请联系开发者。\n错误信息：{type(e)}: {e}"
    else:
        msg = "会话加载成功！"

    await solve_at(msg).finish()
