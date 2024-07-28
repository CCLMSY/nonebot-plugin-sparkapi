from nonebot.params import ArgPlainText
from nonebot.plugin.on import on_message
from nonebot.rule import command, to_me
from nonebot_plugin_alconna.uniseg import UniMessage

from nonebot_plugin_sparkapi.API.PPTGenApi import request_PPT
from nonebot_plugin_sparkapi.config import conf

command_pptgen = conf.sparkapi_commands["ppt_generation"]
priority = conf.sparkapi_priority + 1
max_length = conf.sparkpai_model_maxlength
fl_notice = conf.sparkapi_fl_notice
fl_group_at = conf.sparkapi_fl_group_at

rule = to_me() & command(command_pptgen)
mathcer_pptgen = on_message(rule=rule, priority=priority, block=True)


@mathcer_pptgen.got("content", prompt="请输入生成PPT内容，回复“取消”取消生成")
async def _(content: str = ArgPlainText()):
    if content == "取消":
        await UniMessage("已取消生成PPT").finish(at_sender=fl_group_at)

    msg = "已收到请求，正在生成中...\n过程大约需要60s，请耐心等待"
    await UniMessage(msg).send(at_sender=fl_group_at)

    try:
        ppt = await request_PPT(content)
    except Exception as e:
        msg = f"PPT生成失败！请联系开发者。\n错误信息：{type(e)}: {e}"
    else:
        msg = f"生成成功！\n复制链接前往浏览器下载：\n{ppt}"

    await UniMessage(msg).finish(at_sender=fl_group_at)
