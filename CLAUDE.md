# Cultist Simulator 文本工具

密教模拟器与司辰之书结构化知识库、风格分析与创作工具。

## 项目结构

| 路径 | 属性 | 说明 |
|------|------|------|
| data/raw/ | 只读 | 原始抓取的密教模拟器文本（14类别） |
| data/cleaned/ | 只读 | 清洗后的结构化数据集 |
| knowledge/cs-lore/ | 人工维护 | 密教宇宙显式知识库 |
| knowledge/occult-traditions/ | 人工维护 | 真实世界神秘学知识 |
| src/ | 可编辑 | 所有源代码 |
| prompts/ | 可编辑 | 生成 prompt 模板 |
| references/ | 可编辑 | 风格指南、创作访谈参考 |
| output/ | 可编辑 | 用户生成的实体卡牌和故事 |
| tests/ | 可编辑 | 单元测试与集成测试 |
| docs/ | 可编辑 | 设计文档与实施计划 |

## 硬约束

### 数据不可变
- data/raw/ 和 data/cleaned/ 中的任何文件不得手动编辑
- 如需更正清洗结果，修改 src/cleaner/ 中的逻辑后重新运行

### 知识库与代码隔离
- knowledge/ 是人写的结构化知识，不包含代码
- src/ 是通用工具代码，不包含具体 OC 设定
- output/ 是创作内容，不包含可复用代码

### 生成流程
1. 用户描述需求（性相、类别、创作方向）
2. 检索 knowledge/cs-lore/ 中的相关设定
3. 检索 knowledge/occult-traditions/ 中的相关文化知识
4. 检索 data/cleaned/ 中的风格参考文本
5. 使用 prompts/ 中的模板进行两步生成（概念→卡牌描述）
6. 用户审核、编辑、确认
7. 输出保存到 output/entities/

## 技术栈
- Python 3.10+
- 清洗: pyyaml, jsonlines, pytest
- 生成: Claude API（通过 skill 调用）
- 风格指标: numpy

## 当前进度
- [x] 文本清洗 pipeline（2,146 条）
- [ ] cs-lore 知识库（进行中）
- [ ] occult-traditions 知识库（进行中）
- [ ] skill 定义
- [ ] 初始 OC 创作
