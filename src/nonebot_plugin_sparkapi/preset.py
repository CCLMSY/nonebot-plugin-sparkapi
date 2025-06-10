import json
from pathlib import Path
from typing import Annotated, Any
from typing_extensions import Never, Self, overload

from nonebot.compat import model_dump, type_validate_json, type_validate_python
from nonebot.params import Depends
from pydantic import BaseModel

from .config import DATA_PATH, conf
from .utils import SessionID, format_time


class Preset(BaseModel):
    title: str
    time: str
    content: str

    @classmethod
    def from_prompt(cls, title: str, prompt: str, time: str | None = None) -> Self:
        return cls(
            title=title,
            time=time or format_time(),
            content=prompt,
        )

    @classmethod
    def from_dict(cls, preset_dict: dict[str, Any]) -> Self:
        return type_validate_python(cls, preset_dict)

    def to_dict(self) -> dict:
        return model_dump(self)

    def show(self) -> str:
        return (
            f"【预设信息】\n"
            f"预设名称：{self.title}\n"
            f"更新时间：{self.time}\n"
            f"预设提示词：{self.content}"
        )


preset_assistant = Preset.from_prompt(
    "[默认]智能助手",
    (
        f"在接下来的对话中，你的名字叫 {bot_name}。"
        if (bot_name := conf.bot_name.strip())
        else ""
    ),
    "0000-00-00 00:00:00",
)
preset_libai = Preset.from_prompt(
    "李白",
    "你现在扮演李白，你豪情万丈，狂放不羁；接下来请用李白的口吻和用户对话。",
    "0000-00-00 00:00:00",
)

# 默认预设列表
presets_default = [preset_assistant, preset_libai]


def _dump_presets(presets: list[Preset]) -> list[dict[str, Any]]:
    return [model_dump(i) for i in presets]


def _check_preset_file(session_id: str) -> Path:
    user_path = DATA_PATH / session_id
    user_path.mkdir(parents=True, exist_ok=True)

    presets_file = user_path / "presets.json"
    if not presets_file.exists():
        presets_file.write_text(
            json.dumps(_dump_presets(presets_default), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return presets_file


class UserPresetData:
    session_id: str
    presets: list[Preset]

    def __init__(self, session_id: str, presets: list[Preset]) -> None:
        self.session_id = session_id
        self.presets = presets

    @classmethod
    def load(cls, session_id: str) -> Self:
        fp = _check_preset_file(session_id)
        data = type_validate_json(list[Preset], fp.read_text(encoding="utf-8"))
        return cls(session_id, data)

    def save(self) -> None:
        fp = _check_preset_file(self.session_id)
        fp.write_text(
            json.dumps(_dump_presets(self.presets), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def insert(self, title: str, prompt: str, index: int = -1) -> None:
        preset = Preset.from_prompt(title, prompt)
        if index >= 0:
            self.presets.insert(index, preset)
        else:
            self.presets.append(preset)
        self.save()

    @overload
    def delete(self, *, title: str) -> None: ...
    @overload
    def delete(self, *, index: int) -> None: ...
    @overload
    def delete(self) -> Never: ...

    def delete(
        self,
        title: str | None = None,
        index: int | None = None,
    ) -> None:
        if title is not None:
            self.presets = [p for p in self.presets if p.title != title]
        elif index is not None:
            del self.presets[index]
        else:
            raise ValueError("title 和 index 不能同时为 None")
        self.save()

    @overload
    def select(self, *, title: str) -> Preset: ...
    @overload
    def select(self, *, index: int = ...) -> Preset: ...

    def select(
        self,
        title: str | None = None,
        index: int = 0,
    ) -> Preset:
        if title is not None:
            if ret := next((p for p in self.presets if p.title == title), None):
                return ret
            raise ValueError(f"找不到标题为“{title}”的预设")

        return self.presets[index]

    def show(self) -> str:
        text = "💫预设列表"
        for i, p in enumerate(self.presets):
            text += f"\n{i}. {p.title}"
        return text

    def check_index(self, index: int) -> str | None:
        if index == 0:
            return "不允许选择默认预设"
        if index < 0 or index >= len(self.presets):
            return "序号不合法"
        return None


async def _get_user_preset(session_id: SessionID):
    return UserPresetData.load(session_id)


UserPreset = Annotated[UserPresetData, Depends(_get_user_preset)]
