# Cultist Simulator 文本清洗工具 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 14 个目录中约 2,145 个 Markdown 文件清洗为结构化的 JSONL 数据集

**Architecture:** 五阶段 Pipeline（Extract → Parse → Clean → Validate → Export），每个阶段是独立的 Python 模块，通过 dataclass 传递数据。CLI 入口 `run_clean.py` 编排全流程。

**Tech Stack:** Python 3.10+, pyyaml, jsonlines, pytest

## Global Constraints

- Python 3.10+（使用 `str | None` 联合类型语法）
- 零外部服务依赖，完全离线运行
- 输入：项目根目录下的 14 个类别子目录
- 输出：`cleaned/` 目录下的 3 个 JSONL + 1 个统计 JSON + 1 个词汇表
- 测试使用 pytest，测试 fixtures 放在 `tests/fixtures/`

---

## 文件结构

```
cultist-simulator-text/
├── cleaner/                   # 清洗工具包
│   ├── __init__.py
│   ├── models.py              # 数据模型（RawRecord, ParsedRecord, CleanedRecord）
│   ├── extract.py             # 阶段1: 遍历目录，解析 frontmatter + body
│   ├── parse.py               # 阶段2: 从 body 提取 aspects / i18n / desc
│   ├── clean.py               # 阶段3: [[]] 解包、指令剥离、模板检测
│   ├── validate.py            # 阶段4: Schema 校验、去重
│   ├── export.py              # 阶段5: 输出 JSONL + stats + vocabulary
│   └── pipeline.py            # 编排器：串联五个阶段
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # 共享 fixtures
│   ├── test_extract.py
│   ├── test_parse.py
│   ├── test_clean.py
│   ├── test_validate.py
│   ├── test_export.py
│   ├── test_pipeline.py
│   └── fixtures/
│       ├── sample_dread.md           # 典型条目
│       ├── sample_empty_desc.md      # 空描述
│       ├── sample_template_var.md    # 含 #VARIABLE#
│       ├── sample_game_instruction.md # 含 [游戏指令]
│       └── sample_minimal.md         # 最简条目（无 aspects, 无 i18n）
├── cleaned/                   # 输出目录（gitignore）
├── run_clean.py               # CLI 入口
└── requirements.txt
```

---

### Task 1: 项目脚手架 + 测试 Fixtures

**Files:**
- Create: `cleaner/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/fixtures/sample_dread.md`
- Create: `tests/fixtures/sample_empty_desc.md`
- Create: `tests/fixtures/sample_template_var.md`
- Create: `tests/fixtures/sample_game_instruction.md`
- Create: `tests/fixtures/sample_minimal.md`
- Create: `requirements.txt`

**Interfaces:**
- Produces: 5 个测试 fixture 文件，可供后续所有测试使用
- Produces: `requirements.txt` 列出 `pyyaml`, `jsonlines`, `pytest`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p cleaner tests/fixtures cleaned
```

- [ ] **Step 2: 写入 requirements.txt**

```
pyyaml>=6.0
jsonlines>=4.0
pytest>=8.0
```

- [ ] **Step 3: 创建 `cleaner/__init__.py` 和 `tests/__init__.py`**（空文件）

```bash
touch cleaner/__init__.py tests/__init__.py
```

Wait, on Windows, use New-Item:
```powershell
New-Item -ItemType File -Path "cleaner/__init__.py"
New-Item -ItemType File -Path "tests/__init__.py"
```

No — let's just use Write for the empty files. Actually empty `__init__.py` can just be created with PowerShell.

- [ ] **Step 4: 创建测试 fixture `tests/fixtures/sample_dread.md`**

```markdown
---
element_id: "dread"
category: influences
source_file: "abilities.json"
tags: [cultist-simulator, influences]
---

# 恐惧
> `dread`

> 我已经见得太多了。不知名的恐惧正在用利齿啃噬着我的希望；一种关于存在本身的的恐惧。

**Aspects:** [[刃]], [[诱发绝望]], [[影响]], [[健康欠佳]], [[回忆]]
**Slots:** 忆起
**Requirements for Recipes:** [[绝望]], [[暗夜惊魂]]

---

## 🌐 多语言对照

| 语言 | Label | Description |
|------|-------|-------------|
| 中文 | 恐惧 | 我已经见得太多了。不知名的恐惧正在用利齿啃噬着我的希望；一种关于存在本身的的恐惧。 |
| English | Dread | I've seen too much. A nameless gnawing fear has its teeth in my hopes; an existential horror. |
| 日本語 | 恐怖 | 私はあまりにも目にしすぎてしまった。 |
| Русский | Ужас | Мне ведомо слишком многое. |
| Deutsch | Grauen | Ich hab zu viel gesehen. |

**Slots:**
  - EN: Reminders
  - ZH: 忆起
```

- [ ] **Step 5: 创建 `tests/fixtures/sample_empty_desc.md`**

```markdown
---
element_id: "defiance.foesummoned"
category: spirits
source_file: "DLC_EXILE_exile_elements.json"
tags: [cultist-simulator, spirits]
---

# 给大敌送去一条消息
> `defiance.foesummoned`

> None

**Requirements for Recipes:** [[发出反抗的召唤]]

---

## 🌐 多语言对照

| 语言 | Label | Description |
|------|-------|-------------|
| 中文 | 给大敌送去一条消息，透露我的行踪。 |  |
| English | Sent a message to the Foe, revealing my whereabouts. |  |
```

- [ ] **Step 6: 创建 `tests/fixtures/sample_template_var.md`**

```markdown
---
element_id: "apostleforge.mentor"
category: ascension
source_file: "legacy_apostle_elements.json"
tags: [cultist-simulator, ascension]
---

# 我们的塑形者#PREVIOUSCHARACTERNAME#
> `apostleforge.mentor`

> 斯人抚育我们，造就我们；斯人在流放中等待，必将于我们带来拂晓之时再起。

**Aspects:** [[导师]]

---

## 🌐 多语言对照

| 语言 | Label | Description |
|------|-------|-------------|
| 中文 | 我们的塑形者#PREVIOUSCHARACTERNAME# | 斯人抚育我们，造就我们；斯人在流放中等待，必将于我们带来拂晓之时再起。 |
| English | #PREVIOUSCHARACTERNAME#, our Shaper | The one who raised us; the one who made us what we are. |
```

- [ ] **Step 7: 创建 `tests/fixtures/sample_game_instruction.md`**

```markdown
---
element_id: "city.alexandria"
category: locations
source_file: "DLC_EXILE_exile_elements.json"
tags: [cultist-simulator, locations]
---

