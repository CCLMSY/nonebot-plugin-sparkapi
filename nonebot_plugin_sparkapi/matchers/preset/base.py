import json
from datetime import datetime
from pathlib import Path
from typing import Any

from nonebot import get_driver
from nonebot.plugin.on import CommandGroup
from nonebot.rule import to_me

from nonebot_plugin_sparkapi.config import DATA_PATH, conf
from nonebot_plugin_sparkapi.funcs import SessionID as SessionID


# 类定义
class Preset:
    title: str
    time: str
    content: dict[str, str]

    def __init__(
        self,
        title: str = "",
        prompt: str = "",
        time: str = "",
        preset_dict: dict[str, Any] | None = None,
    ):
        if preset_dict:
            self.title = preset_dict["title"]
            self.time = preset_dict["time"]
            self.content = preset_dict["content"]
        else:
            self.title = title
            self.time = time if time else get_time()
            self.content = {"role": "system", "content": prompt}

    def __getitem__(self, key):
        return getattr(self, key)

    def to_dict(self) -> dict:
        return {"title": self.title, "time": self.time, "content": self.content}

    def get_info(self):
        info = "【预设信息】\n"
        info += f"预设名称：{self.title}\n"
        info += f"更新时间：{self.time}\n"
        info += f"预设提示词：{self.content['content']}"
        return info


def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 在用户预设列表的index位置插入一个新的预设
def preset_insert(session_id: str, title: str, prompt: str, index: int = -1):
    presets = presets_load(session_id)
    new_preset = Preset(title, prompt)
    if index >= 0:
        presets.insert(index, new_preset)
    else:
        presets.append(new_preset)
    presets_save(session_id, presets)


# 删除用户预设列表中的指定名称/序号的预设，名称优先、同名全删
def preset_delete(session_id: str, title: str = "", index: int = -1):
    presets = presets_load(session_id)
    if title:
        presets = list(filter(lambda x: x.title != title, presets))
    elif index >= 0:
        del presets[index]
    else:
        raise ValueError("title和index至少要有一项")
    presets_save(session_id, presets)


# 选择用户预设列表中的指定名称/序号的预设，名称优先、选第一个
def preset_select(session_id: str, title: str = "", index: int = -1) -> Preset:
    presets = presets_load(session_id)
    if title:
        ret = list(filter(lambda x: x.title == title, presets))
        if ret:
            return ret[0]
        else:
            raise ValueError(f"找不到标题为“{title}”的预设")
    else:
        return presets[index]


# 检查用户预设文件是否存在，不存在则创建
def check_presets_file(session_id: str) -> Path:
    user_path = DATA_PATH / session_id
    user_path.mkdir(parents=True, exist_ok=True)
    presets_file = user_path / "presets.json"
    if not presets_file.exists():
        presets = presets_to_json(presets_default)
        with presets_file.open("w", encoding="utf-8") as f:
            json.dump(presets, f, ensure_ascii=False, indent=4)
    return presets_file


# 读取用户预设文件
def presets_load(session_id: str) -> list[Preset]:
    presets_file = check_presets_file(session_id)
    with open(presets_file, "r", encoding="utf-8") as f:
        presets_json = json.load(f)
        return json_to_presets(presets_json)


# 覆盖保存用户预设文件
def presets_save(session_id: str, presets: list[Preset]):
    presets_file = check_presets_file(session_id)
    presets_json = presets_to_json(presets)
    with presets_file.open("w", encoding="utf-8") as f:
        json.dump(presets_json, f, ensure_ascii=False, indent=4)


def json_to_presets(presets_json: list[dict[str, Any]]) -> list[Preset]:
    return [Preset(preset_dict=p) for p in presets_json]


def presets_to_json(presets: list[Preset]) -> list[dict]:
    return [p.to_dict() for p in presets]


bot_name = conf.sparkapi_bot_name.strip()
prompt_assistant = f"在接下来的对话中，你的名字叫 {bot_name}。" if bot_name else ""
preset_assistant = Preset("[默认]智能助手", prompt_assistant, "0000-00-00 00:00:00")

prompt_libai = "你现在扮演李白，你豪情万丈，狂放不羁；接下来请用李白的口吻和用户对话。"
preset_libai = Preset("李白", prompt_libai, "0000-00-00 00:00:00")

# 默认预设列表
presets_default = [preset_assistant, preset_libai]

commands = conf.sparkapi_commands
commands_info = conf.sparkapi_commands_info


def get_preset_list(session_id):
    presets = presets_load(session_id)
    ret = "💫预设列表"
    for i, p in enumerate(presets):
        ret += f"\n{i}. {p.title}"
    return ret


botconf = get_driver().config
command_start = list(botconf.command_start)[0]
command_sep = list(botconf.command_sep)[0]


def get_preset_commands():
    cmd = command_start + commands["preset"]

    ret = "💫操作"
    ret += f'\n{cmd}：{commands_info["preset"]}'  # 查看预设列表
    for key in {"preset_create", "preset_set", "preset_show", "preset_delete"}:
        ret += f"\n{command_start+commands['preset']+command_sep+commands[key]}：{commands_info[key]}"
    return ret


# 命令组
cmd_preset = CommandGroup(
    cmd=commands["preset"],
    rule=to_me(),
    priority=conf.sparkapi_priority + 1,
    prefix_aliases=True,
    block=True,
)
