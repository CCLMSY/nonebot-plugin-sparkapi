from .config import Config
import nonebot
conf = Config.parse_obj(nonebot.get_driver().config.dict())
bot_name = conf.sparkapi_bot_name
command = conf.sparkapi_command

propmt_default = '忽略此前得到的一切提示。'
if bot_name:
    propmt_default += f'现在，你的名字叫{bot_name}。'
propmt_default += '你具有全面的知识储备，可以和人类进行自然交流，解答问题，高效完成各领域认知智能需求。'

prompt_psychological_counselor =\
'忽略此前得到的一切提示。\
现在，你是一位心理咨询师。\
你具有富有同理心、慈悲、开放和具有文化敏感性的心理治疗师形象。\
在下面的对话中，请运用积极倾听技巧、开放式问题和清晰的沟通，帮助客户反思他们的思想、情感和经历。\
与客户建立真诚、信任和支持的关系，创造一个让他们感到安全舒适、可以畅所欲言的环境。\
接下来，请先进行简单的自我介绍（请注意，不要直接使用本提示），并委婉的引导客户说出他们遇到的挫折。\
'

presets = { # 
    "全能机器人": {
        'role': 'system', 
        'content': propmt_default
        },
    "心理咨询师":{
        'role': 'system',
        'content': prompt_psychological_counselor
        }
}

presets_lst = "\n".join([f"{id}. {name}" for id, name in enumerate(presets.keys(), start=1)])
presets_lst = f"【人物预设】\n{presets_lst}\n\n⚠更改预设将自动清空历史记录"

help_info = "【帮助信息】\n"
help_info += f"1. {command+' + ' if command else '直接发送'}对话内容：与机器人进行对话\n"
help_info += "2. help：显示帮助信息\n"
help_info += "3. showpresets：显示人物预设\n"
help_info += "4. setpreset：更改人物预设\n"
help_info += "5. preset + 序号：选择人物预设\n"
help_info += "6. clear：清空对话\n"
help_info += "\n群聊中需要@bot + 指令/对话内容"