# 亚历山大港
> `city.alexandria`

> 战前，我被邀请去亚历山大港隐形的塞拉皮雍。走运的话，那份邀请依然有效。[一旦你离开现在的城市，这张卡牌将永远消失。]

**Aspects:** [[目的地]], [[崇拜狮子匠的密教]]

---

## 🌐 多语言对照

| 语言 | Label | Description |
|------|-------|-------------|
| 中文 | 亚历山大港 | 战前，我被邀请去亚历山大港隐形的塞拉皮雍。走运的话，那份邀请依然有效。[一旦你离开现在的城市，这张卡牌将永远消失。] |
| English | Alexandria | Back before the war, I was invited to the Invisible Serapeum in Alexandria. [Once you leave the current city, this will never be available again.] |
```

- [ ] **Step 8: 创建 `tests/fixtures/sample_minimal.md`**

```markdown
---
element_id: "simple.element"
category: tools
source_file: "test.json"
tags: [cultist-simulator, tools]
---

# 简单物品
> `simple.element`

> 这是一段简短的描述。

**Aspects:** [[铸]]
```

- [ ] **Step 9: 编写 `tests/conftest.py`**

```python
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def read_fixture(name: str) -> str:
    """读取测试 fixture 文件的原始文本。"""
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")
```

- [ ] **Step 10: 运行测试确认环境正常**

```bash
pytest tests/ -v
```
Expected: "no tests ran"（因为没有测试函数，但导入无报错）

- [ ] **Step 11: 初始化 git 并提交**

```bash
git init
git add -A
git commit -m "chore: init project scaffold, test fixtures, and requirements"
```

---

### Task 2: 数据模型

**Files:**
- Create: `cleaner/models.py`
- Create: `tests/test_models.py`

**Interfaces:**
- Produces:
  - `RawRecord(element_id, category, source_file, body: str)`
  - `ParsedRecord(element_id, category, name, desc_raw, aspects_raw: list[str], i18n_raw: dict)`
  - `CleanedRecord(id, name, desc, category, aspects: list[str], i18n: dict, meta: RecordMeta)`
  - `RecordMeta(desc_length: int, has_game_instruction: bool, has_template_var: bool)`
  - `I18nEntry(name: str, desc: str)`

- [ ] **Step 1: 编写失败的测试 `tests/test_models.py`**

```python
import json
from dataclasses import asdict
from cleaner.models import RawRecord, ParsedRecord, CleanedRecord, RecordMeta, I18nEntry


def test_raw_record_creation():
    r = RawRecord(
        element_id="dread",
        category="influences",
        source_file="abilities.json",
        body="# 恐惧\n> description text"
    )
    assert r.element_id == "dread"
    assert r.category == "influences"


def test_parsed_record_creation():
    r = ParsedRecord(
        element_id="dread",
        category="influences",
        name="恐惧",
        desc_raw="我已经见得太多了。",
        aspects_raw=["[[刃]]", "[[影响]]"],
        i18n_raw={"en": {"label": "Dread", "desc": "I've seen too much."}}
    )
    assert r.name == "恐惧"
    assert len(r.aspects_raw) == 2


def test_cleaned_record_creation():
    r = CleanedRecord(
        id="dread",
        name="恐惧",
        desc="我已经见得太多了。",
        category="influences",
        aspects=["刃", "影响"],
        i18n={
            "en": I18nEntry(name="Dread", desc="I've seen too much.")
        },
        meta=RecordMeta(
            desc_length=11,
            has_game_instruction=False,
            has_template_var=False
        )
    )
    assert r.id == "dread"
    assert r.meta.desc_length == 11
    assert r.meta.has_game_instruction is False


def test_cleaned_record_serializable():
    """CleanedRecord 应该可以序列化为 JSON。"""
    r = CleanedRecord(
        id="dread",
        name="恐惧",
        desc="测试文本。",
        category="influences",
        aspects=["刃"],
        i18n={
            "en": I18nEntry(name="Dread", desc="Test text.")
        },
        meta=RecordMeta(desc_length=5, has_game_instruction=False, has_template_var=False)
    )
    d = asdict(r)
    json_str = json.dumps(d, ensure_ascii=False)
    assert "恐惧" in json_str
    parsed = json.loads(json_str)
    assert parsed["id"] == "dread"
    assert parsed["meta"]["desc_length"] == 5


def test_record_meta_defaults():
    m = RecordMeta(desc_length=0)
    assert m.has_game_instruction is False
    assert m.has_template_var is False
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_models.py -v
```
Expected: 全部 FAIL（`ModuleNotFoundError: No module named 'cleaner.models'`）

- [ ] **Step 3: 实现 `cleaner/models.py`**

```python
from dataclasses import dataclass, field


@dataclass
class RawRecord:
    """从 Markdown 文件提取的原始记录。"""
    element_id: str
    category: str
    source_file: str
    body: str


@dataclass
class ParsedRecord:
    """解析 body 后的结构化记录（尚未清洗）。"""
    element_id: str
    category: str
    name: str                     # # Title
    desc_raw: str                 # > description block
    aspects_raw: list[str]        # still with [[...]]
    i18n_raw: dict[str, dict]     # {lang: {label, desc}}


@dataclass
class I18nEntry:
    """单语言条目。"""
    name: str
    desc: str


@dataclass
class RecordMeta:
    """质量元数据。"""
    desc_length: int
    has_game_instruction: bool = False
    has_template_var: bool = False


@dataclass
class CleanedRecord:
    """最终清洗后的记录。"""
    id: str
    name: str
    desc: str
    category: str
    aspects: list[str]
    i18n: dict[str, I18nEntry]
    meta: RecordMeta
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_models.py -v
```
Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
git add cleaner/models.py tests/test_models.py
git commit -m "feat: add data models (RawRecord, ParsedRecord, CleanedRecord)"
```

---

### Task 3: Extract 模块 — 遍历目录，提取 frontmatter + body

**Files:**
- Create: `cleaner/extract.py`
- Create: `tests/test_extract.py`

