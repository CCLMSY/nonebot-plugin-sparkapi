from nonebot.params import ArgPlainText
from nonebot_plugin_alconna.uniseg import UniMessage

from nonebot_plugin_sparkapi.config import conf

from .base import SessionID, cmd_preset, fl_group_at, get_preset_list, preset_select

command = conf.sparkapi_commands["preset_show"]

matcher_preset_show = cmd_preset.command(command)


@matcher_preset_show.handle()
async def _(session_id: SessionID):
    preset_list = get_preset_list(session_id)
    msg = f"{preset_list}\n\n输入序号显示预设内容，回复其他内容取消显示"
    await UniMessage(msg).send(at_sender=fl_group_at)


@matcher_preset_show.got("index")
async def _(session_id: SessionID, index: str = ArgPlainText()):
    if not index.isdigit():
        await UniMessage("已取消显示").finish(at_sender=fl_group_at)
    preset_list = get_preset_list(session_id)
    idx = int(index)

    if idx not in range(len(preset_list)):
        await matcher_preset_show.reject(
            "序号不合法，请重新输入",
            at_sender=fl_group_at,
        )
    if idx == 0:
        await UniMessage("不允许查看默认预设").finish(at_sender=fl_group_at)

    try:
        ps = preset_select(session_id, index=idx)
    except Exception as e:
        msg = f"查看失败！请联系开发者。\n错误信息：{type(e)}: {e}"
    else:
        msg = ps.get_info()

    await UniMessage(msg).finish(at_sender=fl_group_at)
