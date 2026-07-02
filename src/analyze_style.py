#!/usr/bin/env python3
"""Analyze CS text style from cleaned dataset — produce data-driven style guide."""

import json
import re
from collections import Counter
from pathlib import Path

DATASET = Path(__file__).parent.parent / "data" / "cleaned" / "cs_dataset.jsonl"
OUTPUT = Path(__file__).parent.parent / "references" / "style-guide.md"

# Load data
records = []
with open(DATASET, encoding="utf-8") as f:
    for line in f:
        records.append(json.loads(line))

# Filter to records with actual descriptions
with_desc = [r for r in records if r["meta"]["desc_length"] > 0]
print(f"Total: {len(records)}, with desc: {len(with_desc)}")

# ========== 1. Length distribution ==========
lengths = sorted(r["meta"]["desc_length"] for r in with_desc)
pcts = [10, 25, 50, 75, 90, 95]
length_pct = {}
for p in pcts:
    idx = int(len(lengths) * p / 100)
    length_pct[p] = lengths[idx]

# ========== 2. Function word frequency ==========
function_words = ["之", "者", "其", "此", "于", "为", "所", "斯", "已", "将", "与", "以", "而", "则", "乃", "亦", "非", "皆"]
fw_counter = Counter()
total_chars = 0
for r in with_desc:
    desc = r["desc"]
    total_chars += len(desc)
    for fw in function_words:
        fw_counter[fw] += desc.count(fw)

# ========== 3. Sentence patterns ==========
patterns = {
    "据说": 0, "某一": 0, "某种": 0, "无人知晓": 0,
    "……": 0, "已被": 0, "将": 0, "已": 0,
    "可能是": 0, "据说……": 0, "——": 0,
}
for r in with_desc:
    desc = r["desc"]
    for p in patterns:
        patterns[p] += desc.count(p)

# ========== 4. First-person vs third-person ==========
first_person = sum(1 for r in with_desc if "我" in r["desc"])
third_person = sum(1 for r in with_desc if "他" in r["desc"] or "她" in r["desc"])

# ========== 5. Category stats ==========
cat_stats = {}
for r in with_desc:
    cat = r["category"]
    if cat not in cat_stats:
        cat_stats[cat] = {"count": 0, "total_len": 0, "lengths": []}
    cat_stats[cat]["count"] += 1
    cat_stats[cat]["total_len"] += r["meta"]["desc_length"]
    cat_stats[cat]["lengths"].append(r["meta"]["desc_length"])

# ========== 6. Opening words ==========
opening_counter = Counter()
for r in with_desc:
    desc = r["desc"]
    if len(desc) >= 2:
        opening_counter[desc[:2]] += 1

# ========== 7. Ending characters ==========
ending_counter = Counter()
for r in with_desc:
    desc = r["desc"]
    if desc:
        ending_counter[desc[-1]] += 1

# ========== 8. Aspect-specific vocabulary ==========
aspect_vocab = {}
for r in with_desc:
    for asp in r.get("aspects", []):
        if asp not in aspect_vocab:
            aspect_vocab[asp] = Counter()
        # Extract 2-char bigrams from desc
        desc = r["desc"]
        for i in range(len(desc) - 1):
            bigram = desc[i:i+2]
            aspect_vocab[asp][bigram] += 1

# ========== Write report ==========
lines = []
lines.append("# 密教模拟器中文风格量化报告\n")
lines.append(f"> 数据来源：`cs_dataset.jsonl`，{len(with_desc)} 条有效叙事文本\n")

lines.append("## 一、描述长度分布\n")
lines.append("| 分位数 | 字数 |")
lines.append("|--------|------|")
for p in pcts:
    lines.append(f"| P{p} | {length_pct[p]} |")
lines.append(f"\n- 最短：{lengths[0]} 字")
lines.append(f"- 最长：{lengths[-1]} 字")
lines.append(f"- 中位：{length_pct[50]} 字")
lines.append(f"- 平均：{sum(lengths)/len(lengths):.1f} 字\n")

lines.append("## 二、文言虚词频率\n")
lines.append("| 虚词 | 出现次数 | 每千字频率 |")
lines.append("|------|---------|-----------|")
per_k = total_chars / 1000
for fw, count in fw_counter.most_common():
    rate = count / per_k if per_k > 0 else 0
    lines.append(f"| {fw} | {count} | {rate:.1f} |")

lines.append(f"\n**虚词总密度：{sum(fw_counter.values())/total_chars*100:.1f}%**（所有文言虚词占全部字符的百分比）\n")

lines.append("## 三、句式模式\n")
lines.append("| 模式 | 出现次数 | 占比 |")
lines.append("|------|---------|------|")
n = len(with_desc)
for p, count in sorted(patterns.items(), key=lambda x: -x[1]):
    if count > 0:
        lines.append(f"| `{p}` | {count} | {count/n*100:.1f}% |")

lines.append(f"\n## 四、叙事视角\n")
lines.append(f"- 第一人称（含\"我\"）：{first_person} 条（{first_person/n*100:.1f}%）")
lines.append(f"- 第三人称（含\"他/她\"）：{third_person} 条（{third_person/n*100:.1f}%）\n")

lines.append("## 五、各类别描述长度\n")
lines.append("| 类别 | 数量 | 平均长度 | 中位长度 |")
lines.append("|------|------|---------|---------|")
for cat in sorted(cat_stats.keys()):
    s = cat_stats[cat]
    avg = s["total_len"] / s["count"]
    sorted_lens = sorted(s["lengths"])
    med = sorted_lens[len(sorted_lens) // 2]
    lines.append(f"| {cat} | {s['count']} | {avg:.1f} | {med} |")

lines.append(f"\n## 六、最高频开头二字\n")
lines.append("| 开头 | 次数 |")
lines.append("|------|------|")
for phrase, count in opening_counter.most_common(20):
    lines.append(f"| {phrase} | {count} |")

lines.append(f"\n## 七、结尾字符分布\n")
lines.append("| 结尾 | 次数 | 占比 |")
lines.append("|------|------|------|")
for char, count in ending_counter.most_common(15):
    lines.append(f"| {char} | {count} | {count/n*100:.1f}% |")

lines.append(f"\n## 八、风格规则总结\n")
lines.append(f"基于以上数据，密教模拟器中文文本的风格规则：\n")
lines.append(f"1. **长度**：目标 15-80 字。中位 {length_pct[50]} 字，90% 在 {length_pct[90]} 字以内")
lines.append(f"2. **虚词密度**：每千字约 {sum(fw_counter.values())/per_k:.0f} 个文言虚词。最常用：{', '.join([f'{w}({c}次)' for w, c in fw_counter.most_common(6)])}")
lines.append(f"3. **句式**：{first_person/n*100:.0f}% 用第一人称，{third_person/n*100:.0f}% 用第三人称。高频句式：{', '.join([f'`{p}`({c}次)' for p, c in sorted(patterns.items(), key=lambda x: -x[1])[:5] if c > 0])}")
lines.append(f"4. **结尾**：最常见的句尾字符是 `{ending_counter.most_common(1)[0][0]}`（{ending_counter.most_common(1)[0][1]}条，{ending_counter.most_common(1)[0][1]/n*100:.0f}%）")
lines.append(f"5. **克制性**：不用语气词（吧呢啊），不用解释性语言。暗示多于明示\n")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(lines), encoding="utf-8")
print(f"\nReport written to {OUTPUT}")