**Interfaces:**
- Consumes: `RawRecord` from `cleaner.models`
- Produces:
  - `extract_all(data_dir: Path) -> list[RawRecord]` — 遍历 14 个子目录，返回所有原始记录
  - `extract_file(filepath: Path) -> RawRecord | None` — 解析单个 .md 文件
  - `split_frontmatter_body(text: str) -> tuple[dict, str]` — 分离 frontmatter 和 body

- [ ] **Step 1: 编写失败的测试 `tests/test_extract.py`**

```python
import pytest
from pathlib import Path
from cleaner.extract import split_frontmatter_body, extract_file, extract_all
from cleaner.models import RawRecord
from tests.conftest import FIXTURES_DIR


class TestSplitFrontmatterBody:
    def test_normal_file(self):
        text = (FIXTURES_DIR / "sample_dread.md").read_text("utf-8")
        fm, body = split_frontmatter_body(text)
        assert fm["element_id"] == "dread"
        assert fm["category"] == "influences"
        assert "# 恐惧" in body
        # body 不应包含 frontmatter 分隔符
        assert "---" not in body

    def test_no_frontmatter(self):
        text = "# Just a heading\n> some text"
        fm, body = split_frontmatter_body(text)
        assert fm == {}
        assert body == text


class TestExtractFile:
    def test_extract_dread(self):
        filepath = FIXTURES_DIR / "sample_dread.md"
        record = extract_file(filepath)
        assert record is not None
        assert record.element_id == "dread"
        assert record.category == "influences"
        assert "恐惧" in record.body
        assert "多语言对照" in record.body

    def test_extract_minimal(self):
        filepath = FIXTURES_DIR / "sample_minimal.md"
        record = extract_file(filepath)
        assert record is not None
        assert record.element_id == "simple.element"
        assert "简单物品" in record.body

    def test_extract_nonexistent_file(self):
        record = extract_file(Path("/nonexistent/file.md"))
        assert record is None


class TestExtractAll:
    def test_extract_all_from_fixtures(self, tmp_path):
        # 复制 fixtures 到临时目录模拟真实结构
        import shutil
        fixtures_dir = tmp_path / "influences"
        fixtures_dir.mkdir()
        for f in FIXTURES_DIR.glob("*.md"):
            shutil.copy(f, fixtures_dir / f.name)

        records = extract_all(tmp_path)
        assert len(records) >= 5
        ids = {r.element_id for r in records}
        assert "dread" in ids
        assert "simple.element" in ids

    def test_extract_all_empty_dir(self, tmp_path):
        records = extract_all(tmp_path)
        assert records == []
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_extract.py -v
```
Expected: FAIL（模块不存在）

- [ ] **Step 3: 实现 `cleaner/extract.py`**

```python
import re
from pathlib import Path
import yaml

from cleaner.models import RawRecord


def split_frontmatter_body(text: str) -> tuple[dict, str]:
    """分离 YAML frontmatter 和 Markdown body。"""
    # frontmatter 以 --- 开头和结束
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, text, re.DOTALL)
    if not match:
        return {}, text
    fm_text = match.group(1)
    body = text[match.end():]
    try:
        fm = yaml.safe_load(fm_text)
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        fm = {}
    return fm, body


def extract_file(filepath: Path) -> RawRecord | None:
    """解析单个 .md 文件，返回 RawRecord。"""
    if not filepath.exists() or not filepath.suffix == '.md':
        return None
    try:
        text = filepath.read_text(encoding='utf-8')
    except Exception:
        return None
    fm, body = split_frontmatter_body(text)
    return RawRecord(
        element_id=fm.get("element_id", filepath.stem),
        category=fm.get("category", ""),
        source_file=fm.get("source_file", ""),
        body=body
    )


def extract_all(data_dir: Path) -> list[RawRecord]:
    """遍历 data_dir 下所有子目录，提取所有 .md 文件。"""
    records: list[RawRecord] = []
    for md_file in sorted(data_dir.rglob("*.md")):
        record = extract_file(md_file)
        if record:
            records.append(record)
    return records
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_extract.py -v
```
Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
git add cleaner/extract.py tests/test_extract.py
git commit -m "feat: add extract module — walk dirs, parse frontmatter + body"
```

---

### Task 4: Parse 模块 — 解析 body 中的 aspects / i18n / 描述

**Files:**
- Create: `cleaner/parse.py`
- Create: `tests/test_parse.py`

**Interfaces:**
- Consumes: `RawRecord` from `cleaner.models`, `ParsedRecord` from `cleaner.models`
- Produces:
  - `parse_record(raw: RawRecord) -> ParsedRecord` — 解析单条 RawRecord
  - `parse_title(body: str) -> str` — 提取 `# Title`
  - `parse_description(body: str) -> str` — 提取 `> desc` 块
  - `parse_aspects(body: str) -> list[str]` — 提取 `[[...]]` 列表
  - `parse_i18n_table(body: str) -> dict[str, dict]` — 解析多语言表

- [ ] **Step 1: 编写失败的测试 `tests/test_parse.py`**

