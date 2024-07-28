from nonebot.params import ArgPlainText
from nonebot_plugin_alconna.uniseg import UniMessage

from nonebot_plugin_sparkapi.config import conf

from .base import SessionID, cmd_session, fl_group_at, get_sessions_list, session_select

command = conf.sparkapi_commands["session_show"]

matcher_session_show = cmd_session.command(command)


@matcher_session_show.handle()
async def _(session_id: SessionID):
    session_list = get_sessions_list(session_id)
    msg = f"{session_list}\n\n输入序号显示会话内容，回复其他内容取消显示"
    await UniMessage(msg).send(at_sender=fl_group_at)


@matcher_session_show.got("index")
async def _(session_id: SessionID, index=ArgPlainText()):
    if not index.isdigit():
        await UniMessage("已取消显示").finish(at_sender=fl_group_at)

    session_list = get_sessions_list(session_id)
    idx = int(index)
    if idx not in range(len(session_list)) or idx == 0:
        await matcher_session_show.reject(
            "序号不合法，请重新输入",
            at_sender=fl_group_at,
        )

    session = session_select(session_id, index=idx)
    msg = f"{session.get_info()}"
    await UniMessage(msg).finish(at_sender=fl_group_at)
