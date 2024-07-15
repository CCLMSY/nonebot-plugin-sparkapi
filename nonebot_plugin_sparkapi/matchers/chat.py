from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import Message, MessageSegment as MS

from nonebot.rule import to_me,command
from nonebot.plugin.on import on_message
from nonebot.params import CommandArg,EventMessage

from ..funcs import get_session_id
from ..API.SparkApi import request_chat

from ..config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
command_chat = conf.sparkapi_command_chat
priority = conf.sparkapi_priority+2
max_length = conf.sparkpai_model_maxlength
fl_notice = conf.sparkapi_fl_notice
fl_group_at = conf.sparkapi_fl_group_at

rule = (to_me() & command(command_chat))  if command_chat else to_me()
matcher_chat = on_message(
    rule = rule,
    priority=priority,
    block=True
)

@matcher_chat.handle()
async def _(event:ME, arg:Message=CommandArg() if command_chat else EventMessage()):
    question = arg.extract_plain_text().strip()
    if not question:
        await matcher_chat.finish("内容不能为空！", at_sender=fl_group_at)
    session_id = get_session_id(event)
    answer = ""
    if fl_notice:
        await matcher_chat.send(MS.text("正在思考中..."), at_sender=fl_group_at)
    try:
        answer = await request_chat(session_id, question)
    except Exception as e:
        await matcher_chat.finish(MS.text(f"对话请求失败！请联系开发者。\n错误信息：{type(e)}:{e}"), at_sender=fl_group_at)
    else:
        await matcher_chat.finish(MS.text(answer), at_sender=fl_group_at)