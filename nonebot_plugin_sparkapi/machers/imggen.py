# 事件响应器：AI绘图
from nonebot.adapters.onebot.v11 import MessageEvent as ME, PrivateMessageEvent as PME # type: ignore
from nonebot.adapters.onebot.v11 import Message, MessageSegment as MS # type: ignore

from nonebot.rule import to_me
from nonebot.plugin.on import on_message
from nonebot.params import CommandArg
from nonebot.params import ArgPlainText

from .. import funcs, storage, info
from ..API.ImgGenApi import request_IG

from nonebot import get_plugin_config
from ..config import Config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["image_generation"]
priority = conf.sparkapi_priority+1
maxlength = conf.sparkpai_model_maxlength

async def fl_imggen() -> bool:
    return conf.sparkapi_fl_imggen
rule_imggen = to_me() & funcs.trans_command(command) & fl_imggen
matcher_imggen = on_message(
    rule = rule_imggen,
    priority = priority,
    block = True
)

@matcher_imggen.handle()
async def imggen_handle_function(event: ME, msg: Message = CommandArg()):
    content = msg.extract_plain_text().strip()
    session_id = funcs.get_session_id(event)

    if content : 
        if len(content) > maxlength:
            await matcher_imggen.finish(MS.text(f"输入文字过长：请不要超过{maxlength}字节！"))
        ret = await request_IG(content)
        path = storage.f_image_base64_save(ret, f"{session_id}.png")
        await matcher_imggen.finish(MS.image(path))

@matcher_imggen.got("content",prompt="请输入文字描述\n回复“取消”退出")
async def imggen_got_function(event: ME, content: str = ArgPlainText()):
    if content=="取消":
        await matcher_imggen.finish(MS.text("操作已取消"))
    if len(content) > maxlength:
        await matcher_imggen.finish(MS.text(f"输入文字过长：请不要超过{maxlength}字节！"))
    
    session_id = funcs.get_session_id(event)

    ret = await request_IG(content)
    path = storage.f_image_base64_save(ret, f"{session_id}.png")
    await matcher_imggen.finish(MS.image(path))
