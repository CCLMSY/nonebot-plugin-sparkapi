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
    info: tuple[str, str],
    *args: Args | Option | Subcommand,
) -> Subcommand:
    name, help_text = info
    return Subcommand(name, *args, dest=name.split("_")[-1], help_text=help_text)


cmd_info = conf.command_info
arg_index = Args["index?#序号", str]
opt_check = Option("-y|--yes|--check", dest="check")
alc = Alconna(
    cmd_info.base,
    subcommand(cmd_info.help),
    subcommand(cmd_info.clear),
    subcommand(cmd_info.image, Args["content?#生成图片内容", AllParam]),
    subcommand(cmd_info.ppt, Args["content?#生成PPT内容", AllParam]),
    subcommand(
        cmd_info.preset,
        subcommand(
            cmd_info.preset_create,
            Args["title?#预设名称", str],
            Args["prompt?#预设提示词", AllParam],
        ),
        subcommand(cmd_info.preset_delete, arg_index, opt_check),
        subcommand(cmd_info.preset_set, arg_index),
        subcommand(cmd_info.preset_show, arg_index),
    ),
    subcommand(
        cmd_info.session,
        subcommand(cmd_info.session_save, Args["title?#会话名称", str]),
        subcommand(cmd_info.session_load, arg_index, opt_check),
        subcommand(cmd_info.session_show, arg_index),
        subcommand(cmd_info.session_delete, arg_index, opt_check),
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
