from pydantic import BaseModel

class Config(BaseModel):
    # API信息：讯飞开放平台控制台（https://console.xfyun.cn/）中的“服务接口认证信息”
    sparkapi_app_id: str = "" # APP ID
    sparkapi_api_secret: str = "" # API Secret
    sparkapi_api_key: str = "" # API Key

    # 模型设置
    sparkapi_model_version: str = "" # 星火大模型的版本，默认为当前最新。可选值：v3.5, v3.0, v2.0, v1.5
    sparkapi_model_top_k: int = 4 # 平衡生成文本的质量和多样性。较小的 k 值会减少随机性，使得输出更加稳定；而较大的 k 值会增加随机性，产生更多新颖的输出。取值范围[1, 6]，默认为4
    sparkapi_model_temperature : float = 0.5 # 控制结果随机性，取值越高随机性越强，即相同的问题得到的不同答案的可能性越高。取值范围 (0，1]，默认为0.5
    sparkpai_model_maxlength: int = 8000 # 单次上下文最大长度 越大，对话历史记录保留越长，消耗token上限越高
    
    # 优先级：该值越小，事件越先被触发。本插件建议设置较大的值。可选值：1~97
    # 若触发本插件事件，所有插件中优先级大于此值的事件都将被阻断。
    # 本插件中事件的优先级顺序：私聊阻断（=priority）< 功能（=priority+1）< 对话（=priority+2）
    sparkapi_priority: int = 80 # 优先级
    
    # 命令设置
    sparkapi_command_chat : str|list[str] = "" # 机器人对话指令（默认：为""且同时在`.env`中配置命令起始字符为空：COMMAND_START = [""]，即可直接对话）
    sparkapi_commands : dict[str, str|list[str]] = { # 命令
        "chat" : "", # 本条不生效，仅维持代码一致性
        "help" : ["help","帮助"], # 显示帮助信息
        "preset_show" : ["preset","人物预设"], # 显示人物预设
        "preset_set" : ["set","切换预设"], # 切换人物预设
        "preset_create" : ["create","创建预设"], # 创建人物预设
        "preset_delete" : ["delete","删除预设"], # 删除人物预设
        "session_clear" : ["clear","清空对话"], # 清空对话
        "session_save" : ["save","保存对话"], # 保存对话记录
        "session_load" : ["load","加载对话"],  # 加载对话记录
        "image_generation" : ["imggen","AI绘图"],  # AI绘图
        "ppt_generation" : ["pptgen","AIPPT",],  # AI制作PPT
    }
    sparkapi_commands_info: dict[str, str] = { # 命令说明，用于生成帮助信息
        "chat" : "与机器人进行对话",
        "help" : "显示帮助信息",
        "preset_show" : "显示人物预设菜单和当前预设",
        "preset_set" : "切换人物预设",
        "preset_create" : "创建人物预设",
        "preset_delete" : "删除人物预设",
        "session_clear" : "清空当前对话上下文",
        "session_save" : "保存本次对话记录",
        "session_load" : "加载上次保存的对话记录",
        "image_generation" : "AI根据文字描述绘制一张图片",
        "ppt_generation" : "AI根据文字描述制作PPT",
    }

    # 聊天设置  
    sparkapi_fl_notice: bool = False # 收到请求时是否提示已收到请求
    sparkapi_fl_setpreset_clear: bool = True # 切换人物预设时是否清空上下文

    # 私聊设置
    sparkapi_fl_private_chat: bool = True # 允许私聊
    sparkapi_message_blockprivate: str = "私聊功能已关闭！如有需要，请联系管理员。" # 阻断私聊时的提示信息
    
    # 群聊设置
    sparkapi_fl_group_public: bool = False # 群聊启用公共会话：True：所有人共享同一会话；False：每个人的会话各自独立
    sparkapi_fl_group_at: bool = True # 群聊中，回复时是否需要@提问者
    
    # 扩展功能
    sparkapi_fl_imggen : bool = False # 启用图片生成功能，需要申请独立用量，API信息一般与AI对话API一致
    sparkapi_fl_pptgen : bool = False # 启用PPT生成功能，需要申请独立用量，API信息一般与AI对话API一致

    # 其他设置
    sparkapi_bot_name: str = "" # 机器人名字
    # sparkapi_console_notice: bool = True # 控制台是否显示请求和响应交互内容（用于判断连接是否正常）

