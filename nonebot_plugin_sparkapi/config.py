from pydantic import BaseModel
from typing import Optional

class Config(BaseModel):
    # 讯飞开放平台控制台中的 服务接口认证信息
    sparkapi_app_id: Optional[str] = "" # APP ID
    sparkapi_api_secret: Optional[str] = "" # API Secret
    sparkapi_api_key: Optional[str] = "" # API Key

    sparkapi_model_version: str = "" # 星火大模型的版本，默认为当前最新。可选值：v3.5, v3.0, v2.0, v1.5
    sparkapi_model_top_k: int = 4 # 平衡生成文本的质量和多样性。较小的 k 值会减少随机性，使得输出更加稳定；而较大的 k 值会增加随机性，产生更多新颖的输出。取值范围[1, 6]，默认为4
    sparkapi_model_temperature : float = 0.5 # 控制结果随机性，取值越高随机性越强，即相同的问题得到的不同答案的可能性越高。取值范围 (0，1]，默认为0.5

    sparkapi_command_chat :str = "" # 机器人对话指令，默认为空可直接对话（需要同时在`.env`中配置命令起始字符为空：COMMAND_START = [""]）
    sparkapi_private_chat: bool = True # 允许私聊
    sparkapi_group_public: bool = False # 群聊启用公共会话：True：所有人共享同一会话；False：每个人的会话各自独立
    sparkapi_group_at: bool = True # 群聊回复时是否需要@提问者
    sparkapi_fnotice:bool = True # 收到请求时是否提示已收到请求

    sparkapi_priority: int = 90 # 聊天事件响应器优先级，[1,99]，数字越小优先级越高
    sparkpai_max_length: int = 8000 # 单次上下文最大长度 越大，对话历史记录保留越长，消耗token上限越高

    sparkapi_setpreset_clear: bool = True # 切换人物预设时是否清空上下文

    sparkapi_bot_name: str = "" # 机器人名字

commands = {
    "chat" : "chat", # 此处chat项只是为了保持代码一致性，在此处修改不生效，需要修改该命令请参阅插件文档
    "help" : "help", # 显示帮助信息
    "showpresets" : "presets", # 显示人物预设
    "setpreset" : "set", # 更改人物预设
    "clear" : "clear", # 清空对话
    "savesession" : "save", # 保存对话记录
    "loadsession" : "load"  # 加载对话记录
}
commands_lst = {
    f"{commands['chat'] + ' + ' if commands['chat'] else '直接发送'}对话内容" : "与机器人进行对话",
    commands["help"] : "显示帮助信息",
    commands["showpresets"] : "显示人物预设",
    commands["setpreset"] : "更改人物预设",
    f"{commands['setpreset']} + 序号" : "选择人物预设",
    commands["savesession"] : "保存当前对话记录",
    commands["loadsession"] : "加载上次保存的对话记录",
    commands["clear"] : "清除对话"
}
