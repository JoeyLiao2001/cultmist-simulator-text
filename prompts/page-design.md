# 展示页设计框架

OC 叙事星座的最终产出是一张**自包含的 A4 HTML 页面**（210×297mm），可直接打印或另存为 PDF。

---

## 设计原则

**页面身份**：不是档案、不是报告、不是海报。是一张来自 1920 年代秘教出版社的散页——某个人关于 OC 所做记录的一页。神秘但克制，优雅但不装饰。

**主体是文字**：sprite 插图是辅助，不是主角。引文和小传的字号 > 插图尺寸。

---

## 视觉令牌

### 颜色

| 令牌 | 色值 | 用途 |
|------|------|------|
| 纸色 | `#ece4d5` | 页面底色 |
| 暖墨 | `#2c2418` | 正文、物品名称 |
| 冷墨 | `#3c4048` | 角色名（与铁路油墨、冬之灰呼应） |
| 灰墨 | `#5a4e3e` | 引文、描述文字 |
| 标签灰 | `#908070` | 类型标签、二级信息 |
| 淡灰 | `#6b5e4e` | 物品描述 |

### 背景纹理

```
repeating-linear-gradient(45deg, transparent, transparent 3.5px, rgba(180,160,130,0.07) 3.5px, rgba(180,160,130,0.07) 4.5px),
repeating-linear-gradient(-45deg, transparent, transparent 3.5px, rgba(180,160,130,0.07) 3.5px, rgba(180,160,130,0.07) 4.5px)
```

来源：CS 人物肖像背景的菱形小格纹。只作为纸面的微弱肌理，不喧宾夺主。

### 字体

| 层级 | 字号 | 字重 | 说明 |
|------|------|------|------|
| 角色名 | 15pt | 400 | 冷墨色，宽字距（0.1em） |
| 引文 | 9pt | italic | 斜体，行距 1.9 |
| 小传 | 8pt | normal | 行距 2.2，段首缩进 2em |
| 物品名 | 8pt | 600 | tier 2；tier 3 用 7pt |
| 物品描述 | 7pt | normal | tier 2；tier 3 用 6.2pt |
| 类型标签 | 5.5pt | uppercase | 宽字距（0.2em），标签灰 |

---

## 布局结构

从上到下三区块，自然文档流，无 flex 拉伸：

```
┌──────────────────────────────────┐
│ [肖像 36mm]  角色名               │  ← hero 区
│              Long · Elegiast      │
│              引文                 │
│              [[冬]] [[启]]        │
│                                  │
│   小传段落一                       │  ← 小传区
│   小传段落二                       │     4段叙事
│   小传段落三                       │
│   小传段落四                       │
│                                  │
│ [图] 书籍  [图] 工具  [图] 地点   │  ← 物品区
│ 《无名日记》 哭丧人披肩 沃洛格达   │     tier 2: 50%宽
│  desc...    desc...    desc...   │     tier 3: 33%宽
│  文献冬秘史  工具冬     冬        │
│                                  │
│ [小图] 影响   [小图] 传闻  [小图]  │
│  预忘         打听不得    维奥莱特 │
└──────────────────────────────────┘
```

- **hero**：左侧肖像 36×36mm，右侧名字+引文+原则图标。flex 横排，gap 6mm
- **小传**：4 段叙事文字，max-width 150mm 居中，不提及星座中任何具体物品
- **物品**：flex-wrap 排列。tier 2 占 50% 宽，sprite 20×20mm。tier 3 占 33% 宽，sprite 15×15mm。每件：左侧缩略图 + 右侧文字块

### 间距

| 区域 | 值 |
|------|-----|
| 页边距 | 14mm |
| hero 与 小传 | 8mm |
| 小传与物品 | 5mm |
| 物品行间距 | 5mm（垂直）/ 6mm（水平） |

---

## 插图规则

### Sprite 来源优先级

1. 专门为该 OC 生成的 sprite（放入 `assets/` 目录）
2. 若无，**复用游戏原 sprite**——选择同原则 / 同类别的最接近者。例：缺工具 sprite → 使用 `toolwinterb.png`（游戏中的冬之骨笛）。禁止复用 OC 本人的肖像
3. 不显示任何占位符 icon

### Sprite 尺寸

| 层级 | 尺寸 |
|------|------|
| Hero 肖像 | 36×36mm |
| Tier 2 物品 | 20×20mm |
| Tier 3 物品 | 15×15mm |

---

## 性相图标

每件物品显示**完整的性相图标集**，包括类别性相和原则性相：

| 类别性相 | 图标 | 适用对象 |
|----------|------|----------|
| 文献 | `books.png` | 书籍 |
| 工具 | `tool.png` | 工具 |
| 影响 | `influence.png` | 影响 |
| 传闻 | `rumour.png` | 传闻、流言 |
| 仪式 | `ritual_icon.png` | 仪式 |
| — | （无需图标） | 地点、召唤物、回忆（无通用类别图标，仅显示原则图标） |

图标尺寸：hero 22×22px，物品 15×15px，透明度 0.5。

原则性相按 CS 准则体系分配：冬/启/蛾/秘史等，图标从游戏 sprite 中提取。

---

## 打印规则

```css
@media print {
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body { background: #d5cdbd; padding: 0; }
  .page { box-shadow: none; }
}
```

页面必须 `height: 297mm`（固定高度，不用 min-height），`overflow: hidden`。

---

## 文件结构

```
output/{oc-name}/
├── index.html          ← 自包含 HTML，数据内嵌
└── assets/
    ├── sprite_*.png    ← 生成的/复用的 sprite
    ├── *.png           ← 原则图标（winter/knock/moth/secrethistories）
    └── *.png           ← 类别图标（books/tool/influence/rumour/ritual_icon）
```

数据全量内嵌于 `<script>` 的 DATA 常量。换 OC 只需替换 DATA 和 `assets/` 中的 sprite 文件。
