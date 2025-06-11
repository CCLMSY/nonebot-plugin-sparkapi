import functools
from typing import TYPE_CHECKING

from nonebot import get_driver, get_plugin_config, logger
from nonebot.compat import PYDANTIC_V2
from nonebot_plugin_localstore import get_plugin_data_dir
from pydantic import BaseModel, SecretStr

if TYPE_CHECKING:
    from pydantic import field_validator  # V2
else:
    from nonebot.compat import field_validator


def _generate_alias(name: str) -> str:
    if name in ("version", "top_k", "temperature", "maxlength"):
        name = f"model_{name}"
    return f"sparkapi_{name}"


class CommandInfo(BaseModel):
    base: str = "spark"
    chat: str = "与机器人进行对话"

    help: tuple[str, str] = ("help", "显示帮助信息")
    clear: tuple[str, str] = ("clear", "清空当前对话")
    image: tuple[str, str] = ("image", "AI根据文字描述绘制一张图片")
    ppt: tuple[str, str] = ("ppt", "AI根据文字描述制作PPT")

    preset: tuple[str, str] = ("preset", "预设管理")
    preset_create: tuple[str, str] = ("create", "创建人物预设")
    preset_set: tuple[str, str] = ("set", "切换人物预设")
    preset_show: tuple[str, str] = ("show", "显示人物预设")
    preset_delete: tuple[str, str] = ("delete", "删除人物预设")

    session: tuple[str, str] = ("session", "会话管理")
    session_save: tuple[str, str] = ("save", "保存本次对话记录")
    session_load: tuple[str, str] = ("load", "加载保存的对话记录")
    session_show: tuple[str, str] = ("show", "显示对话记录")
    session_delete: tuple[str, str] = ("delete", "删除对话记录")

    @field_validator("base", mode="after")
    @staticmethod
    def validate_base(value: str) -> str:
        if not value:
            raise ValueError("base command cannot be empty")
        return value.strip().lower()


class Config(BaseModel):
    # API信息：讯飞开放平台控制台（https://console.xfyun.cn/）中的“服务接口认证信息”
    app_id: SecretStr
    """APP ID"""
    api_secret: SecretStr
    """API Secret"""
    api_key: SecretStr
    """API Key"""

    # 模型设置
    version: str = "default"
    """
    星火大模型的版本，默认为当前最新。

    可选值："default", "v4.0", "v3.5", "128k", "v3.0", "v2.0", "v1.5"
    """
    top_k: int = 4
    """
    平衡生成文本的质量和多样性。

    较小的 k 值会减少随机性，使得输出更加稳定；
    而较大的 k 值会增加随机性，产生更多新颖的输出。

    取值范围[1, 6]，默认为4
    """
    temperature: float = 0.5
    """
    控制结果随机性。

    取值越高随机性越强，即相同的问题得到的不同答案的可能性越高。

    取值范围 (0，1]，默认为0.5
    """
    maxlength: int = 8000
    """
    单次上下文最大token长度，不能超过8000token。

    1token≈1.5个中文字≈1个英文单词。保守起见，在本插件中1token取1.25个字符

    该值越大，对话历史记录保留越长，单次请求消耗token的最大值越大。建议取值范围：[4000,8000]

    注：QQ单条消息上限4500个字符（计3600token），消息超过最大长度可能导致响应不正确
    """

    priority: int = 80  # 优先级
    """
    优先级：该值越小，事件越先被触发。本插件建议设置较大的值。可选值：1~97

    若触发本插件事件，所有插件中优先级大于此值的事件都将被阻断。

    本插件中事件的优先级顺序：
    私聊阻断（=priority）< 功能（=priority+1）< 对话（=priority+2）
    """

    # 命令设置
    command_chat: str = ""
    """机器人对话指令（默认：为""即可直接对话）"""
    command_info: CommandInfo = CommandInfo()
    """命令信息"""

    require_at: bool = True
    """是否需要@机器人才能触发对话"""
    use_cmd_start: bool | None = None
    """是否使用全局命令前缀（如/）来触发命令"""
    use_cmd_sep: bool | None = None
    """是否使用全局命令分隔符（如空格）来分隔命令"""

    # 聊天设置
    fl_notice: bool = False
    """收到对话请求时是否提示已收到请求"""
    fl_private_chat: bool = True
    """允许私聊"""
    fl_group_public: bool = False
    """
    群聊启用公共会话

    True：所有人共享同一会话

    False：每个人的会话各自独立
    """
    fl_interflow: bool = False
    """对于同一用户，群聊与私聊数据互通（公共会话启用时，群聊仍独立）"""
    fl_group_at: bool = True
    """群聊中，回复时是否需要@提问者"""

    # 扩展功能
    fl_imggen: bool = False
    """启用图片生成功能（需要申请独立用量，API信息一般与AI对话API一致）"""
    fl_pptgen: bool = False
    """启用PPT生成功能（需要申请独立用量，API信息一般与AI对话API一致）"""

    # 图片生成设置
    IG_size: tuple[int, int] = (1280, 720)
    """AI绘图的图片尺寸，[宽,高]。具体尺寸可选值和API消耗请请查看文档"""

    # 其他设置
    bot_name: str = ""
    """机器人名字"""

    @functools.cached_property
    def cmd_start(self) -> str:
        return (
            next(iter(get_driver().config.command_start), "/")
            if self.use_cmd_start is True
            else ""
        )

    @functools.cached_property
    def cmd_sep(self) -> str:
        return (
            next(iter(get_driver().config.command_sep), ".")
            if self.use_cmd_sep is True
            else " "
        )

    @property
    def help_command(self) -> str:
        return (
            f"{self.cmd_start}{self.command_info.base}"
            f"{self.cmd_sep}{self.command_info.help[0]}"
        )

    if PYDANTIC_V2:
        from pydantic import ConfigDict

        model_config = ConfigDict(alias_generator=_generate_alias)
        del ConfigDict

    else:

        class Config:
            alias_generator = _generate_alias


conf = get_plugin_config(Config)
logger.debug(f"Loaded config: {conf!r}")
DATA_PATH = get_plugin_data_dir()
