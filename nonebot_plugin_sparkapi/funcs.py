import hashlib
from nonebot.adapters.onebot.v11 import PrivateMessageEvent
from .config import Config, commands_lst
from nonebot import get_driver
conf = Config.parse_obj(get_driver().config.dict())

group_public = conf.sparkapi_group_public
max_length = conf.sparkpai_max_length

def unify_model_version(model_version : str):
    version : str
    if model_version in ["v3.5","3.5","","default"]:
        version = "v3.5"
    elif model_version in ["v3.0","3.0","v3.1","3.1","v3","3"]:
        version = "v3.0"
    elif model_version in ["v2.0","2.0","v2.1","2.1","v2","2"]:
        version = "v2.0"
    elif model_version in ["v1.0","1.0","v1.1","1.1","v1.5","1.5","v1","1"]:
        version = "v1.5"
    return version

def get_Spark_url(model_version : str):
    if model_version == "v3.5":
        return "wss://spark-api.xf-yun.com/v3.5/chat"
    if model_version == "v3.0":
        return "wss://spark-api.xf-yun.com/v3.1/chat"
    if model_version == "v2.0":
        return "wss://spark-api.xf-yun.com/v2.1/chat"
    if model_version == "v1.5":
        return "wss://spark-api.xf-yun.com/v1.1/chat"

def get_domain(model_version : str):
    if model_version == "v3.5":
        return "generalv3.5"
    if model_version == "v3.0":
        return "generalv3"
    if model_version == "v2.0":
        return "generalv2"
    if model_version == "v1.5":
        return "general"
    
def gethash(data:str) -> str: 
    return hashlib.md5(data.encode()).hexdigest()

def appendText(role, content, text):
    # "role": "system","user","assistant"
    # text: [{"role": "system", "content": ""},...]
    # 将对话内容追加到text列表中
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

def getlength(text): # 获取对话长度
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

# 根据消息类型创建会话ID
def get_session_id(event):
    if isinstance(event, PrivateMessageEvent):
        return "private_" + str(event.user_id)
    if group_public:
        return event.get_session_id().replace(str(event.user_id), "public")
    else:
        return event.get_session_id()
    
def checklen(text): # 修理对话长度
    while (getlength(text) > max_length):
        del text[1]
    return text


help_info = "【帮助信息】\n"

for id, (command, description) in enumerate(commands_lst.items(), start=1):
    help_info += f"{id}. {command}：{description}\n"

help_info += "\n群聊中需要@bot + 指令/对话内容"
