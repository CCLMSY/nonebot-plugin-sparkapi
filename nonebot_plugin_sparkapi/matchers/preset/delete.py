from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.typing import T_State
from nonebot.params import ArgPlainText

from .base import(
    cmd_preset,
    get_session_id,
    get_preset_list,
    preset_delete,
    preset_select,
    fl_group_at
)

from nonebot_plugin_sparkapi.config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["preset_delete"]

matcher_preset_delete = cmd_preset.command(command)
@matcher_preset_delete.handle()
async def _(event:ME):
    session_id = get_session_id(event)
    preset_list = get_preset_list(session_id)
    msg = f"{preset_list}\n\n输入序号选择预设，回复其他内容取消删除"
    await matcher_preset_delete.send(MS.text(msg), at_sender=fl_group_at)

@matcher_preset_delete.got("index")
async def _(event:ME, state:T_State, index=ArgPlainText()):
    if not index.isdigit():
        await matcher_preset_delete.finish(MS.text("已取消删除"), at_sender=fl_group_at)
    session_id = get_session_id(event)
    preset_list = get_preset_list(session_id)
    idx = int(index)
    if idx not in range(len(preset_list)):
        await matcher_preset_delete.reject(MS.text("序号不合法，请重新输入"), at_sender=fl_group_at)
    if idx == 0:
        await matcher_preset_delete.finish(MS.text("不允许删除默认预设"), at_sender=fl_group_at)
    preset = preset_select(session_id, index=idx)
    msg = f"{preset.get_info()}\n\n确认删除该预设？\n回复“确认”确认删除，回复其他内容取消删除"
    await matcher_preset_delete.send(MS.text(msg), at_sender=fl_group_at)
    state["index"] = idx

@matcher_preset_delete.got("check")
async def _(event:ME, state:T_State, check=ArgPlainText()):
    if check!="确认":
        await matcher_preset_delete.finish(MS.text("已取消删除"), at_sender=fl_group_at)
    session_id = get_session_id(event)
    index = state["index"]
    try:
        preset_delete(session_id, index=index)
    except Exception as e:
        await matcher_preset_delete.finish(MS.text(f"删除失败！请联系开发者。\n错误信息：{type(e)}:{e}"), at_sender=fl_group_at)
    await matcher_preset_delete.finish(MS.text("预设删除成功！"), at_sender=fl_group_at)