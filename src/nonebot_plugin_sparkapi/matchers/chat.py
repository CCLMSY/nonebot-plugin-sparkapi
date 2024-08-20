from nonebot.adapters import Message
from nonebot.params import CommandArg, EventMessage
from nonebot.plugin.on import on_message
from nonebot.rule import command, to_me

from nonebot_plugin_sparkapi.API.SparkApi import request_chat
from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import SessionID, solve_at

command_chat = conf.sparkapi_command_chat
priority = conf.sparkapi_priority + 2
max_length = conf.sparkpai_model_maxlength
fl_notice = conf.sparkapi_fl_notice
fl_group_at = conf.sparkapi_fl_group_at

rule = (to_me() & command(command_chat)) if command_chat else to_me()
matcher_chat = on_message(rule=rule, priority=priority, block=True)
arg_dependency = CommandArg() if command_chat else EventMessage()


@matcher_chat.handle()
async def _(
    session_id: SessionID,
    arg: Message = arg_dependency,
):
    question = arg.extract_plain_text().strip()
    if not question:
        await solve_at("内容不能为空！").finish()

    receipt = None
    if fl_notice:
        receipt = await solve_at("正在思考中...").send()

    try:
        answer = await request_chat(session_id, question)
    except Exception as e:
        answer = f"对话请求失败！请联系开发者。\n错误信息：{type(e)}: {e}"

    if receipt is not None:
        await receipt.recall()
    await solve_at(answer).finish()
