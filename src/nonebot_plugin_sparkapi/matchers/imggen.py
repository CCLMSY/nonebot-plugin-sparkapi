import contextlib

from nonebot.exception import ActionFailed
from nonebot.params import ArgPlainText
from nonebot.plugin.on import on_command
from nonebot.rule import to_me

from nonebot_plugin_sparkapi.API.ImgGenApi import request_IG
from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import SessionID, solve_at


mathcer_imggen = on_command(
    conf.sparkapi_commands["image_generation"],
    rule=to_me(),
    priority=conf.sparkapi_priority + 1,
    block=True,
)


@mathcer_imggen.got("content", prompt="请输入生成图片内容，回复“取消”取消生成")
async def _(session_id: SessionID, content=ArgPlainText()):
    if content == "取消":
        await solve_at("已取消生成图片").finish()

    msg = solve_at("已收到请求，正在生成中...\n过程大约需要30s，请耐心等待")
    receipt = await msg.send()

    try:
        img = await request_IG(session_id, content)
    except Exception as e:
        msg = solve_at(f"图片生成失败！请联系开发者。\n错误信息：{type(e)}: {e}")
    else:
        msg = solve_at().image(raw=img.read_bytes())

    if receipt.recallable:
        with contextlib.suppress(ActionFailed):
            await receipt.recall()

    await msg.finish()
