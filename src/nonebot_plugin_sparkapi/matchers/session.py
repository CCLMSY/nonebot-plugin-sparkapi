from nonebot_plugin_alconna import UniMessage

from ..session import UserSession
from ..utils import IndexParam, ParamOrPrompt, catch_exc, prompt
from .alc import matcher
from .help import get_session_commands


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
    async with catch_exc("会话保存失败"):
        user_session.save_current(title)
    await matcher.finish(f"会话保存成功！\n{user_session.show()}")


@matcher.assign("~session.load")
async def assign_session_load(
    user_session: UserSession,
    index: int = IndexParam(
        prompt_msg="{sessions}\n\n输入序号选择会话，回复其他内容取消加载",
        cancel_msg="已取消加载",
        annotation=UserSession,
    ),
    check: bool = False,
) -> None:
    if not check:
        await prompt(
            f"{user_session.select(index).get_info()}\n\n"
            "确认加载该会话？\n回复“确认”以确认加载，回复其他内容取消加载",
            not_confirm="已取消加载",
        )

    async with catch_exc("会话加载失败"):
        user_session.load_session(index)
    await matcher.finish(f"会话加载成功！\n{user_session.current.get_info()}")


@matcher.assign("~session.show")
async def assign_session_show(
    user_session: UserSession,
    index: int = IndexParam(
        prompt_msg="{sessions}\n\n输入序号显示会话内容，回复其他内容取消显示",
        cancel_msg="已取消显示",
        annotation=UserSession,
    ),
) -> None:
    async with catch_exc("会话显示失败"):
        session = user_session.select(index)
    await UniMessage.text(session.get_info()).finish()


@matcher.assign("~session.delete")
async def assign_session_delete(
    user_session: UserSession,
    index: int = IndexParam(
        prompt_msg="{sessions}\n\n输入序号选择会话，回复其他内容取消删除",
        cancel_msg="已取消删除",
        annotation=UserSession,
    ),
    check: bool = False,
) -> None:
    if not check:
        await prompt(
            f"{user_session.select(index).get_info()}\n\n"
            "确认删除该会话？\n回复“确认”以确认删除，回复其他内容取消删除",
            not_confirm="已取消删除",
        )

    async with catch_exc("会话删除失败"):
        user_session.delete(index)
    await UniMessage.text("会话删除成功！").finish()


@matcher.assign("~session.rollback")
async def assign_session_rollback(user_session: UserSession) -> None:
    async with catch_exc("会话回滚失败"):
        user_session.rollback()
    await matcher.finish(f"会话回滚成功！\n{user_session.current.get_info()}")


@matcher.assign("~session")
async def assign_session(user_session: UserSession) -> None:
    await UniMessage.text(f"{user_session.show()}\n\n{get_session_commands()}").finish()
