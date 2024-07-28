from nonebot.params import ArgPlainText
from nonebot.typing import T_State
from nonebot_plugin_alconna.uniseg import UniMessage

from nonebot_plugin_sparkapi.config import conf

from .base import SessionID, cmd_preset, fl_group_at, preset_insert, preset_select

command = conf.sparkapi_commands["preset_create"]

matcher_preset_create = cmd_preset.command(command)


@matcher_preset_create.got("title", prompt="请输入预设名称，回复“取消”取消创建")
async def _(state: T_State, title: str = ArgPlainText()):
    if title == "取消":
        await UniMessage("已取消创建").finish(at_sender=fl_group_at)

    state["title"] = title


@matcher_preset_create.got("prompt", prompt="请输入预设提示词，回复“取消”取消创建")
async def _(state: T_State, prompt: str = ArgPlainText()):
    if prompt == "取消":
        await UniMessage("已取消创建").finish(at_sender=fl_group_at)

    state["prompt"] = prompt


@matcher_preset_create.handle()
async def _(session_id: SessionID, state: T_State):
    title = state["title"]
    prompt = state["prompt"]

    try:
        preset_insert(session_id, title, prompt)
    except Exception as e:
        msg = f"创建失败！请联系开发者。\n错误信息：{type(e)}: {e}"
        await UniMessage(msg).finish(at_sender=fl_group_at)

    new_preset = preset_select(session_id)
    msg = f"预设创建成功！\n{new_preset.get_info()}"
    await UniMessage(msg).finish(at_sender=fl_group_at)
