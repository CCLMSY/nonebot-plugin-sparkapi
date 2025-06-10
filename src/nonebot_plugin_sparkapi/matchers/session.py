from nonebot import logger
from nonebot_plugin_alconna import UniMessage

from ..session import UserSession
from ..utils import IndexParam, ParamOrPrompt, prompt
from .alc import matcher


@matcher.assign("~session.save")
async def assign_session_save(
    user_session: UserSession,
    title: str = ParamOrPrompt(
        param="title",
        prompt_msg="输入会话名称，回复“取消”以取消保存",
        cancel_msg="已取消保存",
        cancel_check=lambda x: not x.strip(),
    ),
) -> None:
    try:
        user_session.save_current(title)
    except Exception as e:
        msg = f"保存失败！请联系开发者。\n错误信息：{type(e)}: {e}"
        logger.exception("会话保存失败")
    else:
        msg = f"会话保存成功！\n{user_session.show()}"
    await UniMessage.text(msg).finish()


@matcher.assign("~session.load")
async def assign_session_load(
    user_session: UserSession,
    index: int = IndexParam(
        prompt_msg="{sessions}\n\n输入序号选择会话，回复其他内容取消加载",
        cancel_msg="已取消加载",
    ),
    yes: bool = False,
) -> None:
    if err_msg := user_session.check_index(index):
        await UniMessage.text(err_msg).finish()

    if not yes:
        await prompt(
            f"{user_session.select(index).get_info()}\n\n"
            "确认加载该会话？\n回复“确认”以确认加载，回复其他内容取消加载",
            not_confirm="已取消加载",
        )

    try:
        user_session.load_session(index)
    except Exception as e:
        msg = f"加载失败！请联系开发者。\n错误信息：{type(e)}: {e}"
        logger.exception("会话加载失败")
    else:
        msg = "会话加载成功！\n" + user_session.current.get_info()

    await UniMessage.text(msg).finish()


@matcher.assign("~session.show")
async def assign_session_show(
    user_session: UserSession,
    index: int = IndexParam(
        prompt_msg="{sessions}\n\n输入序号显示会话内容，回复其他内容取消显示",
        cancel_msg="已取消显示",
    ),
) -> None:
    if err_msg := user_session.check_index(index):
        await UniMessage.text(err_msg).finish()

    session = user_session.select(index)
    await UniMessage.text(session.get_info()).finish()


@matcher.assign("~session.delete")
async def assign_session_delete(
    user_session: UserSession,
    index: int = IndexParam(
        prompt_msg="{sessions}\n\n输入序号选择会话，回复其他内容取消删除",
        cancel_msg="已取消删除",
    ),
    yes: bool = False,
) -> None:
    if err_msg := user_session.check_index(index):
        await UniMessage.text(err_msg).finish()

    if not yes:
        await prompt(
            f"{user_session.select(index).get_info()}\n\n"
            "确认删除该会话？\n回复“确认”以确认删除，回复其他内容取消删除",
            not_confirm="已取消删除",
        )

    try:
        user_session.delete(index)
    except Exception as e:
        msg = f"删除失败！请联系开发者。\n错误信息：{type(e)}: {e}"
        logger.exception("会话删除失败")
    else:
        msg = "会话删除成功！"

    await UniMessage.text(msg).finish()
