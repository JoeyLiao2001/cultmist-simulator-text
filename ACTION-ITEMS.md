# Action Items & Status

## 项目目标

创建一个开源工具链，用于生成密教模拟器（Cultist Simulator）风格的世界观实体。核心定位：**小数据量中文文学风格的结构化生成方法论**——以密教模拟器/司辰之书为案例，展示可复现的完整管道。

## 进展总览

| 模块 | 状态 | 质量 |
|------|------|------|
| 文本清洗 pipeline | ✅ 完成 | 可靠 — 54测试通过 |
| 项目结构重构 | ✅ 完成 | data/src/knowledge/output 四层 |
| cs-lore 知识库 | ✅ 完成 | 可靠 — 直接从数据集提取 |
| cs-lore 精选片段 | ✅ 完成 | 九个准则全覆盖 |
| occult-traditions 卡片 | ✅ 220张 | ⚠️ 未验证 — agent凭记忆写，未web search |
| occult-traditions 长文 | ✅ 5篇 | ⚠️ 未验证 — 同上 |
| deep-research 琐罗亚斯德教 | ✅ 完成 | 可靠 — 16主张经3票对抗验证 |
| skill.md | ✅ 完成 | 可用于生成 |
| prompts | ✅ 完成 | 概念生成 + 卡牌渲染 |
| Book of Hours 文本 | ❌ 放弃 | Rowenarium/维基/GitHub 均不可用。仅用 CS 数据（1,746条） |
| references/style-guide.md | ❌ 未开始 | |
| 生成第一个 OC | ❌ 未开始 | |

## 立即待办

### P0 — 必须做

1. **[ ] 验证 220 张神秘学卡片**
   - 当前状态：卡片是 agent 凭训练记忆写的，可能含事实错误
   - 正确做法：用 `deep-research` skill 逐批验证
   - 每次跑一个传统（30-45分钟），产出验证报告，修正卡片内容
   - 优先级：琐罗亚斯德教系卡片 > 俄耳甫斯系 > 赫尔墨斯系 > 炼金术系 > 其余

2. **[ ] 爬取司辰之书（Book of Hours）文本**
   - 参考: `references/book-of-hours-data-sources.md`
   - 目标：扩充数据集到 5000+ 条
   - 爬取后运行 `src/cleaner/` 的清洗 pipeline 处理

3. **[ ] 生成第一个 OC**
   - 主题：冬性相悼歌诗人长生者
   - 使用 skill.md 中定义的两步流程
   - 测试整个管道是否可用

### P1 — 应该做

4. **[ ] 完成 references/style-guide.md**
   - 从数据集统计出句长分布、虚词频率、句式指纹
   - 作为生成时的量化参考

5. **[ ] 补齐 occult-traditions 中的深度参考**
   - 当前可用：深研验证的琐罗亚斯德教
   - 还需要深研：俄耳甫斯/希腊、赫尔墨斯主义、炼金术、酒神
   - 每次用 `deep-research` skill，不要用普通 agent

6. **[ ] 更新 skill.md**
   - 当前 skill.md 引用了未验证的卡片——等卡片验证后更新引用

### P2 — 可以延后

7. **[ ] 训练配方文档**
   - QLoRA + Qwen 的数据量估算和训练脚本
   - 等数据集扩充到 5000+ 条后再做

8. **[ ] 更多性相的精选片段索引**
   - 当前每个准则一个 fragments/ 文件
   - 可以加上跨准则主题（如"代价与印记""飞升之路"）

## 关键约束（写进 CLAUDE.md 的）

- `data/raw/` 和 `data/cleaned/` 只读
- `knowledge/` 人工维护，不包含代码
- `output/` 创作空间
- 不创造新的准则或司辰
- occult-traditions 内容必须经过 web search 验证，禁止 agent 凭记忆写
- 长生者及以上层级的实体必须有代价或印记

## 当前文件结构

```
cultist-simulator-text/
├── data/
│   ├── raw/                   # 只读 — 14目录原始文本
│   └── cleaned/               # 只读 — 2,146条清洗后JSONL
├── knowledge/
│   ├── cs-lore/
│   │   ├── principles.md
│   │   ├── hours.md
│   │   ├── hierarchy.md
│   │   └── fragments/         # 9个性相精选原文
│   └── occult-traditions/
│       ├── references/        # 深研验证产出
│       └── cards/             # 220张素材卡片 ⚠️
├── src/cleaner/               # 清洗pipeline · 54测试
├── prompts/
│   ├── concept-generation.md
│   └── card-rendering.md
├── output/entities/           # OC产出目录
├── skill.md
├── CLAUDE.md
├── run_clean.py
└── requirements.txt
```

## 如何继续

在新的对话中，让 Claude 读取这个文件和 `CLAUDE.md`：

```
请阅读 ACTION-ITEMS.md 和 CLAUDE.md 了解项目状态，然后从 P0 第一项开始工作。
```
