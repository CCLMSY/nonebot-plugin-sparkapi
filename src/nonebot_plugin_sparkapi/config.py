from nonebot import get_plugin_config
from nonebot_plugin_localstore import get_data_dir
from pydantic import BaseModel


class Config(BaseModel):
    # API信息：讯飞开放平台控制台（https://console.xfyun.cn/）中的“服务接口认证信息”
    sparkapi_app_id: str
    """APP ID"""
    sparkapi_api_secret: str
    """API Secret"""
    sparkapi_api_key: str
    """API Key"""

    # 模型设置
    sparkapi_model_version: str = "default"
    '''星火大模型的版本，默认为当前最新。可选值："default", "v4.0", "v3.5", "v3.0", "v2.0", "v1.5"'''
    sparkapi_model_top_k: int = 4
    """平衡生成文本的质量和多样性。较小的 k 值会减少随机性，使得输出更加稳定；而较大的 k 值会增加随机性，产生更多新颖的输出。取值范围[1, 6]，默认为4"""
    sparkapi_model_temperature: float = 0.5
    """控制结果随机性，取值越高随机性越强，即相同的问题得到的不同答案的可能性越高。取值范围 (0，1]，默认为0.5"""
    sparkpai_model_maxlength: int = 8000
    """
    单次上下文最大token长度，不能超过8000token。

    1token≈1.5个中文字≈1个英文单词。保守起见，在本插件中1token取1.25个字符

    该值越大，对话历史记录保留越长，单次请求消耗token的最大值越大。建议取值范围：[4000,8000]

    注：QQ单条消息上限4500个字符（计3600token），消息超过最大长度可能导致响应不正确
    """

    sparkapi_priority: int = 80  # 优先级
    """
    优先级：该值越小，事件越先被触发。本插件建议设置较大的值。可选值：1~97

    若触发本插件事件，所有插件中优先级大于此值的事件都将被阻断。

    本插件中事件的优先级顺序：私聊阻断（=priority）< 功能（=priority+1）< 对话（=priority+2）
    """

    # fmt: off
    # 命令设置
    sparkapi_command_chat : str = ""
    """机器人对话指令（默认：为""即可直接对话）"""
    # 命令
    sparkapi_commands : dict[str, str] = { 
        "chat" : "",                        # 本条不生效，仅便于插件配置并维持代码一致性
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
        "image_generation" : "image",       # AI绘图
        "ppt_generation" : "ppt",           # AI制作PPT
        "help" : "help"                     # 帮助信息
    }
    # 命令说明，用于生成帮助信息
    sparkapi_commands_info: dict[str, str] = { 
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
        "image_generation" : "AI根据文字描述绘制一张图片",
        "ppt_generation" : "AI根据文字描述制作PPT",
        "help" : "显示帮助信息"
    }
    # fmt: on

    # 聊天设置
    sparkapi_fl_notice: bool = False
    """收到对话请求时是否提示已收到请求"""
    sparkapi_fl_private_chat: bool = True
    """允许私聊"""
    sparkapi_fl_group_public: bool = False
    """
    群聊启用公共会话

    True：所有人共享同一会话

    False：每个人的会话各自独立
    """
    sparkapi_fl_interflow: bool = False
    """对于同一用户，群聊与私聊数据互通（公共会话启用时，群聊仍独立）"""
    sparkapi_fl_group_at: bool = True
    """群聊中，回复时是否需要@提问者"""

    # 扩展功能
    sparkapi_fl_imggen: bool = False
    """启用图片生成功能（需要申请独立用量，API信息一般与AI对话API一致）"""
    sparkapi_fl_pptgen: bool = False
    """启用PPT生成功能（需要申请独立用量，API信息一般与AI对话API一致）"""

    # 图片生成设置
    sparkapi_IG_size: list[int] = [1280, 720]
    """AI绘图的图片尺寸，[宽,高]。具体尺寸可选值和API消耗请请查看文档"""

    # 其他设置
    sparkapi_bot_name: str = ""
    """机器人名字"""


conf = get_plugin_config(Config)
DATA_PATH = get_data_dir("nonebot_plugin_sparkapi")
