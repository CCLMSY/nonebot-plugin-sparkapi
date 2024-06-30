# 事件响应器：删除人物预设
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
command = conf.sparkapi_commands["preset_delete"]
priority = conf.sparkapi_priority + 1

rule_preset_delete = to_me() & funcs.trans_command(command)
matcher_preset_delete = on_message(
    rule = rule_preset_delete,
    priority = priority,
    block = True
)

@matcher_preset_delete.handle()
async def preset_delete_handle_function(event: ME, msg: Message = CommandArg()):
    pname = msg.extract_plain_text().strip()
    session_id = funcs.get_session_id(event)
    custom_presets = storage.f_preset_load(funcs.get_session_id(event))

    if custom_presets:
        presets[session_id] = funcs.merge_dict(info.presets_default,custom_presets)
    else:
        presets[session_id] = info.presets_default

    if pname in info.presets_default:
        await matcher_preset_delete.finish(MS.text("不可删除默认预设！"))

    if len(custom_presets) == 0:
        await matcher_preset_delete.finish(MS.text("无自定义预设！"))

    if pname:
        await preset_delete_function(event, pname)
        
    ret = info.get_preset_lst({},custom_presets)
    ret = ret+"\n请输入名称以删除人物预设，回复“取消”退出"
    await matcher_preset_delete.send(MS.text(ret))

@matcher_preset_delete.got("pname")
async def preset_delete_got_function(event: ME, pname: str = ArgPlainText()):
    if pname=="取消":
        await matcher_preset_delete.finish(MS.text("操作已取消"))

    await preset_delete_function(event, pname)
    
async def preset_delete_function(event: ME, pname: str):
    
    session_id = funcs.get_session_id(event)

    if storage.f_preset_delete(pname, session_id):
        if (session_id in spname) and (spname[session_id] == pname):
            spname[session_id] = "智能助手"
        await matcher_preset_delete.finish(MS.text(f'已删除预设"{pname}"'))
    else:
        await matcher_preset_delete.finish(MS.text("删除预设失败！"))
    
