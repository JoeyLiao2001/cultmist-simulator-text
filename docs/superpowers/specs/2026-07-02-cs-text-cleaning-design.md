# Cultist Simulator 文本清洗工具 — 设计文档

## 概述

将散落在 14 个目录、约 2,145 个 Markdown 文件中的密教模拟器游戏文本，清洗为结构清晰、信息完整、无冗余的 JSONL 数据集，同时产出中英平行语料和统计报告。

## 源数据格式

每个 `.md` 文件的结构：

```
---
element_id: "dread"
category: influences
source_file: "abilities.json"
tags: [cultist-simulator, influences]
---

# 中文名称
> `element_id`

> 叙事描述文本（核心语料）。

**Aspects:** [[刃]], [[诱发绝望]], ...
**Slots:** 忆起
**Requirements for Recipes:** [[...]], ...
**Effect of Recipes:** [[...]], ...

---

## 🌐 多语言对照

| 语言 | Label | Description |
|------|-------|-------------|
| 中文 | ... | ... |
| English | ... | ... |
| ...
```

## 目标 Schema（JSONL，每行一条）

```json
{
  "id": "dread",
  "name": "恐惧",
  "desc": "我已经见得太多了。...",
  "category": "influences",
  "aspects": ["刃", "诱发绝望", "影响", "健康欠佳", "回忆"],
  "i18n": {
    "en": {"name": "Dread", "desc": "I've seen too much. ..."},
    "ja": {"name": "恐怖", "desc": "..."},
    "ru": {"name": "Ужас", "desc": "..."},
    "de": {"name": "Grauen", "desc": "..."}
  },
  "meta": {
    "desc_length": 39,
    "has_game_instruction": false,
    "has_template_var": false
  }
}
```

### 字段说明

| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| `id` | string | frontmatter `element_id` | 唯一标识 |
| `name` | string | 中文 `Label` | 实体中文名 |
| `desc` | string | 中文 `Description` | 核心叙事文本，训练语料 |
| `category` | string | frontmatter `category` | 14 类之一，用于条件生成 |
| `aspects` | string[] | body `**Aspects:**` | `[[]]` 清洗为纯字符串数组 |
| `i18n` | object | 多语言对照表 | en/ja/ru/de，各有 name + desc |
| `meta.desc_length` | int | 计算 | 中文描述字符数 |
| `meta.has_game_instruction` | bool | desc 匹配 | 是否含 `[...]` 游戏指令 |
| `meta.has_template_var` | bool | desc 匹配 | 是否含 `#...#` 模板变量 |

### 删除的字段及理由

| 字段 | 理由 |
|------|------|
| `tags` | 恒为 `[cultist-simulator, <category>]`，模板值无信息量 |
| `source_file` | 爬取元数据，非游戏内容 |
| `Requirements for Recipes` | 纯游戏机制，`[[...]]` 配方列表无叙事价值 |
| `Effect of Recipes` | 同上 |
| `Decay from` | 游戏内部状态机 |
| `In Decks` | 游戏内部牌组配置 |
| 多语言表下方 `Slots` | 与 body `Slots` 重复 |
| 正文内嵌 `` `id` `` | 与 `element_id` 重复 |

### 清洗转换规则

1. **`[[]]` 解包**: `[[刃]]` → `"刃"`，`[[]]` → 丢弃
2. **游戏指令剥离**: desc 中 `[...]` 内容移除并设 `has_game_instruction: true`
3. **模板变量标记**: desc 中 `#VARIABLE#` 保留原文，设 `has_template_var: true`
4. **空描述**: 保留记录，设 `desc_length: 0`，由下游过滤
5. **英文截断修复**: 部分 `i18n.en.desc` 在源文件中被截断（多语言表列宽限制），从英文源数据可尝试补全

## 输出文件

```
cleaned/
├── cs_dataset.jsonl        # 全量，~2100+ 条
├── cs_dataset_lite.jsonl   # 仅中文核心字段，
│                           #   过滤 desc_length < 10
├── cs_parallel_zh_en.jsonl # 中英平行语料，
│                           #   过滤 desc_length == 0
├── cs_stats.json           # 统计报告
└── cs_vocabulary.txt       # 术语/人名/地名/司辰名去重列表
```

## Pipeline 结构

```
源文件 (.md)
    │
    ▼
Extract  ─── 遍历 14 个目录，解析 YAML frontmatter + Markdown body
    │
    ▼
Parse    ─── 正则提取 Aspects / Slots / Recipes / 多语言表
    │
    ▼
Clean    ─── [[]] 解包、游戏指令剥离、模板变量检测、空值处理
    │
    ▼
Validate ─── schema 校验、去重、完整性检查
    │
    ▼
Export   ─── JSONL × 3 + stats.json + vocabulary.txt
```

## 技术选型

- **语言**: Python 3.10+
- **依赖**: `pyyaml` (frontmatter), `jsonlines` (输出), `regex` (Unicode 感知)
- **无外部服务依赖**，完全离线可运行

## 非目标（v1 不做）

- 数据增强 / 风格变体生成
- 基于 Wiki-link 的实体关系图谱
- 训练配方文档
- Web UI / 可视化
