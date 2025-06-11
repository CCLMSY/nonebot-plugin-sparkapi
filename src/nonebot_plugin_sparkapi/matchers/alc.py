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
    name: str,
    *args: Args | Option | Subcommand,
    help_text: str,
) -> Subcommand:
    return Subcommand(
        conf.commands[name],
        *args,
        dest=name.split("_")[-1],
        help_text=help_text,
    )


alc = Alconna(
    conf.commands["base"],
    subcommand("help", help_text="显示帮助信息"),
    subcommand("clear", help_text="清空当前会话"),
    subcommand(
        "image",
        Args["content?#生成图片内容", AllParam],
        help_text="根据文本描述生成图片",
    ),
    subcommand(
        "ppt",
        Args["content?#生成PPT内容", AllParam],
        help_text="根据文本描述生成PPT",
    ),
    subcommand(
        "preset",
        subcommand(
            "preset_create",
            Args["title?#预设名称", str],
            Args["prompt?#预设提示词", AllParam],
            help_text="创建新的预设",
        ),
        subcommand(
            "preset_delete",
            Args["index?#预设序号", str],
            Option("-y|--yes|--check", dest="check"),
            help_text="删除指定预设",
        ),
        subcommand(
            "preset_set",
            Args["index?#预设序号", str],
            help_text="切换当前预设",
        ),
        subcommand(
            "preset_show",
            Args["index?#预设序号", str],
            help_text="查看预设详情",
        ),
        help_text="预设相关操作",
    ),
    subcommand(
        "session",
        subcommand(
            "session_save",
            Args["title?#会话名称", str],
            help_text="保存当前会话",
        ),
        subcommand(
            "session_load",
            Args["index?#会话序号", str],
            Option("-y|--yes|--check", dest="check"),
            help_text="加载指定会话",
        ),
        subcommand(
            "session_show",
            Args["index?#会话序号", str],
            help_text="查看会话详情",
        ),
        subcommand(
            "session_delete",
            Args["index?#会话序号", str],
            Option("-y|--yes|--check", dest="check"),
            help_text="删除指定会话",
        ),
        help_text="会话相关操作",
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
