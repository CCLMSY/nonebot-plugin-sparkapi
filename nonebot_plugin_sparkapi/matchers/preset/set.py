from nonebot.adapters import Event
from nonebot.params import ArgPlainText

from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import solve_at

from .base import SessionID, cmd_preset, get_preset_list, preset_select

command = conf.sparkapi_commands["preset_set"]

matcher_preset_set = cmd_preset.command(command)


@matcher_preset_set.handle()
async def _(session_id: SessionID):
    preset_list = get_preset_list(session_id)
    msg = f"{preset_list}\n\n输入序号选择预设，回复其他内容取消设置\n⚠设置预设将清除当前对话记录"
    await solve_at(msg).send()


@matcher_preset_set.got("index")
async def _(event: Event, session_id: SessionID, index: str = ArgPlainText()):
    from ..session.base import set_prompt

    if not index.isdigit():
        await solve_at("已取消设置").finish()

    preset_list = get_preset_list(session_id)
    idx = int(index)
    if idx < 0 or idx >= len(preset_list):
        msg = await solve_at("序号不合法，请重新输入").export()
        await matcher_preset_set.reject(msg)

    try:
        ps = preset_select(session_id, index=idx)
        set_prompt(session_id, ps)
    except Exception as e:
        msg = f"设置失败！请联系开发者。\n错误信息：{type(e)}: {e}"
    else:
        msg = "预设设置成功！"

    await solve_at(msg).finish()
