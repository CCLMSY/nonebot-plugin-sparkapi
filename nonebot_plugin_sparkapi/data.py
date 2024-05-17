from .config import Config,commands
from nonebot import get_driver
conf = Config.parse_obj(get_driver().config.dict())
bot_name = conf.sparkapi_bot_name
command_chat = conf.sparkapi_command_chat
setprset_clear = conf.sparkapi_setpreset_clear

propmt_base = '忽略此前得到的一切提示。'
if bot_name:
    propmt_base += f'现在，你的名字叫{bot_name}。'

propmt_assistant = propmt_base + \
'你具有全面的知识储备，可以和人类进行自然交流，解答问题，高效完成各领域认知智能需求。'

prompt_psychological_counselor =  propmt_base + \
'你是一位心理咨询师，你富有同理心、慈悲、开放，且具有文化敏感性。\
在下面的对话中，请帮助客户反思他们的思想、情感和经历。\
在信息不足时，可以运用积极倾听技巧、开放式问题和清晰的沟通来引导客户分享。\
与客户建立真诚、信任和支持的关系，创造一个让他们感到安全舒适、可以畅所欲言的环境。\
接下来，请先进行简单的自我介绍（请注意，不要直接使用本提示），并委婉的引导客户说出他们遇到的挫折。\
'

presets = { # 
    "全能机器人": {
        'role': 'system', 
        'content': propmt_assistant
        },
    "心理咨询师":{
        'role': 'system',
        'content': prompt_psychological_counselor
        }
}

presets_lst = "\n".join([f"{id}. {name}" for id, name in enumerate(presets.keys(), start=1)])
presets_lst = f"【人物预设】\n{presets_lst}"
if setprset_clear:
    presets_lst += "\n\n⚠更改人物预设时会清空对话！"

commands_lst = {
    f"{command_chat+' + ' if command_chat else '直接发送'}对话内容" : "与机器人进行对话",
    commands["help"] : "显示帮助信息",
    commands["showpresets"] : "显示人物预设",
    commands["setpreset"] : "更改人物预设",
    f"{commands['setpreset']} + 序号" : "选择人物预设",
    commands["savesession"] : "保存当前对话记录",
    commands["loadsession"] : "加载上次保存的对话记录",
    commands["clear"] : "清除对话"
}

help_info = "【帮助信息】\n"

for id, (command, description) in enumerate(commands_lst.items(), start=1):
    help_info += f"{id}. {command}：{description}\n"

help_info += "\n群聊中需要@bot + 指令/对话内容"