```python
import pytest
from pathlib import Path
from cleaner.models import RawRecord
from cleaner.parse import (
    parse_title, parse_description, parse_aspects,
    parse_i18n_table, parse_record
)
from tests.conftest import FIXTURES_DIR


def _raw_from_fixture(name: str) -> RawRecord:
    text = (FIXTURES_DIR / name).read_text("utf-8")
    # 手动构造 RawRecord 以便测试（绕过 extract）
    body_start = text.find("\n---\n", text.find("---\n") + 4)
    body = text[body_start + 5:] if body_start != -1 else text
    return RawRecord(
        element_id="test",
        category="test",
        source_file="test.json",
        body=body
    )


class TestParseTitle:
    def test_parse_title(self):
        body = "# 恐惧\n> `dread`\n> desc"
        assert parse_title(body) == "恐惧"

    def test_parse_title_with_template_var(self):
        body = "# 我们的塑形者#PREVIOUSCHARACTERNAME#\n> desc"
        assert parse_title(body) == "我们的塑形者#PREVIOUSCHARACTERNAME#"

    def test_parse_title_no_heading(self):
        body = "no heading here"
        assert parse_title(body) == ""


class TestParseDescription:
    def test_parse_normal_desc(self):
        body = "# 恐惧\n> `dread`\n\n> 我已经见得太多了。\n\n**Aspects:**"
        assert parse_description(body) == "我已经见得太多了。"

    def test_parse_none_desc(self):
        body = "# Test\n> `id`\n\n> None\n\n**Requirements:**"
        assert parse_description(body) == ""

    def test_parse_empty_desc_line(self):
        body = "# Test\n> `id`\n\n> \n\n**Aspects:**"
        assert parse_description(body) == ""

    def test_parse_game_instruction_desc(self):
        body = "# 亚历山大港\n> `city.alexandria`\n\n> 战前，我被邀请。[指令内容]\n\n**Aspects:**"
        result = parse_description(body)
        assert "战前，我被邀请。" in result
        assert "[指令内容]" in result  # parse 阶段保留原始文本


class TestParseAspects:
    def test_parse_aspects(self):
        body = "**Aspects:** [[刃]], [[诱发绝望]], [[影响]], [[健康欠佳]], [[回忆]]"
        aspects = parse_aspects(body)
        assert aspects == ["[[刃]]", "[[诱发绝望]]", "[[影响]]", "[[健康欠佳]]", "[[回忆]]"]

    def test_parse_aspects_with_empty(self):
        body = "**Aspects:** [[刃]], [[]], [[影响]]"
        aspects = parse_aspects(body)
        assert aspects == ["[[刃]]", "[[]]", "[[影响]]"]

    def test_parse_no_aspects(self):
        body = "**Slots:** 忆起"
        aspects = parse_aspects(body)
        assert aspects == []


class TestParseI18nTable:
    def test_parse_i18n_table(self):
        raw = _raw_from_fixture("sample_dread.md")
        i18n = parse_i18n_table(raw.body)
        assert "zh" in i18n
        assert i18n["zh"]["label"] == "恐惧"
        assert "我已经见得太多了" in i18n["zh"]["desc"]
        assert "en" in i18n
        assert i18n["en"]["label"] == "Dread"
        assert "ja" in i18n
        assert "ru" in i18n
        assert "de" in i18n

    def test_parse_no_i18n_table(self):
        raw = _raw_from_fixture("sample_minimal.md")
        i18n = parse_i18n_table(raw.body)
        assert i18n == {}


class TestParseRecord:
    def test_parse_dread(self):
        raw = _raw_from_fixture("sample_dread.md")
        parsed = parse_record(raw)
        assert parsed.name == "恐惧"
        assert "我已经见得太多了" in parsed.desc_raw
        assert len(parsed.aspects_raw) == 5
        assert "en" in parsed.i18n_raw

    def test_parse_empty_desc(self):
        raw = _raw_from_fixture("sample_empty_desc.md")
        parsed = parse_record(raw)
        assert parsed.desc_raw == ""

    def test_parse_template_var(self):
        raw = _raw_from_fixture("sample_template_var.md")
        parsed = parse_record(raw)
        assert "#PREVIOUSCHARACTERNAME#" in parsed.name
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_parse.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现 `cleaner/parse.py`**

```python
import re
from cleaner.models import RawRecord, ParsedRecord

# 语言名到 ISO 代码的映射
LANG_MAP = {
    "中文": "zh",
    "English": "en",
    "日本語": "ja",
    "Русский": "ru",
    "Deutsch": "de",
}


def parse_title(body: str) -> str:
    """提取 # Title 行。"""
    match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
    return match.group(1).strip() if match else ""


def parse_description(body: str) -> str:
    """提取 > description 块（id 行之后的 > 文本）。"""
    # 找到 `id` 后面的第一个 > 段落
    # 格式: > `id`\n\n> description text\n\n**Something:**
    # 或:   > `id`\n\n> None\n\n
    # 提取 id 行之后、下一个 ** 之前的所有 > 行
    pattern = r'>\s*`[^`]+`\s*\n+\n*(?:>\s*(.+?)\s*\n(?:\n|(?=\*\*)))'
    match = re.search(pattern, body, re.DOTALL)
    if not match:
        return ""
    desc = match.group(1).strip()
    if desc.lower() == "none" or not desc:
        return ""
    return desc


def parse_aspects(body: str) -> list[str]:
    """提取 Aspects 行中的 [[...]] 列表（保留双方括号）。"""
    match = re.search(r'\*\*Aspects:\*\*\s*(.+)$', body, re.MULTILINE)
    if not match:
        return []
    raw = match.group(1)
    # 匹配所有 [[...]]
    aspects = re.findall(r'\[\[.*?\]\]', raw)
    return aspects


def parse_i18n_table(body: str) -> dict[str, dict]:
    """解析 ## 🌐 多语言对照 下方的 Markdown 表格。"""
    # 找到多语言对照 section
    section_match = re.search(
        r'##\s*🌐\s*多语言对照\s*\n(.*?)(?:\n\*\*Slots:|$)',
        body, re.DOTALL
    )
    if not section_match:
        return {}

    table_text = section_match.group(1)

    # 解析表格行: | 语言 | Label | Description |
    # 跳过表头
    rows = re.findall(
        r'\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.*?)\s*\|',
        table_text
    )

    result = {}
    for row in rows:
        lang_name = row[0].strip()
        label = row[1].strip()
        desc = row[2].strip()

        # 跳过表头分隔行
        if lang_name in ("语言", "------", ":---"):
            continue
        if set(lang_name) <= {'-', ':', '|', ' '}:
            continue

        iso = LANG_MAP.get(lang_name, lang_name.lower())
        result[iso] = {"label": label, "desc": desc}

    return result


def parse_record(raw: RawRecord) -> ParsedRecord:
    """解析 RawRecord 的 body，生成 ParsedRecord。"""
    body = raw.body
    return ParsedRecord(
        element_id=raw.element_id,
        category=raw.category,
        name=parse_title(body),
        desc_raw=parse_description(body),
        aspects_raw=parse_aspects(body),
        i18n_raw=parse_i18n_table(body),
    )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_parse.py -v
```
Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
git add cleaner/parse.py tests/test_parse.py
git commit -m "feat: add parse module — extract title, desc, aspects, i18n from body"
```

---

### Task 5: Clean 模块 — `[[]]` 解包、游戏指令剥离、模板检测

**Files:**
- Create: `cleaner/clean.py`
- Create: `tests/test_clean.py`

**Interfaces:**
- Consumes: `ParsedRecord`, `CleanedRecord`, `RecordMeta`, `I18nEntry` from `cleaner.models`
- Produces:
  - `clean_record(parsed: ParsedRecord) -> CleanedRecord` — 清洗单条记录
  - `clean_aspects(raw: list[str]) -> list[str]` — 去掉 `[[]]`，过滤空值
  - `clean_description(desc: str) -> tuple[str, bool, bool]` — 返回 (clean_desc, has_instruction, has_template)
  - `clean_i18n(raw: dict) -> dict[str, I18nEntry]`

