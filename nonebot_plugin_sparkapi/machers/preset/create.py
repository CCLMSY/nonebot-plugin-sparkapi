# 事件响应器：创建人物预设
from nonebot.adapters.onebot.v11 import MessageEvent as ME, PrivateMessageEvent as PME # type: ignore
from nonebot.adapters.onebot.v11 import Message, MessageSegment as MS # type: ignore

from nonebot.rule import to_me
from nonebot.plugin.on import on_message
from nonebot.params import CommandArg
from nonebot.params import ArgPlainText

from ..data import presets, sessions, spname
from ... import funcs, storage, info

from nonebot import get_plugin_config
from ...config import Config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["preset_create"]
priority = conf.sparkapi_priority + 1

rule_preset_create = to_me() & funcs.trans_command(command)
matcher_preset_create = on_message(
    rule = rule_preset_create,
    priority = priority,
    block=True
)

@matcher_preset_create.got("pname",prompt="请输入预设名称\n回复“取消”退出")
async def preset_create_got_check(event: ME, pname: str= ArgPlainText()):
    # print(presets)
    if pname=="取消":
        await matcher_preset_create.finish(MS.text("操作已取消"))

    session_id = funcs.get_session_id(event)
    
    check = storage.f_preset_check(pname, session_id) or (pname in info.presets_default)
    if check:
        await matcher_preset_create.finish(MS.text(f'已存在名为"{pname}"的预设'))

@matcher_preset_create.got("prompt",prompt="请输入预设内容\n回复“取消”退出")
async def preset_create_got_function(event: ME, pname: str = ArgPlainText(), prompt: str = ArgPlainText()):
    if prompt=="取消":
        await matcher_preset_create.finish(MS.text("操作已取消"))

    prompt = info.prompt_base + prompt
    await preset_create_function(event, pname, prompt)

async def preset_create_function(event: ME, pname: str, prompt: str):
    session_id = funcs.get_session_id(event)
    storage.f_preset_create(pname, prompt, session_id)

    try:
        custom_preset = storage.f_preset_load(session_id)
        presets[session_id]=funcs.merge_dict(info.presets_default,custom_preset)
    except:
        await matcher_preset_create.finish(MS.text("创建预设失败！"))

    await matcher_preset_create.finish(MS.text("创建预设成功！"))

