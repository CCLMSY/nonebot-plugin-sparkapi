from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from .base import(
    cmd_session,
    get_session_id,
    get_sessions_list,
    get_session_commands,
    fl_group_at
)

matcher_session = cmd_session.command(tuple())
@matcher_session.handle()
async def _(event:ME):
    session_id = get_session_id(event)
    session_list = get_sessions_list(session_id)
    session_commands = get_session_commands()
    msg = session_list + "\n\n" + session_commands
    await matcher_session.finish(MS.text(msg), at_sender=fl_group_at)