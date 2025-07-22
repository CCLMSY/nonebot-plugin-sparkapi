import json
from typing import Annotated, Literal
from typing_extensions import Self

from nonebot.compat import model_dump, type_validate_python
from nonebot.params import Depends
from pydantic import BaseModel, Field

from .config import DATA_PATH, conf
from .preset import Preset, preset_assistant
from .utils import SessionID, format_time

Role = Literal["system", "assistant", "user"]


class SessionContent(BaseModel):
    role: Role
    content: str

    def dump_json(self) -> str:
        return json.dumps({"role": self.role, "content": self.content})


class Session(BaseModel):
    title: str
    time: str
    system: str
    content: list[SessionContent]

    @classmethod
    def from_preset(cls, preset: Preset = preset_assistant) -> Self:
        return cls(
            title=preset.title,
            time=format_time(),
            system=preset.content,
            content=[],
        )

    def _calc_content_length(self) -> int:
        return len(self.system) + 15 + sum(len(msg.dump_json()) for msg in self.content)

    def check_length(self) -> None:
        while (
            self._calc_content_length() > conf.maxlength * 1.25
            and len(self.content) > 2
        ):
            self.content.pop(1)

    def display_content(self, pref_len: int) -> str:
        pref_len += 15 + len(self.system)
        conv = {"user": "User", "assistant": "Bot"}
        result: list[str] = []
        for msg in self.content[::-1]:
            line = f"{conv[msg.role]}: {msg.content}"
            pref_len += len(line)
            if pref_len >= 4500:
                result.append("...")
                break
            result.append(line)
        result.append(f"System: {self.system}")
        result.append("【会话内容】")
        return "\n".join(result[::-1])

    def get_info(self) -> str:
        info = "【会话信息】\n"
        info += f"会话名称：{self.title}\n"
        info += f"更新时间：{self.time}\n\n"
        info += self.display_content(len(info))
        return info

    def set_prompt(self, preset: Preset) -> None:
        self.system = preset.content
        self.check_length()

    def add_msg(self, role: Role, content: str) -> None:
        """追加消息"""
        self.content.append(SessionContent(role=role, content=content))
        self.check_length()

    def get_content(self) -> list[SessionContent]:
        return [SessionContent(role="system", content=self.system), *self.content]

    def rollback(self) -> None:
        if not self.content:
            raise Exception("当前会话没有对话记录")

        self.content.pop()
        while self.content and self.content[-1].role != "assistant":
            self.content.pop()


def _check_session_file(session_id: str):
    user_path = DATA_PATH / session_id
    user_path.mkdir(parents=True, exist_ok=True)

    sessions_file = user_path / "sessions.json"
    if not sessions_file.exists():
        with sessions_file.open("w", encoding="utf-8") as file:
            json.dump({"session_id": session_id}, file, ensure_ascii=False, indent=2)
    return sessions_file


class UserSessionData(BaseModel):
    session_id: str
    current: Session = Field(default_factory=Session.from_preset)
    saved: list[Session] = Field(default_factory=list)

    @classmethod
    def load(cls, session_id: str) -> Self:
        fp = _check_session_file(session_id)
        with fp.open("r+", encoding="utf-8") as f:
            data = json.load(f)
        return type_validate_python(cls, data)

    def save(self) -> None:
        fp = _check_session_file(self.session_id)
        with fp.open("w+", encoding="utf-8") as file:
            json.dump(model_dump(self), file, ensure_ascii=False, indent=2)

    def add_msg(self, role: Role, content: str) -> None:
        self.current.add_msg(role, content)

    def set_prompt(self, preset: Preset) -> None:
        self.current = Session.from_preset(preset)
        self.save()

    def clear_current(self) -> None:
        self.current = Session.from_preset()
        self.save()

    def save_current(self, title: str, index: int = -1) -> None:
        session = Session(
            title=title,
            time=format_time(),
            system=self.current.system,
            content=self.current.content[:],
        )
        if index >= 0:
            self.saved.insert(index, session)
        else:
            self.saved.append(session)
        self.save()

    def load_session(self, index: int) -> None:
        session = self.select(index)
        self.current = Session(
            title=session.title,
            time=format_time(),
            system=session.system,
            content=session.content[:],
        )
        self.save()

    def select(self, index: int) -> Session:
        return self.saved[index - 1]

    def delete(self, index: int) -> None:
        del self.saved[index - 1]
        self.save()

    def show(self) -> str:
        text = "💫会话列表\n"
        text += "\n".join(f"{i}. {s.title}" for i, s in enumerate(self.saved, 1))
        return text

    def rollback(self) -> None:
        self.current.rollback()

    def check_index(self, index: int) -> str | None:
        if index <= 0 or index > len(self.saved):
            return f"会话序号 {index} 不存在"
        return None


async def _get_user_session(session_id: SessionID):
    return UserSessionData.load(session_id)


UserSession = Annotated[UserSessionData, Depends(_get_user_session)]