- [ ] **Step 1: 编写失败的测试 `tests/test_clean.py`**

```python
import pytest
from cleaner.models import ParsedRecord, CleanedRecord, I18nEntry
from cleaner.clean import (
    clean_aspects, clean_description, clean_i18n, clean_record
)


class TestCleanAspects:
    def test_normal(self):
        raw = ["[[刃]]", "[[诱发绝望]]", "[[影响]]"]
        result = clean_aspects(raw)
        assert result == ["刃", "诱发绝望", "影响"]

    def test_with_empty_brackets(self):
        raw = ["[[刃]]", "[[]]", "[[影响]]"]
        result = clean_aspects(raw)
        assert result == ["刃", "影响"]

    def test_empty_list(self):
        assert clean_aspects([]) == []


class TestCleanDescription:
    def test_normal(self):
        desc, has_inst, has_tmpl = clean_description("一段纯粹的叙事文本。")
        assert desc == "一段纯粹的叙事文本。"
        assert has_inst is False
        assert has_tmpl is False

    def test_with_game_instruction(self):
        desc, has_inst, has_tmpl = clean_description(
            "战前，我被邀请去亚历山大港。[一旦你离开，卡牌将消失。]"
        )
        assert "战前，我被邀请去亚历山大港。" in desc
        assert "[一旦你离开" not in desc
        assert has_inst is True
        assert has_tmpl is False

    def test_with_multiple_instructions(self):
        desc, has_inst, has_tmpl = clean_description(
            "文本开头。[指令一]中间文本。[指令二]"
        )
        assert "指令一" not in desc
        assert "指令二" not in desc
        assert "文本开头。" in desc
        assert "中间文本。" in desc
        assert has_inst is True

    def test_with_template_var(self):
        desc, has_inst, has_tmpl = clean_description(
            "斯人抚育我们，造就我们；斯人在流放中等待，必将于我们带来拂晓之时再起。"
        )
        # 描述本身不含 #VAR#，但 title 可能含，这里测 desc
        assert has_inst is False
        # has_template_var 由调用方根据 name + desc 一起判断

    def test_with_template_var_in_text(self):
        desc, has_inst, has_tmpl = clean_description(
            "我们的塑形者#PREVIOUSCHARACTERNAME#在等待。"
        )
        assert has_tmpl is True

    def test_empty_desc(self):
        desc, has_inst, has_tmpl = clean_description("")
        assert desc == ""
        assert has_inst is False
        assert has_tmpl is False


class TestCleanI18n:
    def test_normal(self):
        raw = {
            "en": {"label": "Dread", "desc": "I've seen too much. [game tip]"},
            "ja": {"label": "恐怖", "desc": "テスト。"},
        }
        result = clean_i18n(raw)
        assert result["en"].name == "Dread"
        assert "[game tip]" not in result["en"].desc
        assert result["ja"].name == "恐怖"

    def test_empty(self):
        assert clean_i18n({}) == {}


class TestCleanRecord:
    def test_full_clean(self):
        parsed = ParsedRecord(
            element_id="dread",
            category="influences",
            name="恐惧",
            desc_raw="我已经见得太多了。[游戏提示]",
            aspects_raw=["[[刃]]", "[[]]", "[[影响]]"],
            i18n_raw={
                "en": {"label": "Dread", "desc": "I've seen too much."}
            }
        )
        result = clean_record(parsed)
        assert result.id == "dread"
        assert result.name == "恐惧"
        assert "我已经见得太多了" in result.desc
        assert "[游戏提示]" not in result.desc
        assert result.aspects == ["刃", "影响"]
        assert result.meta.has_game_instruction is True
        assert result.meta.desc_length > 0

    def test_template_var_in_name(self):
        parsed = ParsedRecord(
            element_id="test",
            category="ascension",
            name="我们的塑形者#PREVIOUSCHARACTERNAME#",
            desc_raw="斯人抚育我们。",
            aspects_raw=[],
            i18n_raw={}
        )
        result = clean_record(parsed)
        assert result.meta.has_template_var is True
        assert "#PREVIOUSCHARACTERNAME#" in result.name

    def test_empty_desc_record(self):
        parsed = ParsedRecord(
            element_id="empty",
            category="spirits",
            name="空条",
            desc_raw="",
            aspects_raw=[],
            i18n_raw={}
        )
        result = clean_record(parsed)
        assert result.desc == ""
        assert result.meta.desc_length == 0
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_clean.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现 `cleaner/clean.py`**

```python
import re
from cleaner.models import ParsedRecord, CleanedRecord, RecordMeta, I18nEntry


def clean_aspects(raw: list[str]) -> list[str]:
    """去掉 [[]] 包裹，过滤空内容。"""
    result = []
    for a in raw:
        inner = a.strip()
        if inner.startswith("[[") and inner.endswith("]]"):
            inner = inner[2:-2]
        if inner:  # 过滤空字符串（原 [[]]）
            result.append(inner)
    return result


def clean_description(desc: str) -> tuple[str, bool, bool]:
    """
    清洗描述文本。
    返回: (cleaned_text, has_game_instruction)
    """
    has_instruction = False

    # 移除 [游戏指令]
    cleaned, count = re.subn(r'\[[^\]]*\]', '', desc)
    if count > 0:
        has_instruction = True
        # 清理多余空格
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        # 清理句号后缺少空格，以及多余标点
        cleaned = re.sub(r'。\s*。', '。', cleaned)
        cleaned = re.sub(r'，\s*，', '，', cleaned)
        cleaned = cleaned.strip()

    # 检测模板变量 #VAR#
    has_template = bool(re.search(r'#[A-Z_]+#', desc))

    return cleaned, has_instruction, has_template


def clean_i18n(raw: dict[str, dict]) -> dict[str, I18nEntry]:
    """清洗多语言数据。"""
    result = {}
    for lang_code, entry in raw.items():
        name = entry.get("label", "")
        desc = entry.get("desc", "")
        # 同样清洗 i18n 中的游戏指令
        desc_clean, _, _ = clean_description(desc)
        result[lang_code] = I18nEntry(name=name, desc=desc_clean)
    return result


