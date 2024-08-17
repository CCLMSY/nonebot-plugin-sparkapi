import contextlib
import shutil
from pathlib import Path
from typing import Annotated, Literal

from nonebot.adapters import Event
from nonebot.internal.matcher import current_event
from nonebot.log import logger
from nonebot.params import Depends
from nonebot_plugin_alconna import MsgTarget, UniMessage
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
fl_group_at = conf.sparkapi_fl_group_at


def solve_at(msg: str | None = None) -> UniMessage:
    unimsg = UniMessage(msg) if msg is not None else UniMessage()
    if not fl_group_at:
        return unimsg
    return UniMessage.at(current_event.get().get_user_id()) + unimsg


# 未安装 OneBot 适配器时, 跳过迁移检查
def _migrate_ob11(  # pyright: ignore[reportRedeclaration]
    event: Event, session_id: str
):
    return


with contextlib.suppress(ImportError):
    from nonebot.adapters.onebot.v11 import MessageEvent, PrivateMessageEvent

    OLD_DATA_PATH = Path() / "SparkApi"

    def _ob11_session_id(event: Event) -> str | None:
        """仅适配 OneBot V11 时的 session_id"""

        if not isinstance(event, MessageEvent):
            return None

        session_id = event.get_session_id()
        if fl_interflow:
            if fl_group_public:
                session_id = session_id.replace(event.get_user_id(), "public")
            else:
                session_id = f"private_{event.user_id}"
        else:
            if isinstance(event, PrivateMessageEvent):
                session_id = f"private_{event.user_id}"
            elif fl_group_public:
                session_id = session_id.replace(event.get_user_id(), "public")
        return session_id

    def _migrate_ob11(event: Event, session_id: str) -> None:
        """检测并迁移 OneBot V11 session_id"""
        ob11_session_id = _ob11_session_id(event)
        if ob11_session_id is None:
            return

        ob11_user_fp = OLD_DATA_PATH / ob11_session_id
        if not ob11_user_fp.exists():
            return

        user_fp = OLD_DATA_PATH / session_id
        user_fp.mkdir(parents=True, exist_ok=True)
        session_fp = ob11_user_fp / "sessions.json"
        preset_fp = ob11_user_fp / "presets.json"

        log = logger.opt(colors=True)
        log.info(f"正在迁移 <y>{event.get_user_id()}</y> 的用户数据")

        if session_fp.exists():
            target = user_fp / "sessions.json"
            log.info(f"  <c>{session_fp}</c> -> <c>{target}</c>")
            session_fp.rename(target)

        if preset_fp.exists():
            target = user_fp / "presets.json"
            log.info(f"  <c>{preset_fp}</c> -> <c>{target}</c>")
            preset_fp.rename(target)

        shutil.rmtree(ob11_user_fp)
        log.success(f"<y>{event.get_user_id()}</y> 的用户数据迁移完成")


def _session_id(event: Event, session: EventSession, target: MsgTarget) -> str:
    match (fl_interflow, fl_group_public, target.private):
        case (_, True, False):
            flag = SessionIdType.GROUP
        case (_, _, True) | (True, False, _):
            flag = SessionIdType.USER
        case _:
            flag = SessionIdType.GROUP_USER

    session_id = session.get_id(flag)
    _migrate_ob11(event, session_id)
    return session_id


SessionID = Annotated[str, Depends(_session_id)]
