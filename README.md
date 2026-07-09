# Cultist Simulator Text Tools

A systematic toolkit for generating Cultist Simulator-style original characters (OCs) with narrative constellations &mdash; 7-8 item fragments scattered across different game object types, forming a distributed storytelling system.

**Not fanfiction. A methodology.**

---

## What this is

Three completed OCs, each with 8-11 carrier items (tools, books, locations, memories, rumours, rituals, dreams, paintings&hellip;), every card written in authentic Cultist Simulator prose, validated against 2,146 real game records, rendered as printable A4 pages.

Under the hood: a codified style guide (10 writing rules + 18 carrier-type voice profiles), an aspect registry derived from data analysis, a validation script, and a Writer-Editor dual-agent pipeline.

## What makes it different

- Textual style is not "prompt engineering" &mdash; it's a set of analyzable, teachable rules. Every rule has before/after examples.
- Characters are not profiles. They're distributed across objects and reconstructed by the reader through discovery.
- Writing quality is enforced by a validation layer: each card's aspects are checked against what the game actually does for that item type.
- The pipeline uses two LLM agents with separated roles: Writer drafts, Editor reviews (grammar -> style -> constellation consistency).

## Project structure

```
├── skill.md                    # Entry point — 6-phase workflow
├── CLAUDE.md                   # Project conventions
├── prompts/
│   ├── cs-writing-guide.md     # Complete style guide
│   ├── concept-generation.md   # Character concept template
│   └── page-design.md          # A4 page design tokens
├── knowledge/
│   ├── cs-lore/                # Explicit CS world knowledge
│   ├── occult-traditions/      # Real-world occult references
│   └── aspect-registry.md      # Per-category mandatory aspects
├── src/
│   ├── cleaner/                # Text cleaning pipeline (54 tests)
│   └── validate_aspects.py     # Aspect validation script
└── output/
    ├── ally.anya/              # Anya of Vologda — Winter/Knock Long
    ├── frizzelif/              # Frizzelif the Magpie — Moth Name
    └── parang-ludwig/          # Parang Ludwig — Edge/Moth/Grail Long
```

## Quick start

Open any `output/*/index.html` in a browser to see the finished page. To create a new OC:

1. Concept phase: define principle, tier, core idea
2. Constellation phase: select 7-8 carriers from the 28-type catalog
3. Card writing phase: Writer Agent generates drafts, Editor Agent reviews
4. Validation: `python src/validate_aspects.py`
5. Page generation: follow `prompts/page-design.md` visual tokens

---

# 密教模拟器文本工具

一个系统化的密教模拟器风格原创角色生成工具链。核心方法论：**叙事星座**——将人物故事拆碎，散落在 7-8 个不同游戏对象类型的碎片中，读者通过拼接碎片自行重构。

**不是同人。是方法。**

## 这是什么

三个完整的 OC 产出，每个配有 8-11 张载体卡牌（工具、书籍、地点、回忆、传闻、仪式、梦境、画作&hellip;&hellip;），所有文本用可验证的密教体规则写成，对 2,146 条游戏数据进行过性相校验，渲染为可打印的 A4 页面。

底层：一本完整的风格语法书（10 条写作规则 + 18 种载体语态）、基于数据分析的性相注册表、校验脚本、Writer-Editor 双 Agent 管道。

## 为什么与众不同

- 文本风格不是"调 prompt"——是可分析、可教学的规则。每条规则有改前/改后对照。
- 角色不是档案。角色是分布于物件中的碎片，读者通过发现来重构。
- 写作质量由校验层保障：每张卡的性相和同类游戏数据进行比对。
- 管道使用两个 LLM Agent，角色分离：Writer 出初稿，Editor 三道审校（语法 → 文风 → 星座一致性）。

## 项目结构

```
├── skill.md                    # 六阶段工作流入口
├── prompts/
│   ├── cs-writing-guide.md     # 完整风格语法书
│   ├── concept-generation.md   # 角色概念模板
│   └── page-design.md          # A4 页面设计令牌
├── output/
│   ├── ally.anya/              # 阿妮亚·沃洛格达 · 冬/启长生者
│   ├── frizzelif/              # 喜鹊·夫里泽里夫 · 蛾之具名者
│   └── parang-ludwig/          # Parang Ludwig · 刃/蛾/杯长生者
```

## 快速开始

浏览器打开任何 `output/*/index.html` 查看成品。创建新 OC：

1. 概念阶段：确定准则、位阶、核心概念
2. 星座规划：从 28 种载体中选 7-8 个
3. 卡牌生成：Writer Agent 初稿 → Editor Agent 审校
4. 性相校验：`python src/validate_aspects.py`
5. 生成页面：按 `prompts/page-design.md` 的视觉令牌组装

---

## License

MIT. The methodology, writing rules, and OC content are original work. Game data extracts are excluded from this repository.