def clean_record(parsed: ParsedRecord) -> CleanedRecord:
    """清洗单条 ParsedRecord 为 CleanedRecord。"""
    desc_clean, has_inst, has_tmpl_desc = clean_description(parsed.desc_raw)

    # 模板变量可能出现在 name 或 desc 中
    has_tmpl_name = bool(re.search(r'#[A-Z_]+#', parsed.name))
    has_template = has_tmpl_desc or has_tmpl_name

    return CleanedRecord(
        id=parsed.element_id,
        name=parsed.name,
        desc=desc_clean,
        category=parsed.category,
        aspects=clean_aspects(parsed.aspects_raw),
        i18n=clean_i18n(parsed.i18n_raw),
        meta=RecordMeta(
            desc_length=len(desc_clean),
            has_game_instruction=has_inst,
            has_template_var=has_template,
        ),
    )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
pytest tests/test_clean.py -v
```
Expected: 全部 PASS

- [ ] **Step 5: 提交**

```bash
git add cleaner/clean.py tests/test_clean.py
git commit -m "feat: add clean module — unpack [[]], strip game instructions, detect templates"
```

---

### Task 6: Validate + Export 模块

**Files:**
- Create: `cleaner/validate.py`
- Create: `cleaner/export.py`
- Create: `tests/test_validate.py`
- Create: `tests/test_export.py`

**Interfaces:**
- Consumes: `CleanedRecord`, `RecordMeta`, `I18nEntry` from `cleaner.models`
- Produces (validate):
  - `validate_record(r: CleanedRecord) -> list[str]` — 返回错误列表，空列表 = 合规
  - `deduplicate(records: list[CleanedRecord]) -> list[CleanedRecord]` — 按 id 去重
- Produces (export):
  - `export_jsonl(records: list[CleanedRecord], path: Path) -> int` — 写入条数
  - `export_lite(records: list[CleanedRecord], path: Path) -> int`
  - `export_parallel(records: list[CleanedRecord], path: Path) -> int`
  - `export_stats(records: list[CleanedRecord], path: Path) -> None`
  - `export_vocabulary(records: list[CleanedRecord], path: Path) -> None`

- [ ] **Step 1: 编写 validate 测试 `tests/test_validate.py`**

```python
import pytest
from cleaner.models import CleanedRecord, RecordMeta
from cleaner.validate import validate_record, deduplicate


class TestValidateRecord:
    def test_valid_record(self):
        r = CleanedRecord(
            id="dread", name="恐惧", desc="文本。",
            category="influences", aspects=["刃"],
            i18n={}, meta=RecordMeta(desc_length=3)
        )
        errors = validate_record(r)
        assert errors == []

    def test_missing_id(self):
        r = CleanedRecord(
            id="", name="恐惧", desc="文本。",
            category="influences", aspects=[],
            i18n={}, meta=RecordMeta(desc_length=3)
        )
        errors = validate_record(r)
        assert len(errors) > 0
        assert any("id" in e.lower() for e in errors)

    def test_missing_name(self):
        r = CleanedRecord(
            id="test", name="", desc="文本。",
            category="influences", aspects=[],
            i18n={}, meta=RecordMeta(desc_length=3)
        )
        errors = validate_record(r)
        assert len(errors) > 0

    def test_missing_category(self):
        r = CleanedRecord(
            id="test", name="测试", desc="文本。",
            category="", aspects=[],
            i18n={}, meta=RecordMeta(desc_length=3)
        )
        errors = validate_record(r)
        assert len(errors) > 0


class TestDeduplicate:
    def test_no_duplicates(self):
        r1 = CleanedRecord(id="a", name="A", desc="", category="x",
                           aspects=[], i18n={}, meta=RecordMeta(desc_length=0))
        r2 = CleanedRecord(id="b", name="B", desc="", category="x",
                           aspects=[], i18n={}, meta=RecordMeta(desc_length=0))
        result = deduplicate([r1, r2])
        assert len(result) == 2

    def test_with_duplicates(self):
        r1 = CleanedRecord(id="a", name="A1", desc="", category="x",
                           aspects=[], i18n={}, meta=RecordMeta(desc_length=0))
        r2 = CleanedRecord(id="a", name="A2", desc="", category="y",
                           aspects=[], i18n={}, meta=RecordMeta(desc_length=0))
        result = deduplicate([r1, r2])
        assert len(result) == 1
        # 保留第一个
        assert result[0].name == "A1"
```

- [ ] **Step 2: 编写 export 测试 `tests/test_export.py`**

```python
import json
import jsonlines
from pathlib import Path
from cleaner.models import CleanedRecord, RecordMeta, I18nEntry
from cleaner.export import (
    export_jsonl, export_lite, export_parallel, export_stats, export_vocabulary
)


def _sample_records():
    return [
        CleanedRecord(
            id="dread", name="恐惧",
            desc="我已经见得太多了。",
            category="influences",
            aspects=["刃", "影响"],
            i18n={
                "en": I18nEntry(name="Dread", desc="I've seen too much.")
            },
            meta=RecordMeta(desc_length=11, has_game_instruction=False, has_template_var=False)
        ),
        CleanedRecord(
            id="empty", name="空条",
            desc="",
            category="spirits",
            aspects=[],
            i18n={},
            meta=RecordMeta(desc_length=0, has_game_instruction=False, has_template_var=False)
        ),
    ]


def test_export_jsonl(tmp_path):
    output = tmp_path / "test.jsonl"
    count = export_jsonl(_sample_records(), output)
    assert count == 2
    assert output.exists()
    with jsonlines.open(output) as reader:
        records = list(reader)
    assert len(records) == 2
    assert records[0]["id"] == "dread"
    assert records[0]["meta"]["desc_length"] == 11


def test_export_lite(tmp_path):
    output = tmp_path / "lite.jsonl"
    count = export_lite(_sample_records(), output)
    assert count == 1  # 只有 desc_length > 10 的条目
    with jsonlines.open(output) as reader:
        records = list(reader)
    assert len(records) == 1
    # Lite 不应包含 i18n 或 meta
    assert "i18n" not in records[0]
    assert "meta" not in records[0]


def test_export_parallel(tmp_path):
    output = tmp_path / "parallel.jsonl"
    count = export_parallel(_sample_records(), output)
    assert count == 1  # 只有有英文翻译的
    with jsonlines.open(output) as reader:
        records = list(reader)
    assert records[0]["zh"] == "我已经见得太多了。"
    assert records[0]["en"] == "I've seen too much."


