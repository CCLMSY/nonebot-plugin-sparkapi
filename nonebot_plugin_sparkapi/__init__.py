from nonebot.plugin import PluginMetadata

from .config import Config
from . import matchers

# ---------------------------Configurations---------------------------
# 插件元数据
__plugin_meta__ = PluginMetadata(
    name="科大讯飞星火大模型官方API聊天机器人插件",
    description="调用科大讯飞星火大模型官方API的聊天机器人插件。适用于所有模型版本（默认当前最新v4.0），支持上下文关联、人物预设、AI绘图、AI生成PPT等功能",
    usage=matchers.help.help_info,
    type='application',
    homepage="https://github.com/CCLMSY/nonebot-plugin-sparkapi",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra = {
        "author": "CCLMSY"
    }
)
