from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.rule import to_me,command
from nonebot.plugin.on import on_message
from nonebot.params import ArgPlainText

from ..API.PPTGenApi import request_PPT

from ..config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
command_pptgen = conf.sparkapi_commands["ppt_generation"]
priority = conf.sparkapi_priority+1
max_length = conf.sparkpai_model_maxlength
fl_notice = conf.sparkapi_fl_notice
fl_group_at = conf.sparkapi_fl_group_at

rule = to_me() & command(command_pptgen)
mathcer_pptgen = on_message(
    rule = rule,
    priority=priority,
    block=True
)

@mathcer_pptgen.got("content",prompt="请输入生成PPT内容，回复“取消”取消生成")
async def _(content=ArgPlainText()):
    if content == "取消":
        await mathcer_pptgen.finish(MS.text("已取消生成PPT"), at_sender=fl_group_at)
    await mathcer_pptgen.send(MS.text("已收到请求，正在生成中...\n过程大约需要60s，请耐心等待"), at_sender=fl_group_at)
    try:
        ppt = await request_PPT(content)
    except Exception as e:
        await mathcer_pptgen.finish(MS.text(f"PPT生成失败！请联系开发者。\n错误信息：{type(e)}:{e}"), at_sender=fl_group_at)
    else:
        await mathcer_pptgen.finish(MS.text(f"生成成功！\n复制链接前往浏览器下载：{ppt}"), at_sender=fl_group_at)