def test_export_stats(tmp_path):
    output = tmp_path / "stats.json"
    export_stats(_sample_records(), output)
    assert output.exists()
    stats = json.loads(output.read_text("utf-8"))
    assert stats["total"] == 2
    assert "by_category" in stats
    assert stats["by_category"]["influences"] == 1
    assert stats["by_category"]["spirits"] == 1
    assert stats["empty_desc"] == 1
    assert "desc_length" in stats


def test_export_vocabulary(tmp_path):
    output = tmp_path / "vocab.txt"
    export_vocabulary(_sample_records(), output)
    assert output.exists()
    content = output.read_text("utf-8")
    # 应该包含 aspects
    assert "刃" in content
    assert "影响" in content
```

- [ ] **Step 3: 运行测试确认失败**

```bash
pytest tests/test_validate.py tests/test_export.py -v
```
Expected: FAIL

- [ ] **Step 4: 实现 `cleaner/validate.py`**

```python
from cleaner.models import CleanedRecord


def validate_record(record: CleanedRecord) -> list[str]:
    """校验单条记录，返回错误列表（空 = 合规）。"""
    errors = []
    if not record.id:
        errors.append(f"missing id")
    if not record.name:
        errors.append(f"[{record.id}] missing name")
    if not record.category:
        errors.append(f"[{record.id}] missing category")
    return errors


def deduplicate(records: list[CleanedRecord]) -> list[CleanedRecord]:
    """按 id 去重，保留首次出现。"""
    seen: set[str] = set()
    result = []
    for r in records:
        if r.id not in seen:
            seen.add(r.id)
            result.append(r)
    return result
```

- [ ] **Step 5: 实现 `cleaner/export.py`**

```python
import json
import re
from collections import Counter
from pathlib import Path
from dataclasses import asdict

import jsonlines
from cleaner.models import CleanedRecord


def export_jsonl(records: list[CleanedRecord], path: Path) -> int:
    """导出全量 JSONL。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with jsonlines.open(path, mode="w") as writer:
        for r in records:
            writer.write(asdict(r))
    return len(records)


def export_lite(records: list[CleanedRecord], path: Path) -> int:
    """导出精简版 JSONL：仅中文核心字段，过滤 desc_length < 10。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    filtered = [r for r in records if r.meta.desc_length >= 10]
    with jsonlines.open(path, mode="w") as writer:
        for r in filtered:
            writer.write({
                "id": r.id,
                "name": r.name,
                "desc": r.desc,
                "category": r.category,
                "aspects": r.aspects,
            })
    return len(filtered)


def export_parallel(records: list[CleanedRecord], path: Path) -> int:
    """导出中英平行语料：仅含有关键英文翻译的条目。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    filtered = []
    for r in records:
        en = r.i18n.get("en")
        if en and en.desc and r.desc:
            filtered.append({"zh": r.desc, "en": en.desc})
    with jsonlines.open(path, mode="w") as writer:
        for item in filtered:
            writer.write(item)
    return len(filtered)


def export_stats(records: list[CleanedRecord], path: Path) -> None:
    """导出统计报告。"""
    path.parent.mkdir(parents=True, exist_ok=True)

    by_category = Counter(r.category for r in records)
    empty_desc = sum(1 for r in records if r.meta.desc_length == 0)
    has_instruction = sum(1 for r in records if r.meta.has_game_instruction)
    has_template = sum(1 for r in records if r.meta.has_template_var)

    lengths = [r.meta.desc_length for r in records if r.meta.desc_length > 0]
    lengths.sort()

    # 性相频率
    aspect_counter = Counter()
    for r in records:
        for a in r.aspects:
            aspect_counter[a] += 1

    stats = {
        "total": len(records),
        "empty_desc": empty_desc,
        "has_game_instruction": has_instruction,
        "has_template_var": has_template,
        "by_category": dict(by_category),
        "desc_length": {
            "min": lengths[0] if lengths else 0,
            "max": lengths[-1] if lengths else 0,
            "mean": round(sum(lengths) / len(lengths), 1) if lengths else 0,
            "median": lengths[len(lengths) // 2] if lengths else 0,
        },
        "top_aspects": aspect_counter.most_common(50),
    }

    path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")


def export_vocabulary(records: list[CleanedRecord], path: Path) -> None:
    """导出术语表：去重的人名、地名、司辰名、书名。"""
    path.parent.mkdir(parents=True, exist_ok=True)

    terms: set[str] = set()

    for r in records:
        # 名称
        if r.name:
            terms.add(r.name)
        # 性相
        for a in r.aspects:
            terms.add(a)
        # 书名《...》
        for match in re.findall(r'《([^》]+)》', r.desc):
            terms.add(f"《{match}》")

    sorted_terms = sorted(terms, key=lambda x: (not x.startswith("《"), x))
    path.write_text("\n".join(sorted_terms), encoding="utf-8")
```

- [ ] **Step 6: 运行测试确认通过**

```bash
pytest tests/test_validate.py tests/test_export.py -v
```
Expected: 全部 PASS

- [ ] **Step 7: 提交**

```bash
git add cleaner/validate.py cleaner/export.py tests/test_validate.py tests/test_export.py
git commit -m "feat: add validate + export modules — schema check, dedup, JSONL/stats/vocab output"
```

---

### Task 7: Pipeline 编排器 + CLI 入口

**Files:**
- Create: `cleaner/pipeline.py`
- Create: `run_clean.py`
- Create: `tests/test_pipeline.py`

**Interfaces:**
- Consumes: 所有前置模块
- Produces:
  - `PipelineReport(total_files, extracted, parsed, cleaned, validated, exported, errors)`
  - `run_pipeline(data_dir: Path, output_dir: Path) -> PipelineReport`

- [ ] **Step 1: 编写集成测试 `tests/test_pipeline.py`**

```python
import json
import shutil
from pathlib import Path
from cleaner.pipeline import run_pipeline
from tests.conftest import FIXTURES_DIR


def test_pipeline_end_to_end(tmp_path):
    # 建立模拟数据目录
    data_dir = tmp_path / "data" / "influences"
    data_dir.mkdir(parents=True)
    for f in FIXTURES_DIR.glob("*.md"):
        shutil.copy(f, data_dir / f.name)

    output_dir = tmp_path / "output"
    report = run_pipeline(data_dir, output_dir)

    assert report.total_files >= 5
    assert report.parsed == report.total_files
    assert report.cleaned == report.total_files
    assert report.errors == 0

    # 检查输出文件
    assert (output_dir / "cs_dataset.jsonl").exists()
    assert (output_dir / "cs_dataset_lite.jsonl").exists()
    assert (output_dir / "cs_parallel_zh_en.jsonl").exists()
    assert (output_dir / "cs_stats.json").exists()
    assert (output_dir / "cs_vocabulary.txt").exists()

    # 验证 stats 内容
    stats = json.loads((output_dir / "cs_stats.json").read_text("utf-8"))
    assert stats["total"] >= 5
    assert "influences" in stats["by_category"]


def test_pipeline_empty_dir(tmp_path):
    data_dir = tmp_path / "empty_data"
    data_dir.mkdir()
    output_dir = tmp_path / "output"
    report = run_pipeline(data_dir, output_dir)
    assert report.total_files == 0
    assert report.parsed == 0
```

- [ ] **Step 2: 运行测试确认失败**

```bash
pytest tests/test_pipeline.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现 `cleaner/pipeline.py`**

```python
from dataclasses import dataclass
from pathlib import Path

from cleaner.extract import extract_all
from cleaner.parse import parse_record
from cleaner.clean import clean_record
from cleaner.validate import validate_record, deduplicate
from cleaner.export import (
    export_jsonl, export_lite, export_parallel, export_stats, export_vocabulary
)


@dataclass
class PipelineReport:
    data_dir: str
    output_dir: str
    total_files: int
    extracted: int
    parsed: int
    cleaned: int
    validated: int
    exported: int
    errors: int
    error_details: list[str]


def run_pipeline(data_dir: Path, output_dir: Path) -> PipelineReport:
    """执行完整的 ETL pipeline。"""
    error_details: list[str] = []

    # 阶段 1: Extract
    raw_records = extract_all(data_dir)
    total_files = len(raw_records)

    # 阶段 2: Parse
    parsed_records = []
    for raw in raw_records:
        try:
            parsed_records.append(parse_record(raw))
        except Exception as e:
            error_details.append(f"Parse error [{raw.element_id}]: {e}")

    # 阶段 3: Clean
    cleaned_records = []
    for p in parsed_records:
        try:
            cleaned_records.append(clean_record(p))
        except Exception as e:
            error_details.append(f"Clean error [{p.element_id}]: {e}")

    # 阶段 4: Validate
    valid_records = []
    for c in cleaned_records:
        errors = validate_record(c)
        if errors:
            error_details.extend(f"Validation [{c.id}]: {err}" for err in errors)
        else:
            valid_records.append(c)

    # 去重
    unique_records = deduplicate(valid_records)

    # 阶段 5: Export
    output_dir.mkdir(parents=True, exist_ok=True)
    exported_count = 0
    try:
        exported_count += export_jsonl(unique_records, output_dir / "cs_dataset.jsonl")
        exported_count += export_lite(unique_records, output_dir / "cs_dataset_lite.jsonl")
        exported_count += export_parallel(unique_records, output_dir / "cs_parallel_zh_en.jsonl")
        export_stats(unique_records, output_dir / "cs_stats.json")
        export_vocabulary(unique_records, output_dir / "cs_vocabulary.txt")
    except Exception as e:
        error_details.append(f"Export error: {e}")

    return PipelineReport(
        data_dir=str(data_dir),
        output_dir=str(output_dir),
        total_files=total_files,
        extracted=len(raw_records),
        parsed=len(parsed_records),
        cleaned=len(cleaned_records),
        validated=len(unique_records),
        exported=exported_count,
        errors=len(error_details),
        error_details=error_details,
    )
```

- [ ] **Step 4: 实现 CLI 入口 `run_clean.py`**

```python
#!/usr/bin/env python3
"""Cultist Simulator 文本清洗工具 — CLI 入口。

