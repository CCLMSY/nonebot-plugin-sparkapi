from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.rule import to_me,command
from nonebot.plugin.on import on_message

from nonebot_plugin_sparkapi.config import Config
import nonebot as nb
conf = nb.get_plugin_config(Config)
command_help = conf.sparkapi_commands["help"]
priority = conf.sparkapi_priority+1
fl_group_at = conf.sparkapi_fl_group_at
botconf = nb.get_driver().config
command_start = list(botconf.command_start)[0]

commands = conf.sparkapi_commands
commands_info = conf.sparkapi_commands_info

rule = to_me() & command(command_help)
matcher_help = on_message(
    rule = rule,
    priority=priority,
    block=True
)

@matcher_help.handle()
async def _():
    await matcher_help.finish(MS.text(help_info), at_sender=fl_group_at)

def get_help_info():
    help_info = "【帮助信息】"
    help_info += f'\n{command_start+commands["chat"] if commands["chat"] else "直接发送消息"}：{commands_info["chat"]}'
    command_list = ["help","clear","preset","session","image_generation","ppt_generation"]
    for item in command_list:
        help_info += f'\n{command_start+commands[item]}：{commands_info[item]}' if commands[item] else ""
    help_info += "\n\n发送对应命令，根据提示操作即可"
    return help_info

help_info = get_help_info()