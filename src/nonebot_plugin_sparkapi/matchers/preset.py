from nonebot_plugin_alconna import UniMessage

from ..preset import UserPreset
from ..session import UserSession
from ..utils import IndexParam, ParamOrPrompt, catch_exc, prompt
from .alc import matcher
from .help import get_preset_commands


@matcher.assign("~preset.create")
async def assign_preset_create(
    user_preset: UserPreset,
    title: str = ParamOrPrompt(
        param="title",
        prompt_msg="输入预设名称，回复“取消”以取消创建",
        cancel_msg="已取消创建",
        cancel_check=lambda x: not x.strip(),
    ),
    prompt: str = ParamOrPrompt(
        param="prompt",
        prompt_msg="请输入预设提示词，回复“取消”以取消创建",
        cancel_msg="已取消创建",
        cancel_check=lambda x: not x.strip(),
    ),
) -> None:
    async with catch_exc("预设创建失败"):
        new_preset = user_preset.insert(title, prompt)
    await matcher.finish(f"预设创建成功！\n{new_preset.get_info()}")


@matcher.assign("~preset.delete")
async def assign_preset_delete(
    user_preset: UserPreset,
    index: int = IndexParam(
        prompt_msg="{presets}\n\n输入序号选择预设，回复其他内容取消删除",
        cancel_msg="已取消删除",
        annotation=UserPreset,
    ),
    check: bool = False,
) -> None:
    if not check:
        await prompt(
            f"{user_preset.select(index=index).get_info()}\n\n"
            "确认删除该预设？\n回复“确认”以确认删除，回复其他内容取消删除",
            not_confirm="已取消删除",
        )

    async with catch_exc("删除预设失败"):
        user_preset.delete(index=index)

    await UniMessage.text("预设删除成功！").finish()


@matcher.assign("~preset.set")
async def assign_preset_set(
    user_preset: UserPreset,
    user_session: UserSession,
    index: int = IndexParam(
        prompt_msg="{presets}"
        "\n\n输入序号选择预设，回复其他内容取消设置"
        "\n⚠设置预设将清除当前对话记录",
        cancel_msg="已取消设置",
        annotation=UserPreset,
    ),
) -> None:
    async with catch_exc("设置预设失败"):
        preset = user_preset.select(index=index)
        user_session.set_prompt(preset)

    await UniMessage.text(f"已选择预设：{preset.title}").finish()


@matcher.assign("~preset.show")
async def assign_preset_show(
    user_preset: UserPreset,
    index: int = IndexParam(
        prompt_msg="{presets}\n\n输入序号显示预设内容，回复其他内容取消显示",
        cancel_msg="已取消显示",
        annotation=UserPreset,
    ),
) -> None:
    async with catch_exc("查看预设失败"):
        preset = user_preset.select(index=index)

    await UniMessage.text(preset.get_info()).finish()


@matcher.assign("~preset")
async def assign_preset(user_preset: UserPreset) -> None:
    await UniMessage.text(f"{user_preset.show()}\n\n{get_preset_commands()}").finish()
