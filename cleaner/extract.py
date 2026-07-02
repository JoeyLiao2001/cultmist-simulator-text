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
    if not filepath.exists() or filepath.suffix != '.md':
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
