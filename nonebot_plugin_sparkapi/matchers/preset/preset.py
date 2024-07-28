from nonebot_plugin_alconna.uniseg import UniMessage

from .base import (
    SessionID,
    cmd_preset,
    fl_group_at,
    get_preset_commands,
    get_preset_list,
)

matcher_preset = cmd_preset.command(tuple())


@matcher_preset.handle()
async def _(session_id: SessionID):
    preset_list = get_preset_list(session_id)
    preset_commands = get_preset_commands()
    msg = f"{preset_list}\n\n{preset_commands}"
    await UniMessage(msg).finish(at_sender=fl_group_at)
