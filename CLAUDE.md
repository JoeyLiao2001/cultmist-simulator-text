# Cultist Simulator 文本工具

密教模拟器结构化知识库、风格分析与 OC 创作工具。核心方法论：叙事星座——将人物故事拆碎，散落在 7-8 个不同游戏对象类型的碎片中。六阶段流程：概念 → 星座 → 双 Agent 写作 → 性相校验 → A4 页面 → 完整性审查。

## 项目结构

| 路径 | 说明 |
|------|------|
| skill.md | 六阶段工作流 + 准则速查（英文） |
| prompts/cs-writing-guide.md | 完整风格语法书（10 条规则 + 语态指南 + 七维度 + 实操技法） |
| prompts/concept-generation.md | 角色概念 JSON 模板 |
| prompts/page-design.md | A4 页面设计令牌 |
| knowledge/cs-lore/ | 密教宇宙显式知识库 |
| knowledge/occult-traditions/ | 真实世界神秘学知识 |
| knowledge/aspect-registry.md | 强制性相注册表（基于 2,146 条数据） |
| src/validate_aspects.py | 性相校验脚本 |
| output/ | OC 产出目录（不纳入版本控制） |

## 硬约束

- knowledge/ 不包含代码，src/ 不包含 OC 设定
- data/ 和 references/sprites/ 不在版本库中（游戏版权数据）
- 不创造新的准则或司辰
- 长生者及以上层级必须有代价或印记
- OC 标志物在全星座中出现不超过两次
- 叙事星座内容不重叠
- 不编造 lore——所有锚点必须追溯至 knowledge/cs-lore/
