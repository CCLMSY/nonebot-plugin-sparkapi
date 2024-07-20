from nonebot.params import ArgPlainText
from nonebot.plugin.on import on_message
from nonebot.rule import command, to_me
from nonebot_plugin_alconna.uniseg import Image, Text, UniMessage

from nonebot_plugin_sparkapi.API.ImgGenApi import request_IG
from nonebot_plugin_sparkapi.config import conf
from nonebot_plugin_sparkapi.funcs import SessionID

command_imggen = conf.sparkapi_commands["image_generation"]
priority = conf.sparkapi_priority + 1
max_length = conf.sparkpai_model_maxlength
fl_notice = conf.sparkapi_fl_notice
fl_group_at = conf.sparkapi_fl_group_at

rule = to_me() & command(command_imggen, force_whitespace=True)
mathcer_imggen = on_message(rule=rule, priority=priority, block=True)


@mathcer_imggen.got("content", prompt="请输入生成图片内容，回复“取消”取消生成")
async def _(session_id: SessionID, content=ArgPlainText()):
    if content == "取消":
        await UniMessage("已取消生成图片").finish(at_sender=fl_group_at)

    msg: UniMessage[Text] | UniMessage[Image]

    msg = UniMessage("已收到请求，正在生成中...\n过程大约需要30s，请耐心等待")
    await msg.send(at_sender=fl_group_at)

    try:
        img = await request_IG(session_id, content)
    except Exception as e:
        msg = UniMessage(f"图片生成失败！请联系开发者。\n错误信息：{type(e)}: {e}")
    else:
        msg = UniMessage.image(raw=img.read_bytes())

    await msg.finish(at_sender=fl_group_at)
