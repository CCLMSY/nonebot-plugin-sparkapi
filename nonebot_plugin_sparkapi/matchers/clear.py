from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.rule import to_me,command
from nonebot.plugin.on import on_message

from nonebot_plugin_sparkapi.matchers.session.base import clear_current
from nonebot_plugin_sparkapi.funcs import get_session_id

from nonebot_plugin_sparkapi.config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
command_clear = conf.sparkapi_commands["clear"]
priority = conf.sparkapi_priority+1
fl_group_at = conf.sparkapi_fl_group_at

rule = to_me() & command(command_clear)
matcher_clear = on_message(
    rule = rule,
    priority=priority,
    block=True
)

@matcher_clear.handle()
async def _(event:ME):
    session_id = get_session_id(event)
    try:
        clear_current(session_id)
    except Exception as e:
        await matcher_clear.finish(MS.text(f"清空对话失败！请联系开发者。\n错误信息：{type(e)}:{e}"), at_sender=fl_group_at)
    else:
        await matcher_clear.finish(MS.text("清空对话成功！"), at_sender=fl_group_at)