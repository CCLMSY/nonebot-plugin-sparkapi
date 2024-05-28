from nonebot.adapters.onebot.v11 import MessageEvent as ME,PrivateMessageEvent as PME # type: ignore
from nonebot.adapters.onebot.v11 import Message , MessageSegment as MS # type: ignore

import nonebot
from nonebot.plugin import PluginMetadata
from nonebot.plugin.on import on_message
from nonebot.params import CommandArg
from nonebot.rule import Rule,to_me,is_type
from nonebot.params import ArgPlainText
# from nonebot.permission import SUPERUSER

from copy import deepcopy

from . import SparkApi,funcs,info,storage
from .config import Config

# ---------------------------Configurations---------------------------
# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="科大讯飞星火大语言模型官方API聊天机器人插件",
    description="调用科大讯飞星火大语言模型官方API的聊天机器人插件。适用于所有模型版本（默认当前最新（v3.5）），支持上下文关联、人物预设",
    usage=info.help_info,
    type='application',
    homepage="https://github.com/CCLMSY/nonebot-plugin-sparkapi",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra = {
        "author": "CCLMSY"
    }
)

# 获取插件配置
conf = nonebot.get_plugin_config(Config)

# 获取API信息
appid = conf.sparkapi_app_id
api_secret = conf.sparkapi_api_secret
api_key = conf.sparkapi_api_key

# 获取优先级设置
priority_blockprivate = conf.sparkapi_priority
priority_function = priority_blockprivate + 1
priority_chat = priority_blockprivate + 2

# if not appid or not api_secret or not api_key:
#     raise ConfigError("请设置API信息,可前往 https://console.xfyun.cn/ 获取")

commands = conf.sparkapi_commands
fl_private_chat = conf.sparkapi_fl_private_chat
fl_group_at = conf.sparkapi_fl_group_at
fl_notice = conf.sparkapi_fl_notice
fl_setpreset_clear = conf.sparkapi_fl_setpreset_clear
maxlength = conf.sparkpai_model_maxlength
priority = conf.sparkapi_priority

sessions = {} # 会话记录
spname = {} # 选取的prompt
presets = {} # 人物预设列表

# ---------------------------Tests---------------------------
# print(unify_commands(commands["chat"]))
# print(unify_commands(commands["help"]))
# print(*unify_commands(commands["help"]))

# ---------------------------Matchers---------------------------
# 事件响应器：私聊阻断
async def fl_blockprivate() -> bool:
    return not conf.sparkapi_fl_private_chat
rule_blockprivate = is_type(PME) & fl_blockprivate
matcher_blockprivate = on_message(
    rule = rule_blockprivate,
    priority = priority_blockprivate,
    block = True
)
@matcher_blockprivate.handle()
async def blockprivate_handle_function():
    await matcher_blockprivate.finish(MS.text(conf.sparkapi_message_blockprivate))


# 事件响应器：带上下文的对话
rule_chat = to_me() & funcs.trans_command(commands["chat"])
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
    sid = funcs.get_sid(event.get_session_id())

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
        res = await request(history,sid,session_id,pname)
        print("res:",res)
    except Exception as e:
        print("WebSockets request error:",e)
        await matcher_chat.finish(MS.text(str(f"连接服务器失败！\n错误信息：{str(e)}")))

    sessions[session_id] = funcs.appendText("assistant",res,sessions[session_id])
    
    if isinstance(event, PME):
        await matcher_chat.finish(MS.text(res))
    else:
        await matcher_chat.finish(MS.text(res),at_sender = fl_group_at)


# 事件响应器：显示帮助信息
rule_help = to_me() & funcs.trans_command(commands["help"])
matcher_help = on_message(
    rule = rule_help,
    priority = priority_function,
    block = True
)
@matcher_help.handle()
async def sparkhelp_handle_function():
    await matcher_help.finish(MS.text(info.help_info))


# 事件响应器：创建人物预设
rule_preset_create = to_me() & funcs.trans_command(commands["preset_create"])
matcher_preset_create = on_message(
    rule = rule_preset_create,
    priority = priority_function,
    block=True
)
@matcher_preset_create.got("pname",prompt="请输入预设名称\n回复“取消”退出")
async def preset_create_got_check(event: ME, pname: str= ArgPlainText()):
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


