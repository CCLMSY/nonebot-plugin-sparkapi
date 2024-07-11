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

from ...config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["preset_show"]

matcher_preset_show=cmd_preset.command(command)
@matcher_preset_show.handle()
async def _(event:ME):
    session_id = get_session_id(event)
    preset_list = get_preset_list(session_id)
    msg = f"{preset_list}\n\n输入序号显示预设内容，回复其他内容取消显示"
    await matcher_preset_show.send(MS.text(msg), at_sender=fl_group_at)

@matcher_preset_show.got("index")
async def _(event:ME, index=ArgPlainText()):
    if not index.isdigit():
        await matcher_preset_show.finish(MS.text("已取消显示"), at_sender=fl_group_at)
    session_id = get_session_id(event)
    preset_list = get_preset_list(session_id)
    idx = int(index)
    if idx not in range(len(preset_list)):
        await matcher_preset_show.reject(MS.text("序号不合法，请重新输入"), at_sender=fl_group_at)
    if idx == 0:
        await matcher_preset_show.finish(MS.text("不允许查看默认预设"), at_sender=fl_group_at)
    try:
        ps = preset_select(session_id, index=idx)
    except Exception as e:
        await matcher_preset_show.finish(MS.text(f"查看失败！请联系开发者。\n错误信息：{type(e)}:{e}"), at_sender=fl_group_at)
    await matcher_preset_show.finish(MS.text(f"{ps.get_info()}"), at_sender=fl_group_at)