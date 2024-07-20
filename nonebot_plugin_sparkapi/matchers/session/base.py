import json
from datetime import datetime
from pathlib import Path

from nonebot import get_driver

from nonebot_plugin_sparkapi.config import DATA_PATH, conf
from nonebot_plugin_sparkapi.funcs import SessionID as SessionID

from ..preset.base import Preset, preset_assistant

botconf = get_driver().config


# 类定义
class Session:
    title: str
    time: str
    content: list[dict[str, str]]
    length: int

    def __init__(
        self,
        title: str = "",
        content: list[dict[str, str]] = [],
        time: str = "",
        ps: Preset = preset_assistant,
        session_dict: dict = {},
    ):
        if session_dict:
            self.title = session_dict["title"]
            self.time = session_dict["time"]
            self.content, self.length = check_length(session_dict["content"])
        else:
            self.title = title
            self.time = time if time else get_time()
            self.content, self.length = check_length(content)
            self.set_prompt(ps=ps)

    def __getitem__(self, key):
        return getattr(self, key)

    def to_dict(self) -> dict:
        return {"title": self.title, "time": self.time, "content": self.content}

    def get_info(self):
        info = "【会话信息】\n"
        info += f"会话名称：{self.title}\n"
        info += f"更新时间：{self.time}\n\n"
        info += display_content(self.content, len(info))
        return info

    def add_msg(self, role: str, content: str):
        """追加消息"""
        self.content.append(gen_msg(role, content))
        self.content, self.length = check_length(self.content)

    def set_prompt(self, ps: Preset):
        """设置提示词"""
        if not self.content or self.content[0]["role"] != "system":
            self.content.insert(0, gen_msg("system", ps.content["content"]))
        else:
            self.content[0]["content"] = ps.content["content"]
        self.content, self.length = check_length(self.content)


def gen_msg(role: str, content: str):
    return {"role": role, "content": content}


def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


maxlength = conf.sparkpai_model_maxlength


def check_length(content: list[dict]):
    cnt = len(json.dumps(content))
    while cnt > maxlength * 1.25:
        del content[1]
        cnt = len(json.dumps(content))
        if len(content) <= 2:
            break
    return content, cnt


def display_content(content: list[dict], pref_len: int) -> str:
    cnt = 0
    conv = {"user": "User", "assistant": "BOT", "system": "System"}
    ret = [f"{conv[content[0]['role']]}：{content[0]['content']}"]
    for msg in content[::-1]:
        line = f"{conv[msg['role']]}：{msg['content']}"
        cnt += len(line)
        if cnt >= 4500 - pref_len:
            ret.insert(1, "...")
            ret.insert(0, "【会话内容】")
            break
        if msg["role"] == "system":
            ret.insert(0, "【会话内容】")
            break
        ret.insert(1, line)
    return "\n".join(ret)


# 向当前会话追加消息
def add_msg(session_id: str, role: str, content: str):
    sessions = sessions_load(session_id)
    sessions[0].add_msg(role, content)
    sessions_save(session_id, sessions)


def set_prompt(session_id: str, ps: Preset):
    sessions = sessions_load(session_id)
    sessions[0] = Session(ps=ps)
    sessions_save(session_id, sessions)


def clear_current(session_id: str):
    sessions = sessions_load(session_id)
    sessions[0] = Session()
    sessions_save(session_id, sessions)


def session_save(session_id: str, title: str, index: int = -1):
    sessions = sessions_load(session_id)
    current = sessions[0]
    new_session = Session(title, current.content)
    if index >= 0:
        sessions.insert(index, new_session)
    else:
        sessions.append(new_session)
    sessions_save(session_id, sessions)


def session_load(session_id: str, index: int):
    sessions = sessions_load(session_id)
    sessions[0] = sessions[index]
    sessions_save(session_id, sessions)


def session_delete(session_id: str, title: str = "", index: int = -1):
    sessions = sessions_load(session_id)
    if title:
        sessions = list(filter(lambda x: x.title != title, sessions))
    elif index >= 0:
        del sessions[index]
    else:
        raise ValueError("title和index至少要有一项")
    sessions_save(session_id, sessions)


def session_select(session_id: str, title: str = "", index: int = 0) -> Session:
    sessions = sessions_load(session_id)
    if title:
        ret = next((s for s in sessions if s.title == title), None)
        if ret is None:
            raise ValueError(f"找不到标题为“{title}”的会话")
        return ret
    return sessions[index]


def check_sessions_file(session_id: str) -> Path:
    user_path = DATA_PATH / session_id
    user_path.mkdir(parents=True, exist_ok=True)
    sessions_file = user_path / "sessions.json"
    if not sessions_file.exists():
        sessions_json = sessions_to_json([Session()])
        with open(sessions_file, "w", encoding="utf-8") as f:
            json.dump(sessions_json, f, ensure_ascii=False, indent=4)
    return sessions_file


def sessions_load(session_id: str) -> list[Session]:
    sessions_file = check_sessions_file(session_id)
    with open(sessions_file, "r", encoding="utf-8") as f:
        sessions_json = json.load(f)
    sessions = json_to_sessions(sessions_json)
    return sessions


def sessions_save(session_id: str, sessions: list[Session]):
    sessions_file = check_sessions_file(session_id)
    with open(sessions_file, "w", encoding="utf-8") as f:
        sessions_json = sessions_to_json(sessions)
        json.dump(sessions_json, f, ensure_ascii=False, indent=4)


def json_to_sessions(sessions_json: list[dict]) -> list[Session]:
    return [Session(session_dict=s) for s in sessions_json]


def sessions_to_json(sessions: list[Session]) -> list[dict]:
    return [s.to_dict() for s in sessions]


commands = conf.sparkapi_commands
commands_info = conf.sparkapi_commands_info


def get_sessions_list(session_id):
    sessions = sessions_load(session_id)
    ret = "💫会话列表"
    for i, s in enumerate(sessions):
        if i == 0:
            continue
        ret += f"\n{i}. {s.title}"
    return ret


command_start = list(botconf.command_start)[0]
command_sep = list(botconf.command_sep)[0]


def get_session_commands():
    ret = "💫操作"
    ret += f'\n{command_start+commands["session"]}：{commands_info["session"]}'
    for key in {"session_save", "session_load", "session_show", "session_delete"}:
        ret += f"\n{command_start+commands['session']+command_sep+commands[key]}：{commands_info[key]}"
    return ret


# 命令组
from nonebot.plugin.on import CommandGroup
from nonebot.rule import to_me

priority = conf.sparkapi_priority + 1
cmd_session = CommandGroup(
    cmd=commands["session"],
    rule=to_me(),
    priority=priority,
    prefix_aliases=True,
    block=True,
)

fl_group_at = conf.sparkapi_fl_group_at

# #test
# data = [
#     {
#         'role': 'user',
#         'content': '你好'
#     },{
#         'role': 'assistant',
#         'content': '你好，有什么可以帮助你的吗？'
#     }]

# data = session("Title", content=data)
# print(data.get_info())
# data.add_msg('system','这是系统消息')
# print(data.get_info())
