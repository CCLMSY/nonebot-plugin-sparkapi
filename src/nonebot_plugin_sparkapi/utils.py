import contextlib
from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, Literal, cast, overload

import nonebot_plugin_waiter.unimsg as waiter
from nonebot import logger
from nonebot.matcher import current_event
from nonebot.params import Depends
from nonebot_plugin_alconna import Arparma, MsgTarget, UniMessage, get_target
from nonebot_plugin_alconna.uniseg import Receipt
from nonebot_plugin_session import EventSession, SessionIdType

from .config import conf

if TYPE_CHECKING:
    from .preset import UserPresetData
    from .session import UserSessionData

ModelVersion = Literal["v4.0", "max-32k", "v3.5", "128k", "v3.0", "v1.5"]


@dataclass
class SparkModelInfo:
    version: ModelVersion
    url: str
    domain: str


spark_model_info: dict[ModelVersion, SparkModelInfo] = {
    info.version: info
    for info in [
        SparkModelInfo("v4.0", "wss://spark-api.xf-yun.com/v4.0/chat", "4.0Ultra"),
        SparkModelInfo("max-32k", "wss://spark-api.xf-yun.com/chat/max-32k", "max-32k"),
        SparkModelInfo("v3.5", "wss://spark-api.xf-yun.com/v3.5/chat", "generalv3.5"),
        SparkModelInfo("128k", "wss://spark-api.xf-yun.com/chat/pro-128k", "pro-128k"),
        SparkModelInfo("v3.0", "wss://spark-api.xf-yun.com/v3.1/chat", "generalv3"),
        SparkModelInfo("v1.5", "wss://spark-api.xf-yun.com/v1.1/chat", "lite"),
    ]
}


def get_model_info(model_version: str) -> SparkModelInfo:
    model_version = model_version.lstrip("v").lower()
    version: ModelVersion
    if model_version in {"4.0", "ultra", "", "default"}:
        version = "v4.0"
    elif model_version in {"max-32k", "32k"}:
        version = "max-32k"
    elif model_version in {"3.5", "max"}:
        version = "v3.5"
    elif model_version in {"128k"}:
        version = "128k"
    elif model_version in {"3.0", "3.1", "3", "pro"}:
        version = "v3.0"
    # elif model_version in {"2.0", "2.1", "2"}:
    #     version = "v2.0"
    elif model_version in {"1.0", "1.1", "1.5", "1", "lite"}:
        version = "v1.5"
    else:
        raise ValueError("模型版本输入错误，请检查")
    return spark_model_info[version]


def format_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _session_id(session: EventSession, target: MsgTarget) -> str:
    match (conf.fl_interflow, conf.fl_group_public, target.private):
        case (_, True, False):
            flag = SessionIdType.GROUP
        case (_, _, True) | (True, False, _):
            flag = SessionIdType.USER
        case _:
            flag = SessionIdType.GROUP_USER

    return session.get_id(flag).replace(" ", "_")


SessionID = Annotated[str, Depends(_session_id)]


def check_at(msg: str | UniMessage) -> UniMessage:
    if isinstance(msg, str):
        msg = UniMessage.text(msg)
    if conf.fl_group_at:
        try:
            event = current_event.get()
        except LookupError:
            event = None
        if event and not get_target(event).private:
            msg = UniMessage.at(event.get_user_id()) + msg
    return msg


@overload
async def prompt(msg: str) -> str | None: ...
@overload
async def prompt(
    msg: str,
    *,
    on_cancel: str | None = None,
    cancel_check: Callable[[str], bool] | None = None,
) -> str: ...
@overload
async def prompt(msg: str, *, not_confirm: str | None = None) -> str: ...


async def prompt(
    msg: str,
    *,
    on_cancel: str | None = None,
    cancel_check: Callable[[str], bool] | None = None,
    not_confirm: str | None = None,
) -> str | None:
    result = await waiter.prompt(check_at(msg))
    if result is None or not (text := result.extract_plain_text().strip()):
        return None
    if on_cancel is not None and (
        (cancel_check is not None and cancel_check(text)) or text == "取消"
    ):
        await check_at(on_cancel).finish()
    if not_confirm is not None and text != "确认":
        await check_at(not_confirm).finish()
    return text


def ParamOrPrompt(  # noqa: N802
    param: str,
    prompt_msg: str,
    cancel_msg: str,
    cancel_check: Callable[[str], bool] | None = None,
) -> Any:
    from .preset import UserPresetData
    from .session import UserSessionData

    async def dependency(arp: Arparma, session_id: SessionID) -> str:
        arg: UniMessage | str | None = arp.all_matched_args.get(param)
        if arg is None:
            msg = prompt_msg
            if "{presets}" in msg:
                msg = msg.replace("{presets}", UserPresetData.load(session_id).show())
            if "{sessions}" in msg:
                msg = msg.replace("{sessions}", UserSessionData.load(session_id).show())
            arg = await prompt(msg, on_cancel=cancel_msg, cancel_check=cancel_check)
        elif isinstance(arg, UniMessage):
            arg = arg.extract_plain_text().strip()
        return arg

    return Depends(dependency)


def IndexParam(  # noqa: N802
    prompt_msg: str,
    cancel_msg: str,
    annotation: Any,  # UserPreset | UserSession
) -> Any:
    async def dependency(
        data: annotation,  # pyright: ignore[reportInvalidTypeForm]
        index: str = ParamOrPrompt(
            "index",
            prompt_msg=prompt_msg,
            cancel_msg=cancel_msg,
            cancel_check=lambda x: not x.isdigit(),
        ),
    ) -> int:
        try:
            idx = int(index)
        except ValueError:
            await check_at("输入序号不合法").finish()

        if err_msg := cast("UserPresetData | UserSessionData", data).check_index(idx):
            await check_at(err_msg).finish()

        return idx

    return Depends(dependency)


@contextlib.asynccontextmanager
async def catch_exc(
    msg: str,
    receipt: Receipt | None = None,
) -> AsyncGenerator[None, None]:
    try:
        yield
    except Exception as exc:
        logger.opt(exception=exc).warning(msg)
        text = f"{msg}\n\n错误信息: {type(exc)}\n{exc}"
        await UniMessage.text(text).finish()
    finally:
        if receipt and receipt.recallable:
            with contextlib.suppress(Exception):
                await receipt.recall()
