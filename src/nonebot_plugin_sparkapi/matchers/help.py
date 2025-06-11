from ..config import conf
from .alc import matcher

cmd_start = conf.cmd_start
cmd_sep = conf.cmd_sep
cmd_info = conf.command_info
base_cmd = cmd_start + cmd_info.base + cmd_sep


def get_help_info() -> str:
    help_info = "【帮助信息】"
    chat_cmd = cmd_start + conf.command_chat if conf.command_chat else "直接发送消息"
    help_info += f"\n{chat_cmd}：{cmd_info.chat}"

    cmd_list = ["help", "clear", "preset", "session"]
    if conf.fl_imggen:
        cmd_list.append("image")
    if conf.fl_pptgen:
        cmd_list.append("ppt")
    for item in cmd_list:
        name, desc = getattr(cmd_info, item)
        help_info += f"\n{base_cmd + name}：{desc}"

    help_info += "\n\n发送对应命令，根据提示操作即可"
    return help_info


def get_preset_commands() -> str:
    result = "💫操作"
    preset_cmd = base_cmd + cmd_info.preset[0]
    result += f"\n{base_cmd + cmd_info.preset[0]}：{cmd_info.preset[1]}"
    for key in ["preset_create", "preset_set", "preset_show", "preset_delete"]:
        name, desc = getattr(cmd_info, key)
        result += f"\n{preset_cmd}{cmd_sep}{name}: {desc}"
    return result


def get_session_commands() -> str:
    result = "💫操作"
    session_cmd = base_cmd + cmd_info.session[0]
    result += f"\n{session_cmd}：{cmd_info.session[1]}"
    for key in ["session_save", "session_load", "session_show", "session_delete"]:
        name, desc = getattr(cmd_info, key)
        result += f"\n{session_cmd}{cmd_sep}{name}：{desc}"
    return result


@matcher.assign("~help")
async def assign_help() -> None:
    await matcher.finish(get_help_info())
