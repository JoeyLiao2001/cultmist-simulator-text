# Book of Hours（司辰之书）数据来源调研报告

> 调研日期：2026-07-02
> 目的：为社区数据集项目评估《司辰之书》游戏文本数据的获取途径

---

## 一、现有数据来源总览

| 来源 | 类型 | 完整度 | 可编程获取 | 中文支持 |
|------|------|--------|------------|----------|
| 游戏本体 JSON 文件 | 原始数据 | **最完整** | 是（Python/JSON解析） | 是（含官方简体中文本地化） |
| Rowenarium | 在线数据浏览器 | 高（与游戏文件同步） | 间接（HTML解析） | 否（仅英文ID/标签） |
| Fandom 英文维基 | 社区维基 | 较高（1,564 条目） | 可爬取（但反爬严格） | 否 |
| 灰机中文维基 | 社区维基 | 中等（2,455 页面） | 可爬取 | 是 |
| Secret Histories API Mod | 运行时REST API | 高（实时游戏状态） | 是（HTTP API） | 取决于游戏本地化 |
| Steam 玩家自制工具 | 解析玩家日志 | 中（仅玩家已发现内容） | 是（CSV输出） | 否 |
| NexusMods | 成品文本mod | 低（仅部分文本替换） | 否 | 部分（有中文本地化mod） |

---

## 二、游戏文件结构详解

### 2.1 文件路径
游戏数据位于 Steam 安装目录下：

```
Book of Hours/bh_Data/StreamingAssets/bhcontent/core/
```

另外有独立的中文本地化文件夹（与英文同步维护）：
```
Book of Hours/bh_Data/StreamingAssets/bhcontent/loc_zh-hans/
```

### 2.2 核心目录结构

```
core/
├── elements/          # 游戏实体定义（最大类别）
│   ├── _aspects.json          # 性相定义（13种准则及子属性）
│   ├── tomes.json             # 书籍定义（~281本）
│   ├── skills.json            # 技能定义
│   ├── skills_r.json          # 额外技能
│   ├── abilities.json         # 灵魂元素（九大魂质）
│   ├── memories/              # 记忆定义（普通、天气、Numen）
│   ├── visitors.json          # 访客/人物定义
│   ├── resources.json         # 资源物品
│   ├── comforts.json          # 舒适品/家具
│   └── ...
├── recipes/           # 配方定义（制作、阅读、交谈等）
├── decks/             # 牌组定义（书籍目录、天气、聊天等）
├── verbs/             # 行动/工作站定义
├── endings/           # 结局定义
├── legacies/          # 初始出身定义
├── cultures/          # 语言/本地化 UI 标签
│   ├── en/            # 英语
│   ├── ru/            # 俄语
│   └── zh-hans/       # 简体中文
└── achievements/      # 成就定义
```

### 2.3 JSON 数据格式（以书籍为例）

每一本书的 JSON 结构如下：

```json
{
  "ID": "t.travelsontherhine",
  "Label": "Travels on the Rhine",
  "Desc": "选中书时的描述文本...",
  "aspects": {
    "mystery.rose": 6,
    "cost.tally": 2,
    "codex": 1
  },
  "xexts": {
    "reading.rose.intro": "初读中...文本",
    "reading.rose": "读完后文本",
    "mastering.rose": "精通后文本"
  },
  "xtriggers": {
    "mastering.rose": [{ "id": "x.stonestories", "morpheffect": "spawn" }],
    "reading.rose": [{ "id": "mem.impulse", "morpheffect": "spawn" }]
  },
  "inherits": "_book",
  "unique": true,
  "audio": "Book"
}
```

**关键文本字段说明：**
- `Label`：显示名称
- `Desc`：卡片描述/提示文本
- `xexts`：阅读叙事文本（核心文字内容），包含 intro（初读中）、正文（阅读后）、mastering（精通后）
- `xtriggers`：阅读/精通后生成的物品（记忆、技能教训等）

### 2.4 与 Cultist Simulator 的结构对比

