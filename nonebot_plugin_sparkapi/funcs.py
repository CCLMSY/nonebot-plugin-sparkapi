from typing import Annotated, Literal

from nonebot.params import Depends
from nonebot_plugin_alconna import MsgTarget
from nonebot_plugin_session import EventSession, SessionIdType

from .config import conf

group_public = conf.sparkapi_fl_group_public
max_length = conf.sparkpai_model_maxlength

ModelVersion = Literal["v4.0", "v3.5", "v3.0", "v2.0", "v1.5"]


# 统一LLM模型版本，获取Spark URL、Domain
def unify_model_version(model_version: str) -> ModelVersion:
    model_version = model_version.lstrip("v").lower()
    version: ModelVersion
    if model_version in {"4.0", "ultra", "", "default"}:
        version = "v4.0"
    elif model_version in {"3.5", "max"}:
        version = "v3.5"
    elif model_version in {"3.0", "3.1", "3", "pro"}:
        version = "v3.0"
    elif model_version in {"2.0", "2.1", "2"}:
        version = "v2.0"
    elif model_version in {"1.0", "1.1", "1.5", "1", "lite"}:
        version = "v1.5"
    else:
        raise ValueError("模型版本输入错误，请检查")
    return version


def get_Spark_url(model_version: ModelVersion):
    url = {
        "v4.0": "wss://spark-api.xf-yun.com/v4.0/chat",
        "v3.5": "wss://spark-api.xf-yun.com/v3.5/chat",
        "v3.0": "wss://spark-api.xf-yun.com/v3.1/chat",
        "v2.0": "wss://spark-api.xf-yun.com/v2.1/chat",
        "v1.5": "wss://spark-api.xf-yun.com/v1.1/chat",
    }.get(model_version, None)
    if url is None:
        raise ValueError("模型版本输入错误，请检查")
    return url


def get_domain(model_version: ModelVersion):
    domain = {
        "v4.0": "4.0Ultra",
        "v3.5": "generalv3.5",
        "v3.0": "generalv3",
        "v2.0": "generalv2",
        "v1.5": "general",
    }.get(model_version, None)
    if domain is None:
        raise ValueError("模型版本输入错误，请检查")
    return domain


# 根据消息类型创建会话ID
fl_group_public = conf.sparkapi_fl_group_public
fl_interflow = conf.sparkapi_fl_interflow


# def get_session_id(event: ME):
#     session_id = ""
#     if fl_interflow:
#         if fl_group_public:
#             session_id = event.get_session_id().replace(str(event.user_id), "public")
#         else:
#             session_id = f"private_{event.user_id}"
#     else:
#         if isinstance(event, PME):
#             session_id = f"private_{event.user_id}"
#         elif fl_group_public:
#             session_id = event.get_session_id().replace(str(event.user_id), "public")
#         else:
#             session_id = event.get_session_id()
#     return session_id


def _session_id(session: EventSession, target: MsgTarget):
    # XXX: Breaking change
    #      修改了 session_id 的格式，将导致原对话记录丢失
    match (fl_interflow, fl_group_public, target.private):
        case (_, True, False):
            flag = SessionIdType.GROUP
        case (_, _, True) | (True, False, _):
            flag = SessionIdType.USER
        case _:
            flag = SessionIdType.GROUP_USER
    return session.get_id(flag)


SessionID = Annotated[str, Depends(_session_id)]
