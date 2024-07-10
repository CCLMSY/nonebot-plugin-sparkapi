from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.typing import T_State
from nonebot.params import ArgPlainText

from .base import(
    cmd_preset,
    get_session_id,
    preset_insert,
    preset_select,
    fl_group_at
)

from nonebot_plugin_sparkapi.config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["preset_create"]

matcher_preset_create = cmd_preset.command(command)
@matcher_preset_create.got("title",prompt="请输入预设名称，回复“取消”取消创建")
async def _(state:T_State, title=ArgPlainText()):
    if title == "取消":
        await matcher_preset_create.finish(MS.text("已取消创建"), at_sender=fl_group_at)
    else:
        state["title"] = title
        
@matcher_preset_create.got("prompt",prompt="请输入预设提示词，回复“取消”取消创建")
async def _(state:T_State, prompt=ArgPlainText()):
    if prompt == "取消":
        await matcher_preset_create.finish(MS.text("已取消创建"), at_sender=fl_group_at)
    else:
        state["prompt"] = prompt

@matcher_preset_create.handle()
async def _(event:ME, state:T_State):
    title = state["title"]
    prompt = state["prompt"]
    session_id = get_session_id(event)
    try:
        preset_insert(session_id, title, prompt)
    except Exception as e:
        await matcher_preset_create.finish(MS.text(f"创建失败！请联系开发者。\n错误信息：{type(e)}:{e}"), at_sender=fl_group_at)
    new_preset = preset_select(session_id)
    await matcher_preset_create.finish(MS.text(f"预设创建成功！\n{new_preset.get_info()}"), at_sender=fl_group_at)