BoH 与 CS 使用**相同的游戏引擎**（Secret Histories Engine / Unity），因此 JSON 结构高度相似：
- CS：`cultist_simulator_Data/StreamingAssets/content/core/`
- BoH：`bh_Data/StreamingAssets/bhcontent/core/`
- 两者都使用 `elements/`、`recipes/`、`decks/`、`verbs/` 等子目录
- JSON 字段命名一致：`ID`、`Label`、`Desc`、`aspects`、`xexts`、`xtriggers`、`inherits`
- 主要区别：BoH 文本体量更大（~281本有文本的书 vs CS 的文本量），实体类型更多（新增了记忆 Memory 系统、访客系统、烹饪系统等）

---

## 三、各数据来源详细评估

### 3.1 游戏本体 JSON 文件（推荐首选）

**来源路径：**
```
{SteamLibrary}/steamapps/common/Book of Hours/bh_Data/StreamingAssets/bhcontent/core/
```

**包含的文本类别：**

| 类别 | 估计数量 | 文本内容 |
|------|----------|----------|
| 书籍（Tomes） | ~281 本 | 每本3段文本：选中描述 + 初读（intro）+ 读完正文 + 精通文本 |
| 技能（Skills） | 73 种 | 名称、描述、性相 |
| 灵魂元素（Elements of the Soul） | 9 + 衍生 | Chor/Shapt/Fet/Ereb/Trist/Mettle/Health/Phost/Wist 及其进化态 |
| 记忆（Memories） | ~37+ | 28种普通记忆 + 9种天气记忆 + 多种Numen |
| 访客（Visitors） | ~24+ | 每位访客的名称、描述、兴趣 |
| 资源物品 | ~200+ | 食物、饮料、工具、材料、家具等的名称和描述 |
| 制作配方 | ~438+（73技能×6配方） | Prentice/Scholar/Keeper 三级配方，含产物描述 |
| 性相（Aspects） | 13种准则 + 子属性 | Edge/Forge/Grail/Heart/Knock/Lantern/Moon/Moth/Nectar/Rose/Scale/Sky/Winter |
| 语言 | 15种 | Aramaic/Cracktrack/Ericapaean/Fucine/Greek/Henavek/Hyksos/Killasimi/Latin/Mandaic/Phrygian/Ramsund/Sabazine/Sanskrit/Vak |
| 结局（Endings） | ~99 | 各类胜利结局描述 |
| 成就（Achievements） | ~99 | 成就名称和描述 |

**优点：**
- 数据最完整，覆盖所有游戏内容
- 格式规范（标准 JSON），易于程序化解析
- 包含官方简体中文本地化（loc_zh-hans 文件夹）
- 无需网络请求，离线可用
- JSON 键名稳定，易于映射到数据库字段

**缺点：**
- 需要拥有游戏才能访问原始文件
- 部分文本分布在 `xexts` 嵌套字段中，需要递归提取
- `elements/` 文件夹文件数量多（Rowenarium 列出了 18+ 个 JSON 文件），需要逐一处理
- DLC（House of Light）有额外的 JSON 文件（DLC_HOL_ 前缀）

**结论：这是获取完整 BoH 文本数据的最佳首选来源。**

---

### 3.2 Rowenarium（在线数据浏览器）

**网址：** `https://uadaf.theevilroot.xyz/rowenarium/`

**说明：** Rowenarium 是 BoH 的"Frangiclave"——一个从游戏 JSON 文件中抓取数据并在线展示的浏览器工具。与 CS 的 Frangiclave Compendium (frangiclave.net) 概念相同，但专注于 BoH。

**数据覆盖范围（实测）：**

| 类别 | JSON文件数 | 实体数（估计） |
|------|-----------|---------------|
| 成就（Achievements） | 10 | ~99 |
| 牌组（Decks） | 7 | ~84 |
| 元素（Elements） | 18+ | ~1,000+（含截断） |
| （更多类别被截断，可能含配方和行动） | - | - |

**优点：**
- 数据直接从游戏 JSON 提取，准确度高
- 可按文件来源浏览，符合游戏内部结构
- 每个实体有独立页面，含完整的 aspects 属性

**缺点：**
- 网站托管在个人域名（theevilroot.xyz），稳定性不确定
- 仅展示属性数据（aspect ID/值），不是完整叙事文本
- 没有中文翻译数据
- 无 API，仅可通过 HTML 解析获取数据
- 似乎不包含 recipes（配方）部分，或该部分在页面截断中