# 事件响应器：删除人物预设
rule_preset_delete = to_me() & funcs.trans_command(commands["preset_delete"])
matcher_preset_delete = on_message(
    rule = rule_preset_delete,
    priority = priority_function,
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

    if len(custom_presets) == 0:
        await matcher_preset_delete.finish(MS.text("无自定义预设！"))

    if pname:
        await preset_delete_function(event, pname)
        
    msg = info.get_preset_lst({},custom_presets)
    msg = msg+"\n请输入名称以删除人物预设，回复“取消”退出"
    await matcher_preset_delete.send(MS.text(msg))

@matcher_preset_delete.got("pname")
async def preset_delete_got_function(event: ME, pname: str = ArgPlainText()):
    if pname=="取消":
        await matcher_preset_delete.finish(MS.text("操作已取消"))

    await preset_delete_function(event, pname)
    
async def preset_delete_function(event: ME, pname: str):
    if pname in info.presets_default:
        await matcher_preset_delete.finish(MS.text("不可删除默认预设！"))
    
    session_id = funcs.get_session_id(event)

    if storage.f_preset_delete(pname, session_id):
        if (session_id in spname) and (spname[session_id] == pname):
            spname[session_id] = "智能助手"
        await matcher_preset_delete.finish(MS.text(f'已删除预设"{pname}"'))
    else:
        await matcher_preset_delete.finish(MS.text("删除预设失败！"))
    

# 事件响应器：显示人物预设
rule_preset_show = to_me() & funcs.trans_command(commands["preset_show"])
matcher_preset_show = on_message(
    rule = rule_preset_show,
    priority = priority_function,
    block = True
)
@matcher_preset_show.handle()
async def preset_show_handle_function(event:ME):
    session_id = funcs.get_session_id(event)
    custom_presets = storage.f_preset_load(session_id)

    msg = info.get_preset_lst(info.presets_default,custom_presets)
    msg += f"\n当前预设为：{spname.get(session_id,'智能助手')}"
    await matcher_preset_show.finish(MS.text(msg))


# 事件响应器：切换人物预设
rule_preset_set = to_me() & funcs.trans_command(commands["preset_set"])
matcher_preset_set = on_message(
    rule = rule_preset_set,
    priority=priority_function,
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

    msg = info.get_preset_lst(info.presets_default,custom_presets)
    msg = msg+"\n请输入名称以选择人物预设，回复“取消”退出"
    await matcher_preset_set.send(MS.text(msg))

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
        sid = funcs.get_sid(session_id)
        res = await request(history,sid,session_id,pname)
        print("res:",res)
    except Exception as e:
        print("WebSockets request error:",e)
        await matcher_preset_set.finish(MS.text(f"连接服务器失败！\n错误信息：{str(e)}"))
    
    sessions[session_id] = funcs.appendText("assistant",res,sessions[session_id])

    if isinstance(event, PME):
        await matcher_preset_set.finish(MS.text(res))
    else:
        await matcher_preset_set.finish(MS.text(res),at_sender = fl_group_at)


# 事件响应器：清空对话
rule_session_clear = to_me() & funcs.trans_command(commands["session_clear"])
matcher_session_clear = on_message(
    rule = rule_session_clear,
    priority=priority_function,
    block=True
)
@matcher_session_clear.handle()
async def session_clear_handle_function(event: ME):
    session_id = funcs.get_session_id(event)

    if session_id in sessions:
        del sessions[session_id]
        del spname[session_id]
        await matcher_session_clear.finish(MS.text("对话已清空"))
    else:
        await matcher_session_clear.finish(MS.text("当前无对话记录"))


# 事件响应器：保存对话记录
rule_session_save = to_me() & funcs.trans_command(commands["session_save"])
matcher_session_save = on_message(
    rule = rule_session_save,
    priority=priority_function,
    block=True
)
@matcher_session_save.handle()
async def session_save_handle_function(event: ME):
    session_id = funcs.get_session_id(event)

    if session_id in sessions:
        storage.f_session_save(sessions[session_id], spname[session_id], session_id)
        await matcher_session_save.finish(MS.text("当前对话记录已保存！"))
    else:
        await matcher_session_save.finish(MS.text("当前无对话记录"))


# 事件响应器：加载对话记录
rule_session_load = to_me() & funcs.trans_command(commands["session_load"])
matcher_session_load = on_message(
    rule = rule_session_load,
    priority=priority_function,
    block=True
)
@matcher_session_load.handle()
async def session_load_handle_function(event: ME):
    session_id = funcs.get_session_id(event)
    session, pname = storage.f_session_load(session_id)

    if session:
        sessions[session_id] = session
        spname[session_id] = pname
        await matcher_session_load.finish(MS.text("已加载上次保存的对话记录！"))
    else:
        await matcher_session_load.finish(MS.text("未保存对话记录"))


# ---------------------------API Request---------------------------
model_version = funcs.unify_model_version(conf.sparkapi_model_version)
Spark_url = funcs.get_Spark_url(model_version)
domain = funcs.get_domain(model_version)

async def request(history, sid, session_id, pname):
    history = deepcopy(history)
    history.insert(0, presets[session_id][pname])
    history = funcs.checklen(history)
    print("request:", history)
    SparkApi.answer = ""
    await SparkApi.main(appid,api_key,api_secret,Spark_url,domain,history,sid)
    return SparkApi.answer