from nonebot.params import ArgPlainText
from nonebot.typing import T_State
from nonebot_plugin_alconna.uniseg import UniMessage

from nonebot_plugin_sparkapi.config import conf

from .base import (
    SessionID,
    cmd_preset,
    fl_group_at,
    get_preset_list,
    preset_delete,
    preset_select,
)

command = conf.sparkapi_commands["preset_delete"]

matcher_preset_delete = cmd_preset.command(command)


@matcher_preset_delete.handle()
async def _(session_id: SessionID):
    preset_list = get_preset_list(session_id)
    msg = f"{preset_list}\n\n输入序号选择预设，回复其他内容取消删除"
    await UniMessage(msg).send(at_sender=fl_group_at)


@matcher_preset_delete.got("index")
async def _(session_id: SessionID, state: T_State, index: str = ArgPlainText()):
    if not index.isdigit():
        await UniMessage("已取消删除").finish(at_sender=fl_group_at)
    preset_list = get_preset_list(session_id)
    idx = int(index)
    if idx not in range(len(preset_list)):
        await matcher_preset_delete.reject(
            "序号不合法，请重新输入",
            at_sender=fl_group_at,
        )
    if idx == 0:
        await UniMessage("不允许删除默认预设").finish(at_sender=fl_group_at)
    preset = preset_select(session_id, index=idx)
    msg = f"{preset.get_info()}\n\n确认删除该预设？\n回复“确认”确认删除，回复其他内容取消删除"
    await UniMessage(msg).send(at_sender=fl_group_at)
    state["index"] = idx


@matcher_preset_delete.got("check")
async def _(session_id: SessionID, state: T_State, check: str = ArgPlainText()):
    if check != "确认":
        await UniMessage("已取消删除").finish(at_sender=fl_group_at)

    try:
        preset_delete(session_id, index=state["index"])
    except Exception as e:
        msg = f"删除失败！请联系开发者。\n错误信息：{type(e)}: {e}"
        await UniMessage(msg).finish(at_sender=fl_group_at)

    await UniMessage("预设删除成功！").finish(at_sender=fl_group_at)
