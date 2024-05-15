from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent,PrivateMessageEvent
from nonebot.adapters.onebot.v11 import Message , MessageSegment as MS
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.params import ArgPlainText

import nonebot
import asyncio
from copy import deepcopy

from .config import Config, ConfigError
from . import SparkApi,funcs
from .funcs import gethash,getlength,appendText
from .data import presets, presets_lst, help_info

__plugin_meta__ = PluginMetadata(
    name="科大讯飞星火大语言模型官方API聊天机器人插件",
    description="调用科大讯飞星火大语言模型官方API的聊天机器人插件，适用于所有模型版本（默认当前最新（v3.5）），支持上下文关联、人物预设",
    usage=help_info,
    type='application',
    homepage="https://github.com/CCLMSY/nonebot-plugin-sparkapi",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra = {
        "author": "CCLMSY",
        "version": "1.0.5"
    }
)

# 获取插件配置（由于gocqhttp使用pydantic==1.10.13，因此沿用老方法）
conf = Config.parse_obj(nonebot.get_driver().config.dict())

appid = conf.sparkapi_app_id
api_secret = conf.sparkapi_api_secret
api_key = conf.sparkapi_api_key

# if not appid or not api_secret or not api_key:
#     raise ConfigError("请设置API信息,可前往 https://console.xfyun.cn/ 获取")

model_version = funcs.unify_model_version(conf.sparkapi_model_version)
Spark_url = funcs.get_Spark_url(model_version)
domain = funcs.get_domain(model_version)

command = conf.sparkapi_command
private_chat = conf.sparkapi_private_chat
group_public = conf.sparkapi_group_public
group_at = conf.sparkapi_group_at
fnotice = conf.sparkapi_fnotice

max_length = conf.sparkpai_max_length
priority = conf.sparkapi_priority

sessions = {} # 会话记录
spname = {} # 选取的prompt

# block:阻止优先级更低的事件继续处理
# priority:数字越小优先级越高
# 私聊功能已关闭

sparkhelp = on_command("help",block=True,priority=5,rule = to_me()) # 显示帮助信息
showpresets = on_command("showpresets",block=True,priority=5,rule = to_me()) # 显示人物预设
setpreset = on_command("setpreset",block=True,priority=5,rule = to_me()) # 更改人物预设
clear = on_command("clear",block=True,priority=5,rule = to_me()) # 清空对话
chat = on_command(command,block=True,priority=priority,rule = to_me()) # 具有上下文的对话

@chat.handle()
async def chat_handle_function(event: MessageEvent, msg: Message = CommandArg()):
    if isinstance(event, PrivateMessageEvent) and not private_chat:
        await chat.finish(MS.text("私聊功能已关闭。如有需要，请联系管理员。"))

    content = msg.extract_plain_text().strip() # 提取纯文本
    if not content:
        await chat.finish(MS.text("请输入文字！"))

    if len(content) > max_length//2:
        await chat.finish(MS.text(f"输入文字过长：请不要超过{max_length//2}字节！"))

    if fnotice:
        await chat.send(MS.text("正在思考中..."))

    session_id = get_session_id(event)
    sid = gethash(event.get_session_id())[-20:]

    if session_id not in sessions:
        sessions[session_id] = []
        spname[session_id] = "全能机器人"

    # sessions[session_id].append({"role": "user", "content": content})
    sessions[session_id] = appendText("user",content,sessions[session_id])

    try:
        history = sessions[session_id]
        pname = spname[session_id]
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(None,request,history,sid,pname)
    except Exception as e:
        await chat.finish(MS.text(str(e)))

    # sessions[session_id].append({"role": "assistant", "content": res})
    sessions[session_id] = appendText("assistant",res,sessions[session_id])
    checklen(sessions[session_id])

    if isinstance(event, PrivateMessageEvent):
        await chat.finish(MS.text(res))
    else:
        await chat.finish(MS.text(res),at_sender = group_at)

@sparkhelp.handle()
async def sparkhelp_handle_function():
    await sparkhelp.finish(MS.text(help_info))

@showpresets.handle()
async def showpresets_handle_function():
    await showpresets.finish(MS.text(presets_lst))

@setpreset.handle()
async def setpreset_handle_function(event: MessageEvent, msg: Message = CommandArg()):
    if isinstance(event, PrivateMessageEvent) and not private_chat:
        await setpreset.finish(MS.text("私聊功能已关闭。如有需要，请联系管理员。"))
    pid = msg.extract_plain_text().strip()
    if pid:
        await fsetpreset(event, pid)

@setpreset.got("pid",prompt=presets_lst+"\n请输入编号以选择人物预设")
async def setpreset_handle_got(event: MessageEvent, pid: str = ArgPlainText()):
    await fsetpreset(event, pid)

async def fsetpreset(event, pid):
    if int(pid) > len(presets) or int(pid) <= 0:
        await setpreset.finish(MS.text("预设编号不存在"))

    session_id = get_session_id(event)
    sid = gethash(event.get_session_id())[-20:]

    sessions[session_id] = []
    spname[session_id] = list(presets.keys())[int(pid)-1]
    
    await setpreset.send(MS.text("已选择人物预设：" + spname[session_id]))
    # sessions[session_id].append({"role": "user", "content": "现在，请进行一段简短的自我介绍"})
    sessions[session_id] = appendText("user","现在，请进行一段简短的自我介绍",sessions[session_id])

    try:
        history = sessions[session_id]
        pname = spname[session_id]
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(None,request,history,sid,pname)
    except Exception as e:
        await setpreset.finish(MS.text(str(e)))

    # sessions[session_id].append({"role": "assistant", "content": res})
    sessions[session_id] = appendText("assistant",res,sessions[session_id])
    checklen(sessions[session_id])

    if isinstance(event, PrivateMessageEvent):
        await setpreset.finish(MS.text(res))
    else:
        await setpreset.finish(MS.text(res),at_sender = group_at)

@clear.handle()
async def clear_handle_function(event: MessageEvent):
    session_id = get_session_id(event)
    if session_id in sessions:
        del sessions[session_id]
        del spname[session_id]
        await clear.finish(MS.text("对话已清空"))
    else:
        await clear.finish(MS.text("无对话记录"))

# 根据消息类型创建会话ID
def get_session_id(event):
    if isinstance(event, PrivateMessageEvent):
        return "private_" + str(event.user_id)
    if group_public:
        return event.get_session_id().replace(str(event.user_id), "public")
    else:
        return event.get_session_id()

def request(history, sid, pname):
    history = deepcopy(history)
    history.insert(0, presets[pname])
    history = checklen(history)
    print(history)
    SparkApi.answer = ""
    SparkApi.main(appid,api_key,api_secret,Spark_url,domain,history,sid)
    ans = SparkApi.answer
    return ans

def checklen(text): # 检查对话长度
    while (getlength(text) > max_length):
        del text[0]
    return text
