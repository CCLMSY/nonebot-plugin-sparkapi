from nonebot_plugin_sparkapi.funcs import solve_at

from .base import SessionID, cmd_preset, get_preset_commands, get_preset_list

matcher_preset = cmd_preset.command(tuple())


@matcher_preset.handle()
async def _(session_id: SessionID):
    preset_list = get_preset_list(session_id)
    preset_commands = get_preset_commands()
    msg = f"{preset_list}\n\n{preset_commands}"
    await solve_at(msg).finish()
