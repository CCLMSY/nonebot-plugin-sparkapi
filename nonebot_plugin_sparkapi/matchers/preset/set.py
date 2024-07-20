from nonebot.params import ArgPlainText
from nonebot_plugin_alconna.uniseg import UniMessage

from nonebot_plugin_sparkapi.config import conf

from .base import SessionID, cmd_preset, fl_group_at, get_preset_list, preset_select

command = conf.sparkapi_commands["preset_set"]

matcher_preset_set = cmd_preset.command(command)


@matcher_preset_set.handle()
async def _(session_id: SessionID):
    preset_list = get_preset_list(session_id)
    msg = f"{preset_list}\n\n输入序号选择预设，回复其他内容取消设置\n⚠设置预设将清除当前对话记录"
    await UniMessage(msg).send(at_sender=fl_group_at)


@matcher_preset_set.got("index")
async def _(session_id: SessionID, index: str = ArgPlainText()):
    from ..session.base import set_prompt

    if not index.isdigit():
        await UniMessage("已取消设置").finish(at_sender=fl_group_at)

    preset_list = get_preset_list(session_id)
    idx = int(index)
    if idx not in range(len(preset_list)):
        await matcher_preset_set.reject("序号不合法，请重新输入", at_sender=fl_group_at)

    try:
        ps = preset_select(session_id, index=idx)
        set_prompt(session_id, ps)
    except Exception as e:
        msg = f"设置失败！请联系开发者。\n错误信息：{type(e)}: {e}"
    else:
        msg = "预设设置成功！"

    await UniMessage(msg).finish(at_sender=fl_group_at)