**结论：可作为游戏属性数据的快捷查询工具，但不适合用于提取完整叙事文本。**

---

### 3.3 Fandom 英文维基

**网址：** `https://book-of-hours.fandom.com/wiki/Book_of_Hours_Wiki`

**统计数据：**
- **1,564 条目（articles）**
- **3,873 总页面**
- 活跃编辑中

**覆盖的文本类别：**

| 类别 | 子页面数（估计） | 文本完整度 |
|------|-----------------|-----------|
| 可读书籍（Readables） | ~281+ | 每本有独立页面，含选中描述、阅读文字、精通文字 |
| 技能（Skills） | 73 | 含主要/次要性相、可进化魂质 |
| 灵魂元素 | 9 + 疾病态 + 进化态 | 含描述、获取方式、疾病治疗 |
| 智慧树（Tree of Wisdoms） | 9分支 | 技能-智慧-魂质映射表 |
| 记忆（Memories） | ~37+ | 含性相值、是否持久（Persistent） |
| 制作（Crafting） | 工作台列表 | Prentice/Scholar/Keeper 三级 |
| 访客（Visitors） | ~24+ | 含姓名、可交谈季节、兴趣 |
| 房间（Rooms） | ~100+ | 含解锁条件、工作台、书架 |

**优点：**
- 社区维护活跃，内容不断更新（含 HOUSE OF LIGHT DLC）
- 书籍页面包含完整的三段叙事文本（用引用块标注）
- 有便捷的"全部页面"索引（按字母排序）

**缺点：**
- Fandom 的反爬机制严格（WebFetch 返回 402 Payment Required）
- 文本格式不统一，难以程序化提取
- 部分页面标为 stub（不完整）
- 仅英文，无中文

**结论：适合人工查阅和验证，不适合大规模程序化抓取。**

---

### 3.4 灰机中文维基（司辰之书中文维基）

**网址：** `https://boh.huijiwiki.com/wiki/首页`

**统计数据：**
- **词条数量：2,455 个**
- **编辑次数：103,399 次**
- **编辑者：712 位**
- **上传图片：13,650 张**

**优点：**
- 中文翻译（社区维护）
- 页面数量比英文维基更多（2,455 vs 1,564），中文内容覆盖面更广
- 有专门的"文本雷同"考据页面，与其他作品进行文本对比

**缺点：**
- 建设进度不一，部分页面可能是机器翻译或未完成
- 爬虫访问返回 403（WebFetch 被拒）
- 与 Fandom 维基一样，不适合大规模程序化爬取

**结论：适合人工参考中文翻译，不适合直接抓取。**

---

### 3.5 Secret Histories API Mod

**仓库：** `https://github.com/SunsetFi/secrethistories-api-mod`

**说明：** 一个运行时 REST API 服务器（端口 8081），从游戏内部暴露数据。支持 Cultist Simulator 和 Book of Hours。

**BoH 安装要求：**
- 须在游戏目录中安装 BepInEx
- 须手动编译（`dotnet publish`，设置 `GAME=BH`）

**API 文档：** `https://sunsetfi.github.io/secrethistories-api-mod`

**语言栈：** C# (98.6%)

**优点：**
- 实时读取游戏运行时数据
- TypeScript 类型化的 npm 库可用
- 开源（GitHub 5星，122次提交）

**缺点：**
- 需要游戏运行才能使用
- 暴露的是游戏状态（当前存档），不是全部原始数据
- 不支持预编译发布，须手动构建
- 不活跃（无正式Release、无package发布）

**结论：适合制作实时辅助工具，不适合作为离线数据集的数据源。**

---

### 3.6 Steam 玩家自制工具

