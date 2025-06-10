import nonebot_plugin_localstore as store
from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel


class ScopedConfig(BaseModel):
    # API信息：讯飞开放平台控制台（https://console.xfyun.cn/）中的“服务接口认证信息”
    app_id: str
    """APP ID"""
    api_secret: str
    """API Secret"""
    api_key: str
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

    # fmt: off
    # 命令设置
    command_chat: str = ""
    """机器人对话指令（默认：为""即可直接对话）"""
    # 命令
    commands: dict[str, str] = {
        "base" : "spark",                   # 命令前缀
        "preset" : "preset",                # 预设管理
            "preset_create" : "create",     # 创建人物预设
            "preset_set" : "set",           # 切换人物预设
            "preset_show" : "show",         # 显示人物预设
            "preset_delete" : "delete",     # 删除人物预设
        "session" : "session",              # 会话管理
            "session_save" : "save",        # 保存对话记录
            "session_load" : "load",        # 加载对话记录
            "session_show" : "show",        # 显示对话记录
            "session_delete" : "delete",    # 删除对话记录
        "clear" : "clear",                  # 清空当前对话
        "image" : "image",                  # AI绘图
        "ppt" : "ppt",                      # AI制作PPT
        "help" : "help",                    # 帮助信息
    }
    # 命令说明，用于生成帮助信息
    commands_info: dict[str, str] = {
        "chat" : "与机器人进行对话",
        "preset" : "预设管理",
            "preset_create" : "创建人物预设",
            "preset_set" : "选择人物预设",
            "preset_show" : "显示人物预设",
            "preset_delete" : "删除人物预设",
        "session" : "会话管理",
            "session_save" : "保存本次对话记录",
            "session_load" : "加载上次保存的对话记录",
            "session_show" : "显示对话记录",
            "session_delete" : "删除对话记录",
        "clear" : "清空当前对话",
        "image" : "AI根据文字描述绘制一张图片",
        "ppt" : "AI根据文字描述制作PPT",
        "help" : "显示帮助信息",
    }
    # fmt: on

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

    @staticmethod
    def get_cmd_start() -> str:
        return next(iter(get_driver().config.command_start), "/")

    @property
    def help_command(self) -> str:
        cmd_start = self.get_cmd_start() if self.use_cmd_start else ""
        return f"{cmd_start}{self.commands['base']} --help"


class Config(BaseModel):
    sparkapi: ScopedConfig


conf = get_plugin_config(Config).sparkapi
DATA_PATH = store.get_plugin_data_dir()
