from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.params import ArgPlainText

from .base import(
    cmd_session,
    get_session_id,
    get_sessions_list,
    session_select,
    fl_group_at
)

from nonebot_plugin_sparkapi.config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["session_show"]

matcher_session_show = cmd_session.command(command)
@matcher_session_show.handle()
async def _(event:ME):
    session_id = get_session_id(event)
    session_list = get_sessions_list(session_id)
    msg = f"{session_list}\n\n输入序号显示会话内容，回复其他内容取消显示"
    await matcher_session_show.send(MS.text(msg), at_sender=fl_group_at)

@matcher_session_show.got("index")
async def _(event:ME, index=ArgPlainText()):
    if not index.isdigit():
        await matcher_session_show.finish(MS.text("已取消显示"), at_sender=fl_group_at)
    session_id = get_session_id(event)
    session_list = get_sessions_list(session_id)
    idx = int(index)
    if idx not in range(len(session_list)) or idx == 0:
        await matcher_session_show.reject(MS.text("序号不合法，请重新输入"), at_sender=fl_group_at)
    session = session_select(session_id, index=idx)
    msg = f"{session.get_info()}"
    await matcher_session_show.finish(MS.text(msg), at_sender=fl_group_at)