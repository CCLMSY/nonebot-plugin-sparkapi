from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.typing import T_State
from nonebot.params import ArgPlainText

from .base import(
    cmd_session,
    get_session_id,
    session_save,
    fl_group_at
)

from nonebot_plugin_sparkapi.config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["session_save"]

matcher_session_save = cmd_session.command(command)
@matcher_session_save.got("title",prompt="请为当前会话命名，回复“取消”取消保存")
async def _(state:T_State, title=ArgPlainText()):
    if title == "取消":
        await matcher_session_save.finish(MS.text("已取消保存"), at_sender=fl_group_at)
    else:
        state["title"] = title

@matcher_session_save.handle()
async def _(event:ME, state:T_State):
    title = state["title"]
    session_id = get_session_id(event)
    try:
        session_save(session_id, title)
    except Exception as e:
        await matcher_session_save.finish(MS.text(f"保存失败！请联系开发者。\n错误信息：{type(e)}:{e}"), at_sender=fl_group_at)
    await matcher_session_save.finish(MS.text(f"会话保存成功！"), at_sender=fl_group_at)