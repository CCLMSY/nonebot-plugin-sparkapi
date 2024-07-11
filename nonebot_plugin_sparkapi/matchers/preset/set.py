from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.params import ArgPlainText

from .base import(
    cmd_preset,
    get_session_id,
    get_preset_list,
    preset_select,
    fl_group_at
)
from ..session.base import set_prompt

from ...config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["preset_set"]

matcher_preset_set=cmd_preset.command(command)
@matcher_preset_set.handle()
async def _(event:ME):
    session_id = get_session_id(event)
    preset_list = get_preset_list(session_id)
    msg = f"{preset_list}\n\n输入序号选择预设，回复其他内容取消设置\n⚠设置预设将清除当前对话记录"
    await matcher_preset_set.send(MS.text(msg), at_sender=fl_group_at)

@matcher_preset_set.got("index")
async def _(event:ME, index=ArgPlainText()):
    if not index.isdigit():
        await matcher_preset_set.finish(MS.text("已取消设置"), at_sender=fl_group_at)
    session_id = get_session_id(event)
    preset_list = get_preset_list(session_id)
    idx = int(index)
    if idx not in range(len(preset_list)):
        await matcher_preset_set.reject(MS.text("序号不合法，请重新输入"), at_sender=fl_group_at)
    try:
        ps = preset_select(session_id, index=idx)
        set_prompt(session_id, ps)
    except Exception as e:
        await matcher_preset_set.finish(MS.text(f"设置失败！请联系开发者。\n错误信息：{type(e)}:{e}"), at_sender=fl_group_at)
    await matcher_preset_set.finish(MS.text("预设设置成功！"), at_sender=fl_group_at)