from ..config import conf
from .alc import matcher

cmd_start = conf.get_cmd_start()
commands = conf.commands
commands_info = conf.commands_info


def get_help_info() -> str:
    help_info = "【帮助信息】"
    chat_cmd = cmd_start + conf.command_chat if conf.command_chat else "直接发送消息"
    help_info += f"\n{chat_cmd}：{commands_info['chat']}"
    command_list = ["help", "clear", "preset", "session"]
    if conf.fl_imggen:
        command_list.append("image_generation")
    if conf.fl_pptgen:
        command_list.append("ppt_generation")
    for item in command_list:
        if commands[item]:
            help_info += f"\n{cmd_start + commands[item]}：{commands_info[item]}"
    help_info += "\n\n发送对应命令，根据提示操作即可"
    return help_info


def get_preset_commands() -> str:
    result = "💫操作"
    result += f"\n{cmd_start + commands['preset']}：{commands_info['preset']}"
    for key in {"preset_create", "preset_set", "preset_show", "preset_delete"}:
        result += (
            f"\n{cmd_start + commands['preset']} {commands[key]}: {commands_info[key]}"
        )
    return result


def get_session_commands() -> str:
    result = "💫操作"
    result += f"\n{cmd_start + commands['session']}：{commands_info['session']}"
    for key in {"session_save", "session_load", "session_show", "session_delete"}:
        result += (
            f"\n{cmd_start + commands['session']} {commands[key]}：{commands_info[key]}"
        )
    return result


@matcher.assign("~help")
async def assign_help() -> None:
    await matcher.finish(get_help_info())
