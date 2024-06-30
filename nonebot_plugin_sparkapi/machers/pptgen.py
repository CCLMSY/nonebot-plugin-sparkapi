# 事件响应器：AI生成PPT
from nonebot.adapters.onebot.v11 import MessageEvent as ME, PrivateMessageEvent as PME # type: ignore
from nonebot.adapters.onebot.v11 import Message, MessageSegment as MS # type: ignore

from nonebot.rule import to_me
from nonebot.plugin.on import on_message
from nonebot.params import CommandArg
from nonebot.params import ArgPlainText

from .. import funcs, storage, info
from ..API.PPTGenApi import request_IP

from nonebot import get_plugin_config
from ..config import Config
conf = get_plugin_config(Config)
command = conf.sparkapi_commands["ppt_generation"]
priority = conf.sparkapi_priority+1
maxlength = conf.sparkpai_model_maxlength

async def fl_pptgen() -> bool:
    return conf.sparkapi_fl_pptgen
rule_pptgen = to_me() & funcs.trans_command(command) & fl_pptgen
matcher_pptgen = on_message(
    rule = rule_pptgen,
    priority = priority,
    block = True
)

@matcher_pptgen.handle()
async def pptgen_handle_function(event: ME, msg: Message = CommandArg()):
    content = msg.extract_plain_text().strip()
    
    if content:
        if len(content) > maxlength:
            await matcher_pptgen.finish(MS.text(f"输入文字过长：请不要超过{maxlength}字节！"))
        ret = await request_IP(content)
        await matcher_pptgen.finish(MS.text("点击链接下载："+ret))
        
@matcher_pptgen.got("content",prompt="请输入文字描述\n回复“取消”退出")
async def pptgen_got_function(event: ME, content: str = ArgPlainText()):
    if content=="取消":
        await matcher_pptgen.finish(MS.text("操作已取消"))
    if len(content) > maxlength:
        await matcher_pptgen.finish(MS.text(f"输入文字过长：请不要超过{maxlength}字节！"))
    
    ret = await request_IP(content)
    await matcher_pptgen.finish(MS.text("点击链接下载："+ret))