Usage:
    python run_clean.py                          # 使用默认路径
    python run_clean.py --data-dir ./data --output-dir ./output
"""

import argparse
import sys
from pathlib import Path

from cleaner.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="清洗 Cultist Simulator 文本数据为结构化 JSONL 数据集"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(__file__).parent,
        help="包含 14 个类别子目录的根目录（默认：项目根目录）"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "cleaned",
        help="输出目录（默认：./cleaned）"
    )
    args = parser.parse_args()

    if not args.data_dir.exists():
        print(f"错误：数据目录不存在：{args.data_dir}")
        sys.exit(1)

    print(f"数据目录: {args.data_dir}")
    print(f"输出目录: {args.output_dir}")
    print("正在清洗...")

    report = run_pipeline(args.data_dir, args.output_dir)

    print(f"\n=== 清洗报告 ===")
    print(f"  扫描文件: {report.total_files}")
    print(f"  提取成功: {report.extracted}")
    print(f"  解析成功: {report.parsed}")
    print(f"  清洗成功: {report.cleaned}")
    print(f"  校验通过: {report.validated}")
    print(f"  导出条数: {report.exported}")
    print(f"  错误数量: {report.errors}")

    if report.error_details:
        print(f"\n错误详情:")
        for err in report.error_details[:20]:  # 最多显示 20 条
            print(f"  - {err}")
        if len(report.error_details) > 20:
            print(f"  ... 及其他 {len(report.error_details) - 20} 条")

    print(f"\n输出文件:")
    for f in sorted(args.output_dir.glob("*")):
        print(f"  {f.name}")

    return 0 if report.errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: 运行测试确认通过**

```bash
pytest tests/test_pipeline.py -v
```
Expected: PASS

- [ ] **Step 6: 运行完整测试套件**

```bash
pytest tests/ -v
```
Expected: 全部 PASS

- [ ] **Step 7: 提交**

```bash
git add cleaner/pipeline.py run_clean.py tests/test_pipeline.py
git commit -m "feat: add pipeline orchestrator + CLI entry point"
```

---

## 验证清单

全部 Task 完成后，逐项验证：

- [ ] `pytest tests/ -v` 全部通过
- [ ] `python run_clean.py` 在真实数据上运行成功，输出到 `cleaned/`
- [ ] `cleaned/cs_dataset.jsonl` 包含 ~2000 条记录
- [ ] `cleaned/cs_stats.json` 统计报告数据合理
- [ ] `cleaned/cs_vocabulary.txt` 包含司辰名、人名、书名等术语
- [ ] Lite 版不包含 desc 过短的条目
- [ ] 中英平行语料数量 > 0 且格式正确