**来源：** [Steam 社区讨论：Writing my own personal "Library Assistant" in Python](https://steamcommunity.com/app/1028310/discussions/0/3819669605966711949/)

**原理：** 解析游戏自动存档的 `player.log` 文件，提取当前档案中所有已发现的书籍信息。

**输出：CSV 文件，包含字段：**
- 阅读状态
- 谜题值（mystery values）
- 技能信息
- 谜题类型
- 描述文本
- 正文内容

**优点：**
- Python 实现，易于复用
- 实时更新（监控自动存档变化）

**缺点：**
- 仅提取玩家已发现的书籍，非全量数据
- player.log 格式无官方文档，可能随版本变化

**结论：可作为实时辅助工具参考，不适合获取全量数据集。**

---

### 3.7 Frangiclave Compendium（对比参考）

**仓库：** `https://github.com/frangiclave/frangiclave-compendium`
**网站：** `https://frangiclave.net/`

**说明：** Frangiclave 是 CS 的数据浏览器，Python (69.1%) + C# (6.4%) 组合，CC0 许可证。

**关键发现：**
- **仅支持 Cultist Simulator，不支持 Book of Hours**
- 无公开计划添加 BoH 支持
- 但其**架构可作为 BoH 数据提取的模板参考**：C# 解析 Unity 资源文件 → Python Web 服务展示
- Rowenarium 本质上是 BoH 的"Frangiclave 替代品"

---

### 3.8 NexusMods

**网站：** `https://www.nexusmods.com/bookofhours/`

**搜索结果：**
- 无 BoH 数据导出工具或数据提取 mod
- 仅有少量本地化 mod（如 Extant Languages 多语言支持）和成品文本提示 mod（如 Memory skill and recipe spoilers）
- Weather Factory 的官方 mod 支持仅限于本地化（locmod 创建参考文档）

**结论：NexusMods 不是 BoH 数据提取的有效来源。**

---

## 四、推荐获取方案

### 方案 A：直接解析游戏 JSON 文件（推荐）

**步骤：**

1. **定位文件**：进入 `{游戏目录}/bh_Data/StreamingAssets/bhcontent/core/`。
   在游戏中可通过 选项 → "BROWSE FILES" 快速到达 mod目录，其上级目录即为核心数据。

2. **解析 elements/ 目录**：
   遍历所有 `.json` 文件，提取每个实体的以下字段：
   - `ID`：唯一标识符
   - `Label`：显示名称
   - `Desc`：描述文本
   - `aspects`：性相字典
   - `xexts`：扩展文本（书籍的阅读文本在此）
   - `xtriggers`：触发结果

3. **提取中文文本**：
   中文翻译位于独立文件夹 `loc_zh-hans/`，结构与 `core/` 平行。
   通过实体 ID 匹配来实现中英文对齐。

4. **解析 recipes/ 目录**：
   提取制作配方及其产物描述。

5. **处理 DLC 数据**：
   House of Light DLC 文件以 `DLC_HOL_` 为前缀，需额外处理。

**推荐技术栈：**
- Python（`json`、`pathlib`、`glob`）
- 输出格式：SQLite / JSON Lines / CSV
- 参考代码：Frangiclave 的 Python 后端（CC0 许可，可复用）

**参考项目架构：**
> Frangiclave Compendium 的 Python 代码可用作解析模板。
> 其 C# 部分用于从 Unity Asset Bundles 中提取原始 TextAsset —— 但在 BoH 中，
> JSON 文件已经明文存储在 StreamingAssets 中，无需 C# 这一步。

### 方案 B：从 Rowenarium 抓取（备选，不推荐）

Rowenarium 虽然结构完整，但仅限于静态 HTML，无 API。而且托管不稳定。不建议作为主要来源。

### 方案 C：社区维基爬取（不推荐）

Fandom 和灰机 wiki 都有严格反爬措施（HTTP 402/403），且文本格式不统一，提取工作量大。

---

## 五、预估文本体量

| 文本类别 | 数量 | 文本段数（每条） | 英语字符数（估算） | 备注 |
|----------|------|----------------|-------------------|------|
| 书籍描述（选中时） | ~281 | 1 | 50–200 字符/条 | `Desc` 字段 |
| 书籍阅读文本 | ~281 | 2–3（intro + 正文 + 精通） | 100–800 字符/条 | `xexts` 字段 |
| 技能名称 + 描述 | 73 | 2 | 20–200 字符/条 | `Label` + `Desc` |
| 魂质名称 + 描述 | 9 + 衍生 | 2 | 20–150 字符/条 | Chor 等 9 种及疾病态 |
| 记忆名称 + 描述 | ~37+ | 2 | 20–150 字符/条 | 含天气记忆和Numen |
| 访客名称 + 描述 | ~24+ | 2 | 20–100 字符/条 | 姓名 + 介绍 |
| 物品名称 + 描述 | ~200+ | 2 | 20–150 字符/条 | 食物、家具、工具等 |
| 制作配方名称 + 产物 | ~438+ | 2 | 20–100 字符/条 | 三级 × 73技能 × 2每级 |
| 结局文本 | ~99 | 1 | 50–300 字符/条 | 含各历史路径 |
| 成就名称 + 描述 | ~99 | 2 | 20–200 字符/条 | Steam成就 |

**总文本量粗估：**
- 英语总字符数：**200,000 – 500,000 字符**
- 英语总词数（Token）：**50,000 – 120,000 词**（以英文单词计）
- 中文总字符数：**150,000 – 400,000 汉字**（官方简体中文本地化）
- 文本条目总数：**超过 2,000 个独立文本段**

**最重要的文本来源是书籍**，~281本书 × 每本3段文本 = ~843段叙事文本，这些是 BoH 的文字精华所在。

---

## 六、补充发现

### 6.1 Weather Factory 的开放态度

- Weather Factory 发布**第六历史社区许可**（Sixth History Community Licence），允许社区创作派生作品
- 官方提供了 **locmod 创建参考文档**（`weatherfactory.biz/book-of-hours-locmod-creation-reference/`）
- 职业本地化合作方会收到一份解释 JSON 字段含义的 Google Doc
- 游戏数据文件采用**明文 JSON** 格式，放在 `StreamingAssets` 下，表明开发者不反对数据查看

### 6.2 数据完整性说明

- BoH 的基础游戏 + House of Light DLC = 完整数据集
- 游戏还在更新中（2024年仍有补丁），数据可能持续微调
- `core/` 文件夹内的 README 文件建议玩家在通关前不要查看原始 JSON（spoiler 警告）

### 6.3 同类项目启示

- **Cultist Simulator 数据集**：Frangiclave 的成功证明了从 JSON 提取 → Web 展示的可行性
- **Rowenarium** 已经做了 BoH 的 JSON 提取和展示，证明了相同方法对 BoH 有效
- **Secret Histories API Mod** 证明了通过 Hook 游戏引擎（BepInEx）可以获取运行时数据

---

## 七、关键链接汇总

| 资源 | URL |
|------|-----|
| Weather Factory 官方 | https://weatherfactory.biz |
| BoH 官方 mod 文档 | https://weatherfactory.biz/book-of-hours-locmod-creation-reference/ |
| BoH Locmod 创建参考 | https://weatherfactory.biz/book-of-hours-locmod-creation-reference/ |
| Rowenarium（BoH 数据浏览器） | https://uadaf.theevilroot.xyz/rowenarium/ |
| Frangiclave Compendium（CS 数据） | https://frangiclave.net/ |
| Frangiclave Compendium 仓库 | https://github.com/frangiclave/frangiclave-compendium |
| Secret Histories API Mod | https://github.com/SunsetFi/secrethistories-api-mod |
| Fandom 英文维基 | https://book-of-hours.fandom.com/wiki/Book_of_Hours_Wiki |
| 灰机中文维基 | https://boh.huijiwiki.com/wiki/首页 |
| Steam 社区（Library Assistant工具） | https://steamcommunity.com/app/1028310/discussions/0/3819669605966711949/ |
| Steam 社区（游戏文件读取讨论） | https://steamcommunity.com/app/1028310/discussions/0/3812913565881387532/ |
| Eldra Echo 资源合集 | http://www.eldraecho.com/blogofhours/cultist-simulator-and-book-of-hours-resources |
| Weather Factory modding 总览 | https://weatherfactory.biz/category/modding/ |
| 第六历史社区许可 | https://weatherfactory.biz/sixth-history-community-licence/ |

---

**结论：直接解析游戏本体 JSON 文件是获取 Book of Hours 完整文本数据的最可行方案。** 游戏使用与 Cultist Simulator 相同的引擎和 JSON 架构，数据文件以明文形式存储在 `StreamingAssets` 中，结构清晰，包含官方中英文双语，且 Rowenarium 项目已证明这一方法的可行性。
