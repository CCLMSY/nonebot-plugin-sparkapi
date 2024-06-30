import hashlib

from nonebot.adapters.onebot.v11 import PrivateMessageEvent as PME # type: ignore
from nonebot.rule import command

from .config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)

group_public = conf.sparkapi_fl_group_public
max_length = conf.sparkpai_model_maxlength

# 统一模型版本，获取Spark URL、Domain
def unify_model_version(model_version : str):
    version : str
    if model_version in ["v4.0","4.0","Ultra","ultra","","default"]:
        version = "v4.0"
    elif model_version in ["v3.5","3.5","Max","max"]:
        version = "v3.5"
    elif model_version in ["v3.0","3.0","v3.1","3.1","v3","3","Pro","pro"]:
        version = "v3.0"
    elif model_version in ["v2.0","2.0","v2.1","2.1","v2","2"]:
        version = "v2.0"
    elif model_version in ["v1.0","1.0","v1.1","1.1","v1.5","1.5","v1","1", "Lite","lite"]:
        version = "v1.5"
    else:
        raise ValueError("模型版本输入错误，请检查")
    return version
def get_Spark_url(model_version : str):
    url : str
    if model_version == "v4.0":
        url = "wss://spark-api.xf-yun.com/v4.0/chat"
    elif model_version == "v3.5":
        url = "wss://spark-api.xf-yun.com/v3.5/chat"
    elif model_version == "v3.0":
        url = "wss://spark-api.xf-yun.com/v3.1/chat"
    elif model_version == "v2.0":
        url = "wss://spark-api.xf-yun.com/v2.1/chat"
    elif model_version == "v1.5":
        url = "wss://spark-api.xf-yun.com/v1.1/chat"
    return url
def get_domain(model_version : str):
    domain : str
    if model_version == "v4.0":
        domain = "4.0Ultra"
    elif model_version == "v3.5":
        domain = "generalv3.5"
    elif model_version == "v3.0":
        domain = "generalv3"
    elif model_version == "v2.0":
        domain = "generalv2"
    elif model_version == "v1.5":
        domain = "general"
    return domain
    
# def gethash(data:str) -> str: 
#     return hashlib.md5(data.encode()).hexdigest()
# def get_sid(data:str) -> str:
#     return gethash(data)[-20:]

def appendText(role, content, text):
    # "role": "system","user","assistant"
    # text: [{"role": "system", "content": ""},...]
    # 将对话内容追加到text列表中
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

def checklen(text): # 修理对话长度
    def getlength(text): # 获取对话长度
        length = 0
        for content in text:
            temp = content["content"]
            leng = len(temp)
            length += leng
        return length
    while (getlength(text) > max_length):
        del text[1]
    return text

# 根据消息类型创建会话ID
def get_session_id(event):
    ret = ""
    if isinstance(event, PME):
        ret = "private_" + str(event.user_id)
    elif group_public:
        ret = event.get_session_id().replace(str(event.user_id), "public")
    else:
        ret = event.get_session_id()
    # print(ret)
    return ret

# 将命令列表转化为Rule
def trans_command(cmds: str|list[str]):
    if(isinstance(cmds, str)): 
        cmds = [cmds]
    return command(*cmds)

# 合并两个dict
def merge_dict(dict1, dict2):
    return {**dict1, **dict2}

