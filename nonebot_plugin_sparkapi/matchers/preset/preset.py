from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from .base import(
    cmd_preset,
    get_session_id,
    get_preset_list,
    get_preset_commands,
    fl_group_at
)

matcher_preset = cmd_preset.command(tuple())
@matcher_preset.handle()
async def _(event:ME):
    session_id = get_session_id(event)
    preset_list = get_preset_list(session_id)
    preset_commands = get_preset_commands()
    msg = preset_list + "\n\n" + preset_commands
    await matcher_preset.finish(MS.text(msg), at_sender=fl_group_at)