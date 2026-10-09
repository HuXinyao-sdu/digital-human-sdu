# -*- coding: utf-8 -*-
"""讲解脚本解析器。

从 data/scripts/*.md 解析出结构化讲解项：
  - 元数据（frontmatter：title/era/duration/source/tags）
  - 讲解正文（去掉 frontmatter 与 Markdown 标题/备注，只留口播文本）

供 tts_generate.py / echomimic_generate.py / build_index.py 复用。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScriptItem:
    file: str                 # 文件名，如 01-登州文会馆.md
    path: Path                # 完整路径
    title: str = ""
    era: str = ""
    duration: str = ""
    source: str = ""
    tags: str = ""
    text: str = ""            # 口播正文（纯文本，已去标题/备注）
    meta: dict = field(default_factory=dict)


def parse_frontmatter(raw: str) -> dict:
    """解析 --- 包裹的 YAML-like frontmatter，字段均为字符串。"""
    meta: dict = {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw, flags=re.S)
    if not m:
        return meta
    block = m.group(1)
    for line in block.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip().strip('"\'')
        # 去掉列表写法中的前缀标记（- xxx）
        if value.startswith("- "):
            value = value[2:].strip()
        meta[key] = value
    return meta


def extract_speech_text(raw: str) -> str:
    """提取口播正文：去掉 frontmatter、'#'标题、引用块、备注区（---后/结尾备注）。

    规则：
      - 丢弃以 # 开头的标题行
      - 丢弃以 > 开头的引用/场景提示行
      - 丢弃 '---' 分隔线
      - 丢弃最后的 '## 备注(...)' 章节（供视频生成使用的提示不属于口播）
    """
    text = raw
    m = re.match(r"^---\s*\n.*?\n---\s*\n", text, flags=re.S)
    if m:
        text = text[m.end():]

    # 截掉"## 备注"之后的全部内容
    text = re.split(r"^##\s*备注", text, flags=re.M)[0]

    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if s.startswith(">"):
            continue
        if s == "---":
            continue
        lines.append(s)

    # 合并为段落：连续非空行合并，段落间保留一个空行
    paras: list[str] = []
    buf: list[str] = []
    for s in lines:
        if s.startswith("**") and s.endswith("**"):
            # 对话脚本中的角色名行（**老舍**：）保留为提示，去掉星号
            s = s.strip("*")
        buf.append(s)
    return "\n".join(buf)


def load_script(script_dir: Path, filename: str) -> ScriptItem | None:
    path = script_dir / filename
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8")
    meta = parse_frontmatter(raw)
    return ScriptItem(
        file=filename,
        path=path,
        title=meta.get("title", filename),
        era=meta.get("era", ""),
        duration=meta.get("duration", ""),
        source=meta.get("source", ""),
        tags=meta.get("tags", ""),
        text=extract_speech_text(raw),
        meta=meta,
    )


def load_all_scripts(script_dir: Path, filenames: list[str]) -> list[ScriptItem]:
    items = []
    for f in filenames:
        item = load_script(script_dir, f)
        if item is not None:
            items.append(item)
    return items


def estimate_duration_sec(item: ScriptItem, cps: float = 4.0) -> int:
    """按平均语速估算口播时长（cps=每秒汉字数，默认4字/秒≈正常语速）。"""
    hanzi = len(re.findall(r"[\u4e00-\u9fff]", item.text))
    return max(30, round(hanzi / cps))
