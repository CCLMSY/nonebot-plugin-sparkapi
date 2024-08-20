from nonebot.params import ArgPlainText
from nonebot.typing import T_State

from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import solve_at

from .base import SessionID, cmd_preset, get_preset_list, preset_delete, preset_select

command = conf.sparkapi_commands["preset_delete"]

matcher_preset_delete = cmd_preset.command(command)


@matcher_preset_delete.handle()
async def _(session_id: SessionID):
    preset_list = get_preset_list(session_id)
    msg = f"{preset_list}\n\n输入序号选择预设，回复其他内容取消删除"
    await solve_at(msg).send()


@matcher_preset_delete.got("index")
async def _(
    session_id: SessionID,
    state: T_State,
    index: str = ArgPlainText(),
):
    if not index.isdigit():
        await solve_at("已取消删除").finish()
    preset_list = get_preset_list(session_id)
    idx = int(index)
    if idx < 0 or idx >= len(preset_list):
        msg = await solve_at("序号不合法，请重新输入").export()
        await matcher_preset_delete.reject(msg)
    if idx == 0:
        await solve_at("不允许删除默认预设").finish()
    preset = preset_select(session_id, index=idx)
    msg = f"{preset.get_info()}\n\n确认删除该预设？\n回复“确认”确认删除，回复其他内容取消删除"
    await solve_at(msg).send()
    state["index"] = idx


@matcher_preset_delete.got("check")
async def _(session_id: SessionID, state: T_State, check: str = ArgPlainText()):
    if check != "确认":
        await solve_at("已取消删除").finish()

    try:
        preset_delete(session_id, index=state["index"])
    except Exception as e:
        await solve_at(f"删除失败！请联系开发者。\n错误信息：{type(e)}: {e}").finish()

    await solve_at("预设删除成功！").finish()
