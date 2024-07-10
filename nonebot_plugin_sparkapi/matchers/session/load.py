from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.typing import T_State
from nonebot.params import ArgPlainText

from .base import(
    cmd_session,
    get_session_id,
    get_sessions_list,
    session_load,
    session_select,
    fl_group_at
)

from nonebot_plugin_sparkapi.config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["session_load"]

matcher_session_load = cmd_session.command(command)
@matcher_session_load.handle()
async def _(event:ME):
    session_id = get_session_id(event)
    session_list = get_sessions_list(session_id)
    msg = f"{session_list}\n\n输入序号选择会话，回复其他内容取消加载"
    await matcher_session_load.send(MS.text(msg), at_sender=fl_group_at)

@matcher_session_load.got("index")
async def _(event:ME, state:T_State, index=ArgPlainText()):
    if not index.isdigit():
        await matcher_session_load.finish(MS.text("已取消加载"), at_sender=fl_group_at)
    session_id = get_session_id(event)
    session_list = get_sessions_list(session_id)
    idx = int(index)
    if idx not in range(len(session_list)) or idx == 0:
        await matcher_session_load.reject(MS.text("序号不合法，请重新输入"), at_sender=fl_group_at)
    session = session_select(session_id, index=idx)
    msg = f"{session.get_info()}\n\n确认加载该会话？\n回复“确认”确认加载，回复其他内容取消加载"
    await matcher_session_load.send(MS.text(msg), at_sender=fl_group_at)
    state["index"] = idx

@matcher_session_load.got("check")
async def _(event:ME, state:T_State, check=ArgPlainText()):
    if check!="确认":
        await matcher_session_load.finish(MS.text("已取消加载"), at_sender=fl_group_at)
    session_id = get_session_id(event)
    index = state["index"]
    try:
        session_load(session_id, index=index)
    except Exception as e:
        await matcher_session_load.finish(MS.text(f"加载失败！请联系开发者。\n错误信息：{type(e)}:{e}"), at_sender=fl_group_at)
    await matcher_session_load.finish(MS.text("会话加载成功！"), at_sender=fl_group_at)