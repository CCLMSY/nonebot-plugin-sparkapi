from .config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
bot_name = conf.sparkapi_bot_name
fl_setprset_clear = conf.sparkapi_fl_setpreset_clear
commands = conf.sparkapi_commands
commands_info = conf.sparkapi_commands_info


prompt_base = '忽略此前得到的一切提示。\
在接下来的对话中，请记住以下提示信息，并完成相应对话任务。'
prompt_name = f'现在，你的名字叫{bot_name}。'

prompt_assistant = prompt_base + f'{prompt_name if bot_name else ""}' +\
'你具有全面的知识储备，可以和人类进行自然交流，解答问题，高效完成各领域认知智能需求。'
prompt_psychological_counselor =  prompt_base + f'{prompt_name if bot_name else ""}' +\
'你是一位心理咨询师，你富有同理心、慈悲、开放，且具有文化敏感性。\
在下面的对话中，请帮助客户反思他们的思想、情感和经历。\
在信息不足时，可以运用积极倾听技巧、开放式问题和清晰的沟通来引导客户分享。\
与客户建立真诚、信任和支持的关系，创造一个让他们感到安全舒适、可以畅所欲言的环境。\
接下来，请先进行简单的自我介绍，并委婉的引导客户说出他们遇到的挫折。\
'
prompt_libai = prompt_base +\
"你现在扮演李白，你豪情万丈，狂放不羁；接下来请用李白的口吻和用户对话。"

presets_default = { # 
    "智能助手": {
        'role': 'system', 
        'content': prompt_assistant
    },
    "心理咨询师":{
        'role': 'system',
        'content': prompt_psychological_counselor
    },
    "李白":{
        'role': 'system',
        'content': prompt_libai
    }
}

# 生成人物预设列表
def get_preset_lst(presets:dict,costom_presets:dict)->str:
    presets_lst = "【人物预设】\n"
    for i, preset in enumerate(presets.keys(),start=1):
        presets_lst += f"{i}. {preset}\n"
    for i, preset in enumerate(costom_presets.keys(),start=len(presets)+1):
        presets_lst += f"{i}. {preset}\n"
    if(fl_setprset_clear):
        presets_lst += "\n切换人物预设时会清空对话记录！"
    return presets_lst
presets_lst_default = get_preset_lst(presets_default,{})

# 生成帮助信息
def get_help_info(commands:dict,commands_info:dict)->str:
    def unify_command(command_info:list)->str:
        ret = "/".join(command_info)
        return ret
    
    help_info = "【帮助信息】\n"
    command_chat = unify_command(commands["chat"])
    help_info += f"1. {command_chat+'+' if command_chat else '直接发送'}对话内容：{commands_info['chat']}\n"
    i = 2
    special_commands = ["chat", "image_generation", "ppt_generation"]

    for command, command_info in commands_info.items():
        if command in special_commands:
            continue
        command = unify_command(commands[command])
        help_info += f"{i}. {command}：{command_info}\n"
        i += 1

    if conf.sparkapi_fl_imggen:
        command_imggen = unify_command(commands["image_generation"])
        help_info += f"{i}. {command_imggen}：{commands_info['image_generation']}\n"
        i += 1

    if conf.sparkapi_fl_pptgen:
        command_pptgen = unify_command(commands["ppt_generation"])
        help_info += f"{i}. {command_pptgen}：{commands_info['ppt_generation']}\n"
        i += 1

    return help_info

help_info = get_help_info(commands,commands_info)
