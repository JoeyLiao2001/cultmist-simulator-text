# -*- coding: utf-8 -*-
"""L1 表层语言分析（writing-dna-skill Step 3）。

对 cs_dataset.jsonl 的中文描述做词频、句式、标点统计，
结果写入 _meta/language_stats.json 并打印摘要。
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import jieba.posseg as pseg

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "cleaned" / "cs_dataset.jsonl"
OUT = ROOT / "_meta" / "language_stats.json"

SENT_SPLIT = re.compile(r"[。！？!?…]+")


def main():
    descs = []          # (category, zh_desc)
    with SRC.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            d = (rec.get("desc") or "").strip()
            if d:
                descs.append((rec["category"], d))

    nouns, verbs, advs, adjs = Counter(), Counter(), Counter(), Counter()
    sent_lens, desc_lens = [], []
    punct = Counter()
    person = Counter()
    per_cat_len = defaultdict(list)
    first_person, second_person, third_person = 0, 0, 0

    for cat, d in descs:
        desc_lens.append(len(d))
        per_cat_len[cat].append(len(d))
        # 句子切分
        for s in SENT_SPLIT.split(d):
            s = s.strip()
            if s:
                sent_lens.append(len(s))
        # 标点
        for ch, key in [("—", "破折号"), ("（", "括号"), ("(", "括号"),
                        ("“", "引号"), ("\"", "引号"), ("…", "省略号"),
                        ("、", "顿号"), ("；", "分号"), ("：", "冒号")]:
            punct[key] += d.count(ch)
        # 人称
        if re.search(r"我们|我", d):
            first_person += 1
        if re.search(r"你们|你", d):
            second_person += 1
        if re.search(r"他们|她们|它们|他|她|它", d):
            third_person += 1
        # 词性
        for w, flag in pseg.cut(d):
            if len(w) < 2:
                continue
            if flag.startswith("n"):
                nouns[w] += 1
            elif flag.startswith("v"):
                verbs[w] += 1
            elif flag.startswith("d"):
                advs[w] += 1
            elif flag.startswith("a"):
                adjs[w] += 1

    n = len(descs)
    sent_lens_sorted = sorted(sent_lens)
    stats = {
        "corpus_size": n,
        "desc_length": {
            "mean": round(sum(desc_lens) / n, 1),
            "median": sorted(desc_lens)[n // 2],
            "max": max(desc_lens),
        },
        "sentence": {
            "count": len(sent_lens),
            "mean_len": round(sum(sent_lens) / len(sent_lens), 1),
            "median_len": sent_lens_sorted[len(sent_lens) // 2],
            "short_ratio_le15": round(sum(1 for x in sent_lens if x <= 15) / len(sent_lens), 3),
            "long_ratio_ge50": round(sum(1 for x in sent_lens if x >= 50) / len(sent_lens), 3),
            "sentences_per_desc": round(len(sent_lens) / n, 2),
        },
        "punctuation_per_100desc": {k: round(v / n * 100, 1) for k, v in punct.most_common()},
        "person_ratio": {
            "第一人称": round(first_person / n, 3),
            "第二人称": round(second_person / n, 3),
            "第三人称": round(third_person / n, 3),
        },
        "per_category_mean_len": {k: round(sum(v) / len(v), 1)
                                  for k, v in sorted(per_cat_len.items())},
        "top_nouns": nouns.most_common(100),
        "top_verbs": verbs.most_common(50),
        "top_adverbs": advs.most_common(30),
        "top_adjectives": adjs.most_common(30),
    }
    OUT.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"语料 {n} 条 / {len(sent_lens)} 句")
    print(f"句长：均值 {stats['sentence']['mean_len']} 字，中位 {stats['sentence']['median_len']} 字，"
          f"短句(≤15)占 {stats['sentence']['short_ratio_le15']:.0%}，长句(≥50)占 {stats['sentence']['long_ratio_ge50']:.0%}")
    print(f"人称：我 {stats['person_ratio']['第一人称']:.0%} / 你 {stats['person_ratio']['第二人称']:.0%} / 三 {stats['person_ratio']['第三人称']:.0%}")
    print("标点(每百条)：", stats["punctuation_per_100desc"])
    print("高频名词：", "、".join(w for w, _ in nouns.most_common(30)))
    print("高频动词：", "、".join(w for w, _ in verbs.most_common(25)))
    print("高频副词：", "、".join(w for w, _ in advs.most_common(20)))
    print("高频形容词：", "、".join(w for w, _ in adjs.most_common(20)))


if __name__ == "__main__":
    sys.exit(main())
