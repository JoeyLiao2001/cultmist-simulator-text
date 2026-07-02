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
