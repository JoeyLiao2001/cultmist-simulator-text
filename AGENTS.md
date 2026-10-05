# Cultist Simulator 文本工具

密教模拟器结构化知识库、风格分析与 OC 创作工具。核心方法论：叙事星座——将人物故事拆碎，散落在 7-8 个不同游戏对象类型的碎片中（碎片的世界焦点优先，人物只是线索）。六阶段流程：概念 → 星座 → 双 Agent 写作 → 性相校验 → A4 页面 → 完整性审查。

## 项目结构

| 路径 | 说明 |
|------|------|
| skill.md | 六阶段工作流 + 准则速查（英文） |
| prompts/cs-writing-guide.md | ★ 唯一文风权威文件（v3：先把话说通 + 游戏原文统计特征 + 15 种载体叙述者表 + 编辑技法 + 深层共识 + 写后自查。数据源自 1,950 条游戏微文本蒸馏） |
| prompts/concept-generation.md | 角色概念 JSON 模板 |
| prompts/page-design.md | A4 页面设计令牌 |
| knowledge/cs-lore/ | 密教宇宙显式知识库 |
| knowledge/occult-traditions/ | 神秘学综述 + 200+ 概念卡片，OC 构思时必须搜索 |
| knowledge/aspect-registry.md | 强制性相注册表（基于 2,146 条数据） |
| src/validate_aspects.py | 性相校验脚本 |
| src/build_raw_corpus.py | 语料转换脚本（data/ → raw/） |
| src/analyze_language_dna.py | L1 表层语言统计脚本 |
| tools/writing-dna-skill/ | 写作蒸馏器（开源 skill），OC 构思时可选调用其六层次蒸馏模板 |
| _meta/ | 文风蒸馏证据归档（DNA 四件套 + 统计数据 + 交叉验证报告），执行时不加载 |
| raw/ | 语料目录（14 类 markdown），文风蒸馏输入，执行时不加载 |
| references/sprites/ | 游戏版权 sprite 文件（不纳入版本控制） |
| output/ | OC 产出目录（不纳入版本控制） |

## 硬约束

- knowledge/ 不包含代码，src/ 不包含 OC 设定
- tools/ 存放第三方工具（如 writing-dna-skill），不混入知识库
- data/ 和 references/sprites/ 不在版本库中（游戏版权数据）
- 不创造新的准则或司辰
- 根目录 `.env` 中的 OPENROUTER_API_KEY 仅供 `src/review_layout.py` 识图评审使用；处理文字或代码时严禁调用、读取或转发该 Key
- 长生者及以上层级必须有代价或印记
- OC 标志物在全星座中出现不超过两次
- 叙事星座内容不重叠
- 不编造 lore——所有锚点必须追溯至 knowledge/cs-lore/
