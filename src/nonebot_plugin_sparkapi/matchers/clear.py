from nonebot.plugin.on import on_command
from nonebot.rule import to_me

from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import SessionID, solve_at

from .session.base import clear_current

matcher_clear = on_command(
    conf.sparkapi_commands["clear"],
    rule=to_me(),
    priority=conf.sparkapi_priority + 1,
    block=True,
)


@matcher_clear.handle()
async def _(session_id: SessionID):
    try:
        clear_current(session_id)
    except Exception as e:
        msg = f"清空对话失败！请联系开发者。\n错误信息：{type(e)}: {e}"
    else:
        msg = "清空对话成功！"

    await solve_at(msg).finish()
