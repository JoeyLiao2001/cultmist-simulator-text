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
