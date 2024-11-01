from nonebot import get_driver
from nonebot.plugin.on import on_command
from nonebot.rule import to_me

from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import solve_at

command_start = next(iter(get_driver().config.command_start), "/")
commands = conf.sparkapi_commands
commands_info = conf.sparkapi_commands_info


matcher_help = on_command(
    conf.sparkapi_commands["help"],
    rule=to_me(),
    priority=conf.sparkapi_priority + 1,
    block=True,
)


@matcher_help.handle()
async def _():
    await solve_at(help_info).finish()


def get_help_info():
    help_info = "【帮助信息】"
    help_info += f'\n{command_start+commands["chat"] if commands["chat"] else "直接发送消息"}：{commands_info["chat"]}'
    command_list = [
        "help",
        "clear",
        "preset",
        "session"
    ]
    if conf.sparkapi_fl_imggen:
        command_list.append("image_generation")
    if conf.sparkapi_fl_pptgen:
        command_list.append("ppt_generation")
    for item in command_list:
        if commands[item]:
            help_info += f"\n{command_start+commands[item]}：{commands_info[item]}"
    help_info += "\n\n发送对应命令，根据提示操作即可"
    return help_info


help_info = get_help_info()
