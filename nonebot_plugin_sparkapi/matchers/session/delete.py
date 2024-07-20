from nonebot.params import ArgPlainText
from nonebot.typing import T_State
from nonebot_plugin_alconna.uniseg import UniMessage

from nonebot_plugin_sparkapi.config import conf

from .base import (
    SessionID,
    cmd_session,
    fl_group_at,
    get_sessions_list,
    session_delete,
    session_select,
)

command = conf.sparkapi_commands["session_delete"]

matcher_session_delete = cmd_session.command(command)


@matcher_session_delete.handle()
async def _(session_id: SessionID):
    session_list = get_sessions_list(session_id)
    msg = f"{session_list}\n\n输入序号选择会话，回复其他内容取消删除"
    await UniMessage(msg).send(at_sender=fl_group_at)


@matcher_session_delete.got("index")
async def _(session_id: SessionID, state: T_State, index=ArgPlainText()):
    if not index.isdigit():
        await UniMessage("已取消删除").finish(at_sender=fl_group_at)
    session_list = get_sessions_list(session_id)
    idx = int(index)
    if idx not in range(len(session_list)) or idx == 0:
        await matcher_session_delete.reject(
            "序号不合法，请重新输入",
            at_sender=fl_group_at,
        )
    session = session_select(session_id, index=idx)
    msg = f"{session.get_info()}\n\n确认删除该会话？\n回复“确认”确认删除，回复其他内容取消删除"
    await UniMessage(msg).send(at_sender=fl_group_at)
    state["index"] = idx


@matcher_session_delete.got("check")
async def _(session_id: SessionID, state: T_State, check=ArgPlainText()):
    if check != "确认":
        await UniMessage("已取消删除").finish(at_sender=fl_group_at)
    index = state["index"]

    try:
        session_delete(session_id, index=index)
    except Exception as e:
        msg = f"删除失败！请联系开发者。\n错误信息：{type(e)}: {e}"
    else:
        msg = "会话删除成功！"

    await UniMessage(msg).finish(at_sender=fl_group_at)
