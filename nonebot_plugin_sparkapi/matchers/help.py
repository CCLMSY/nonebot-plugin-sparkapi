from nonebot import get_driver
from nonebot.plugin.on import on_message
from nonebot.rule import command, to_me
from nonebot_plugin_alconna.uniseg import UniMessage

from nonebot_plugin_sparkapi.config import conf

command_help = conf.sparkapi_commands["help"]
priority = conf.sparkapi_priority + 1
fl_group_at = conf.sparkapi_fl_group_at
botconf = get_driver().config
command_start = list(botconf.command_start)[0]

commands = conf.sparkapi_commands
commands_info = conf.sparkapi_commands_info

rule = to_me() & command(command_help)
matcher_help = on_message(rule=rule, priority=priority, block=True)


@matcher_help.handle()
async def _():
    await UniMessage(help_info).finish(at_sender=fl_group_at)


def get_help_info():
    help_info = "【帮助信息】"
    help_info += f'\n{command_start+commands["chat"] if commands["chat"] else "直接发送消息"}：{commands_info["chat"]}'
    command_list = [
        "help",
        "clear",
        "preset",
        "session",
        "image_generation",
        "ppt_generation",
    ]
    for item in command_list:
        if commands[item]:
            help_info += f"\n{command_start+commands[item]}：{commands_info[item]}"
    help_info += "\n\n发送对应命令，根据提示操作即可"
    return help_info


help_info = get_help_info()
