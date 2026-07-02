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
