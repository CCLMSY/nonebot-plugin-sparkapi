from nonebot_plugin_sparkapi.funcs import solve_at

from .base import SessionID, cmd_session, get_session_commands, get_sessions_list

matcher_session = cmd_session.command(tuple())


@matcher_session.handle()
async def _(session_id: SessionID):
    session_list = get_sessions_list(session_id)
    session_commands = get_session_commands()
    msg = session_list + "\n\n" + session_commands
    await solve_at(msg).finish()
