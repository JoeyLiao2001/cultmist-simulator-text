# -*- coding: utf-8 -*-
"""把 data/cleaned/cs_dataset.jsonl 转换为 writing-dna-skill 所需的 raw/ 语料目录。

按 category 拆分为 markdown 文件（中英对照），剔除空中文描述的条目，
并在 _meta/ 下生成语料级元数据（适配微文本语料，替代 per-article 标注）。
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "cleaned" / "cs_dataset.jsonl"
RAW = ROOT / "raw"
META = ROOT / "_meta"


def main():
    by_cat = defaultdict(list)
    total, skipped = 0, 0
    with SRC.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            total += 1
            zh_desc = (rec.get("desc") or "").strip()
            if not zh_desc:
                skipped += 1
                continue
            by_cat[rec["category"]].append(rec)

    RAW.mkdir(exist_ok=True)
    META.mkdir(exist_ok=True)

    meta_summary = {"source": str(SRC.relative_to(ROOT)), "total": total,
                    "skipped_empty_desc": skipped, "categories": {}}

    for cat, recs in sorted(by_cat.items()):
        lines = [f"# 密教模拟器语料：{cat}", "",
                 f"> 共 {len(recs)} 条。中文为清洗后译文（已去游戏指示），英文为原文。", ""]
        lengths = []
        for rec in recs:
            i18n = rec.get("i18n") or {}
            zh = i18n.get("zh") or {"name": rec["name"], "desc": rec["desc"]}
            en = i18n.get("en") or {}
            aspects = "、".join(rec.get("aspects") or []) or "（无）"
            lengths.append(len(zh["desc"]))
            lines += [f"## {zh['name']} `{rec['id']}`",
                      f"- 性相：{aspects}",
                      f"- 中文：{zh['desc']}"]
            if en.get("desc"):
                lines.append(f"- 英文（{en.get('name', '')}）：{en['desc']}")
            lines.append("")
        out = RAW / f"{cat}.md"
        out.write_text("\n".join(lines), encoding="utf-8")
        meta_summary["categories"][cat] = {
            "count": len(recs),
            "file": out.name,
            "desc_length_mean": round(sum(lengths) / len(lengths), 1),
            "desc_length_max": max(lengths),
        }
        print(f"{out.name}: {len(recs)} 条")

    (META / "corpus-summary.json").write_text(
        json.dumps(meta_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n总计 {total} 条，跳过空描述 {skipped} 条，输出 {len(by_cat)} 个类别文件")


if __name__ == "__main__":
    sys.exit(main())
