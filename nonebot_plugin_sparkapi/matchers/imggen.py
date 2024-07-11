from nonebot.adapters.onebot.v11 import MessageEvent as ME
from nonebot.adapters.onebot.v11 import MessageSegment as MS

from nonebot.rule import to_me,command
from nonebot.plugin.on import on_message
from nonebot.params import ArgPlainText

from ..funcs import get_session_id
from ..API.ImgGenApi import request_IG
from pathlib import Path

from ..config import Config
from nonebot import get_plugin_config
conf = get_plugin_config(Config)
command_imggen = conf.sparkapi_commands["image_generation"]
priority = conf.sparkapi_priority+1
max_length = conf.sparkpai_model_maxlength
fl_notice = conf.sparkapi_fl_notice
fl_group_at = conf.sparkapi_fl_group_at

rule = to_me() & command(command_imggen,force_whitespace=True)
mathcer_imggen = on_message(
    rule = rule,
    priority=priority,
    block=True
)

@mathcer_imggen.got("content",prompt="请输入生成图片内容，回复“取消”取消生成")
async def _(event:ME, content=ArgPlainText()):
    session_id = get_session_id(event)
    await mathcer_imggen.send(MS.text("已收到请求，正在生成中...\n过程大约需要30s，请耐心等待"), at_sender=fl_group_at)
    if content == "取消":
        await mathcer_imggen.finish(MS.text("已取消生成图片"), at_sender=fl_group_at)
    try:
        img = await request_IG(session_id,content)
    except Exception as e:
        await mathcer_imggen.finish(MS.text(f"图片生成失败！请联系开发者。\n错误信息：{type(e)}:{e}"), at_sender=fl_group_at)
    else:
        if isinstance(img,Path):
            await mathcer_imggen.finish(MS.image(img))
        else:
            await mathcer_imggen.finish(MS.text(f"图片生成失败！请联系开发者。\n错误信息：{img}"), at_sender=fl_group_at)