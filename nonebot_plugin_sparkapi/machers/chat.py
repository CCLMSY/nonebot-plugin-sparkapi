# 事件响应器：带上下文的对话
from nonebot.adapters.onebot.v11 import MessageEvent as ME, PrivateMessageEvent as PME # type: ignore
from nonebot.adapters.onebot.v11 import Message, MessageSegment as MS # type: ignore

from nonebot.rule import to_me
from nonebot.plugin.on import on_message
from nonebot.params import CommandArg

from .. import funcs, storage, info
from .data import presets, sessions, spname
from ..API.SparkApi import request

from nonebot import get_plugin_config
from ..config import Config
conf = get_plugin_config(Config)
command_chat = conf.sparkapi_command_chat
priority_chat = conf.sparkapi_priority + 2
maxlength = conf.sparkpai_model_maxlength
fl_notice = conf.sparkapi_fl_notice
fl_group_at = conf.sparkapi_fl_group_at

rule_chat = to_me() & funcs.trans_command(command_chat)
matcher_chat = on_message(
    rule = rule_chat,
    priority = priority_chat,
    block = True
)

@matcher_chat.handle()
async def chat_handle_function(event: ME, msg: Message = CommandArg()):
    content = msg.extract_plain_text().strip()
    if not content:
        await matcher_chat.finish(MS.text("请输入文字！"))

    if len(content) > maxlength//2:
        await matcher_chat.finish(MS.text(f"输入文字过长：请不要超过{maxlength//2}字节！"))

    if fl_notice:
        await matcher_chat.send(MS.text("正在思考中..."))

    session_id = funcs.get_session_id(event)

    costom_presets = storage.f_preset_load(session_id)
    if costom_presets:
        presets[session_id] = funcs.merge_dict(info.presets_default,costom_presets)
    else:
        presets[session_id] = info.presets_default

    if session_id not in sessions:
        sessions[session_id] = []
    if session_id not in spname:
        spname[session_id] = "智能助手"

    sessions[session_id] = funcs.appendText("user",content,sessions[session_id])

    try:
        history = sessions[session_id]
        pname = spname[session_id]
        res = await request(history,session_id,session_id,pname)
        print("res:",res)
    except Exception as e:
        print("WebSockets request error:",e)
        await matcher_chat.finish(MS.text(str(f"连接服务器失败！\n错误信息：{str(e)}")))

    sessions[session_id] = funcs.appendText("assistant",res,sessions[session_id])
    
    if isinstance(event, PME):
        await matcher_chat.finish(MS.text(res))
    else:
        await matcher_chat.finish(MS.text(res),at_sender = fl_group_at)

