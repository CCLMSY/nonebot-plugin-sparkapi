from nonebot.plugin.on import on_message
from nonebot.rule import command, to_me
from nonebot_plugin_alconna.uniseg import UniMessage

from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import SessionID

from .session.base import clear_current

command_clear = conf.sparkapi_commands["clear"]
priority = conf.sparkapi_priority + 1
fl_group_at = conf.sparkapi_fl_group_at

rule = to_me() & command(command_clear)
matcher_clear = on_message(rule=rule, priority=priority, block=True)


@matcher_clear.handle()
async def _(session_id: SessionID):
    try:
        clear_current(session_id)
    except Exception as e:
        msg = f"清空对话失败！请联系开发者。\n错误信息：{type(e)}: {e}"
    else:
        msg = "清空对话成功！"

    await UniMessage(msg).finish(at_sender=fl_group_at)
