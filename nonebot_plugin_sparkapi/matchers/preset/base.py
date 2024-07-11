from datetime import datetime
import json
from pathlib import Path

from ...funcs import get_session_id

# 类定义
class preset:
    def __init__(self, title:str="", prompt:str="", time:str="", preset_dict:dict={}):
        if preset_dict:
            self.title = preset_dict["title"]
            self.time = preset_dict["time"]
            self.content = preset_dict["content"]
        else:
            self.title = title
            self.time = time if time else get_time()
            self.content = {
                'role': 'system',
                'content': prompt
            }
    def __getitem__(self, key):
        return getattr(self, key)
    def to_dict(self)->dict:
        return {
            "title" : self.title,   
            "time" : self.time,
            "content" : self.content
        }
    def get_info(self):
        info="【预设信息】"
        info+=f"\n预设名称：{self.title}"
        info+=f"\n更新时间：{self.time}"
        info+=f"\n预设提示词：{self.content['content']}"
        return info

def get_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

PATH = Path(".") / "SparkApi"

# 在用户预设列表的index位置插入一个新的预设
def preset_insert(session_id:str, title:str, prompt:str, index:int = -1):
    check_presets_file(session_id)
    presets = presets_load(session_id)
    new_preset = preset(title, prompt)
    if index>=0:
        presets.insert(index, new_preset)
    else:
        presets.append(new_preset)
    presets_save(session_id, presets)

# 删除用户预设列表中的指定名称/序号的预设，名称优先、同名全删
def preset_delete(session_id:str, title:str="", index:int=-1):
    check_presets_file(session_id)
    presets = presets_load(session_id)
    if title:
        presets = list(filter(lambda x: x.title!=title, presets))
    elif index>=0:
        del presets[index]
    else:
        raise ValueError("title和index至少要有一项")
    presets_save(session_id, presets)

# 选择用户预设列表中的指定名称/序号的预设，名称优先、选第一个
def preset_select(session_id:str, title:str="", index:int=-1)->preset:
    check_presets_file(session_id)
    presets = presets_load(session_id)
    if title:
        ret = list(filter(lambda x: x.title==title, presets))
        if ret:
            return ret[0]
        else:
            raise ValueError(f"找不到标题为“{title}”的预设")
    else:
        return presets[index]

# 检查用户预设文件是否存在，不存在则创建
def check_presets_file(session_id:str=""):
    user_path = PATH / session_id
    if not user_path.exists():
        user_path.mkdir(parents=True)
    presets_file = user_path / "presets.json"
    if not presets_file.exists():
        presets = presets_to_json(presets_default)
        with open(presets_file, "w") as f:
            json.dump(presets, f, ensure_ascii=False, indent=4)

# 读取用户预设文件
def presets_load(session_id:str)->list[preset]:
    check_presets_file(session_id)
    user_path = PATH / session_id
    presets_file = user_path / "presets.json"
    with open(presets_file, "r") as f:
        presets_json = json.load(f)
        presets = json_to_presets(presets_json)
        return presets

# 覆盖保存用户预设文件
def presets_save(session_id:str, presets:list[preset]):
    check_presets_file(session_id)
    user_path = PATH / session_id
    presets_file = user_path / "presets.json"
    with open(presets_file, "w") as f:
        presets_json = presets_to_json(presets)
        json.dump(presets_json, f, ensure_ascii=False, indent=4)

def json_to_presets(presets_json:list[dict])->list[preset]:
    return [preset(preset_dict=p) for p in presets_json]

def presets_to_json(presets:list[preset])->list[dict]:
    return [p.to_dict() for p in presets]

# 默认预设列表
from ...config import Config
import nonebot as nb
conf = nb.get_plugin_config(Config)

bot_name = conf.sparkapi_bot_name.strip()
prompt_name = f'在接下来的对话中，你的名字叫 {bot_name}。' if bot_name else ''

prompt_assistant = prompt_name if bot_name else ''
preset_assistant = preset("[默认]智能助手", prompt_assistant, "0000-00-00 00:00:00")
prompt_libai = '你现在扮演李白，你豪情万丈，狂放不羁；接下来请用李白的口吻和用户对话。'
preset_libai = preset("李白", prompt_libai, "0000-00-00 00:00:00")

presets_default = [preset_assistant, preset_libai]

commands = conf.sparkapi_commands
commands_info = conf.sparkapi_commands_info
    
def get_preset_list(session_id):
    presets = presets_load(session_id)
    ret = "💫预设列表"
    for i, p in enumerate(presets):
        ret += f"\n{i}. {p.title}"
    return ret

botconf = nb.get_driver().config
command_start = list(botconf.command_start)[0]
command_sep = list(botconf.command_sep)[0]
def get_preset_commands():
    ret='💫操作'
    ret+=f'\n{command_start+commands["preset"]}：{commands_info["preset"]}' # 查看预设列表
    ret+=f'\n{command_start+commands["preset"]+command_sep+commands["preset_create"]}：{commands_info["preset_create"]}' # 创建预设
    ret+=f'\n{command_start+commands["preset"]+command_sep+commands["preset_set"]}：{commands_info["preset_set"]}' # 选择预设
    ret+=f'\n{command_start+commands["preset"]+command_sep+commands["preset_show"]}：{commands_info["preset_show"]}' # 显示预设
    ret+=f'\n{command_start+commands["preset"]+command_sep+commands["preset_delete"]}：{commands_info["preset_delete"]}' # 删除预设
    return ret

# 命令组
from nonebot.plugin.on import CommandGroup
from nonebot.rule import to_me
priority = conf.sparkapi_priority + 1
cmd_preset = CommandGroup(
    cmd = commands["preset"],
    rule = to_me(),
    priority=priority,
    prefix_aliases=True,
    block=True
)

fl_group_at = conf.sparkapi_fl_group_at