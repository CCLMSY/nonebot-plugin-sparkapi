from nonebot_plugin_alconna.uniseg import UniMessage

from .base import (
    SessionID,
    cmd_session,
    fl_group_at,
    get_session_commands,
    get_sessions_list,
)

matcher_session = cmd_session.command(tuple())


@matcher_session.handle()
async def _(session_id: SessionID):
    session_list = get_sessions_list(session_id)
    session_commands = get_session_commands()
    msg = session_list + "\n\n" + session_commands
    await UniMessage(msg).finish(at_sender=fl_group_at)
