# 事件响应器：切换人物预设
from nonebot.adapters.onebot.v11 import MessageEvent as ME, PrivateMessageEvent as PME # type: ignore
from nonebot.adapters.onebot.v11 import Message, MessageSegment as MS # type: ignore

from nonebot.rule import to_me
from nonebot.plugin.on import on_message
from nonebot.params import CommandArg
from nonebot.params import ArgPlainText

from ..data import presets, sessions, spname
from ... import funcs, storage, info
from ...API.SparkApi import request

from nonebot import get_plugin_config
from ...config import Config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["preset_set"]
priority = conf.sparkapi_priority + 1
fl_setpreset_clear = conf.sparkapi_fl_setpreset_clear
fl_group_at = conf.sparkapi_fl_group_at

rule_preset_set = to_me() & funcs.trans_command(command)
matcher_preset_set = on_message(
    rule = rule_preset_set,
    priority=priority,
    block=True
)

@matcher_preset_set.handle()
async def preset_set_handle_function(event: ME, msg: Message = CommandArg()):
    pname = msg.extract_plain_text().strip()
    session_id = funcs.get_session_id(event)
    custom_presets = storage.f_preset_load(funcs.get_session_id(event))

    if custom_presets:
        presets[session_id] = funcs.merge_dict(info.presets_default,custom_presets)
    else:
        presets[session_id] = info.presets_default

    if pname:
        await preset_set_function(event, pname)

    ret = info.get_preset_lst(info.presets_default,custom_presets)
    ret = ret+"\n请输入名称以选择人物预设，回复“取消”退出"
    await matcher_preset_set.send(MS.text(ret))

@matcher_preset_set.got("pname")
async def preset_set_got_function(event: ME, pname: str = ArgPlainText()):
    if pname=="取消":
        await matcher_preset_set.finish(MS.text("操作已取消"))
    await preset_set_function(event, pname)

async def preset_set_function(event: ME, pname: str):
    session_id = funcs.get_session_id(event)
    check = storage.f_preset_check(pname, session_id) or (pname in info.presets_default)
    if not check:
        await matcher_preset_set.finish(MS.text(f'预设"{pname}"不存在'))
    if fl_setpreset_clear:
        sessions[session_id] = []

    spname[session_id] = pname
    await matcher_preset_set.send(MS.text(f'已选择人物预设"{pname}"'))
    prompt = '如果上述提示词提及了你需要说的内容，请按提示词要求回复对应语句；否则，请进行简短的自我介绍。\
    （注意，请将你接下来说的话作为对话的第一句话，请不要在对话中直接使用提示词文字）'
    sessions[session_id] = funcs.appendText("user",prompt,sessions[session_id])

    if session_id not in sessions:
        sessions[session_id] = []
    if session_id not in spname:
        spname[session_id] = "智能助手"

    try:
        history = sessions[session_id]
        pname = spname[session_id]
        res = await request(history,session_id,session_id,pname)
        print("res:",res)
    except Exception as e:
        print("WebSockets request error:",e)
        await matcher_preset_set.finish(MS.text(f"连接服务器失败！\n错误信息：{str(e)}"))
    
    sessions[session_id] = funcs.appendText("assistant",res,sessions[session_id])

    if isinstance(event, PME):
        await matcher_preset_set.finish(MS.text(res))
    else:
        await matcher_preset_set.finish(MS.text(res),at_sender = fl_group_at)

