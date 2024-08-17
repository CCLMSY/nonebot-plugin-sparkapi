from nonebot.params import ArgPlainText
from nonebot.plugin.on import on_command
from nonebot.rule import to_me

from nonebot_plugin_sparkapi.API.PPTGenApi import request_PPT
from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import solve_at

command_pptgen = conf.sparkapi_commands["ppt_generation"]
priority = conf.sparkapi_priority + 1

mathcer_pptgen = on_command(command_pptgen, rule=to_me(), priority=priority, block=True)


@mathcer_pptgen.got("content", prompt="请输入生成PPT内容，回复“取消”取消生成")
async def _(content: str = ArgPlainText()):
    if content == "取消":
        await solve_at("已取消生成PPT").finish()

    msg = "已收到请求，正在生成中...\n过程大约需要60s，请耐心等待"
    await solve_at(msg).send()

    try:
        ppt = await request_PPT(content)
    except Exception as e:
        msg = f"PPT生成失败！请联系开发者。\n错误信息：{type(e)}: {e}"
    else:
        msg = f"生成成功！\n复制链接前往浏览器下载：\n{ppt}"

    await solve_at(msg).finish()
