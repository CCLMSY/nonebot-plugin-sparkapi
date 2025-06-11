from typing_extensions import override

from arclet.alconna import AllParam
from nonebot.adapters import Bot, Event, Message
from nonebot.rule import to_me
from nonebot_plugin_alconna import (
    Alconna,
    Args,
    CommandMeta,
    Extension,
    Option,
    Subcommand,
    UniMessage,
    on_alconna,
)

from ..config import conf
from ..utils import check_at


def subcommand(
    name: str, help_text: str, dest: str, /, *args: Args | Option | Subcommand
) -> Subcommand:
    return Subcommand(name, *args, dest=dest, help_text=help_text)


cmd_info = conf.command_info
arg_index = Args["index?#序号", str]
opt_check = Option("-y|--yes|--check", dest="check")
alc = Alconna(
    cmd_info.base,
    subcommand(*cmd_info.help, "help"),
    subcommand(*cmd_info.clear, "clear"),
    subcommand(*cmd_info.image, "image", Args["content?#生成图片内容", AllParam]),
    subcommand(*cmd_info.ppt, "ppt", Args["content?#生成PPT内容", AllParam]),
    subcommand(
        *cmd_info.preset,
        "preset",
        subcommand(
            *cmd_info.preset_create,
            "create",
            Args["title?#预设名称", str],
            Args["prompt?#预设提示词", AllParam],
        ),
        subcommand(*cmd_info.preset_delete, "delete", arg_index, opt_check),
        subcommand(*cmd_info.preset_set, "set", arg_index),
        subcommand(*cmd_info.preset_show, "show", arg_index),
    ),
    subcommand(
        *cmd_info.session,
        "session",
        subcommand(*cmd_info.session_save, "save", Args["title?#会话名称", str]),
        subcommand(*cmd_info.session_load, "load", arg_index, opt_check),
        subcommand(*cmd_info.session_show, "show", arg_index),
        subcommand(*cmd_info.session_delete, "delete", arg_index, opt_check),
        subcommand(*cmd_info.session_rollback, "rollback"),
    ),
    meta=CommandMeta(
        description="科大讯飞星火大模型官方API聊天机器人插件",
        usage=conf.help_command,
        author="CCLMSY & wyf7685",
    ),
)


class AtExtension(Extension):
    @property
    @override
    def id(self) -> str:
        return "nbp-sparkapi:AtExtension"

    @property
    @override
    def priority(self) -> int:
        return 18

    @override
    async def send_wrapper(
        self,
        bot: Bot,
        event: Event,
        send: str | Message | UniMessage,
    ) -> UniMessage:
        if isinstance(send, Message):
            send = UniMessage.generate_sync(message=send)
        return check_at(send)


matcher = on_alconna(
    alc,
    rule=to_me() if conf.require_at else None,
    use_cmd_start=conf.use_cmd_start,
    use_cmd_sep=conf.use_cmd_sep,
    priority=conf.priority + 1,
    block=True,
    extensions=[AtExtension],
)
