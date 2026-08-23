# 三轴视觉系统合同

`507-ppt` 的底层模型是：

```text
语义组件 × 设计语言 × 视觉呈现 → 页面成品
```

内容 v3 只保存组件与事实；visual-plan v1 保存设计语言、逐页呈现、受控 treatment 和文字流；manifest v2 保存交付证据。视觉层不得改写组件语义。

## 语义组件

| 组件 | 家族 | 核心输入 |
| --- | --- | --- |
| `cover / section / closing` | identity | 标题及可选副标题、正文或 CTA |
| `statement` | assertion | 判断标题及可选解释 |
| `collection` | set | 2～6 项并列内容 |
| `comparison` | relation | 恰好 2 项对照 |
| `sequence` | relation | 2～6 项顺序内容 |
| `relationship` | relation | 2～8 节点与 1～12 条边 |
| `media-evidence` | evidence | 1～3 个带唯一 ID、真实本地 path、alt 的素材 |
| `quote` | evidence | 引语与出处；不承担 closing |
| `metric / chart / table` | data-evidence | 单指标、结构化数列、精确表格 |

`metric / chart / table` 是同一数据证据家族的三个语义叶子，不能由渲染器自行互换。`table` 自带强规则线，任何组合都抑制 `background-grid` 与重复装饰线。

旧内容一轮兼容映射：`image-text → media-evidence`、`three-part → collection`、`process → sequence`、`metric → data-evidence.metric`。新内容只写 v3 组件。

## 设计语言

设计语言是 deck 级稳定规则，不是页面模板。首批基础语言：

- `precision-modern`：严格网格、锐利轮廓、无衬线与等宽角色、稀缺强调、平面层次；
- `editorial-archive`：编辑栏栅格、衬线/无衬线/等宽分工、暖纸、hairline 与纸面层次；
- `soft-product`：模块网格、人文无衬线、圆润轮廓、柔和色场与轻抬升；
- `warm-narrative`：非对称节奏、衬线标题、暖色与纸面质感；
- `research-organic`：模块结构、研究型层级、克制绿色与扁平表面；
- `bold-statement`：海报网格、黑白高对比、粗规则线与单一红色标点。

一套 deck 只能使用一个基础语言。每页仅可使用 `default / inverse / section-emphasis / dense` treatment；不得直接覆写字体、颜色、圆角或间距。旧 `swiss / magazine / cobalt / clay / forest / noir` 降为 preset，分别映射到上述语言，不再是底层唯一入口。

## 视觉呈现与兼容矩阵

`P` 推荐，`S` 支持，`C` 条件支持，空白表示禁止。

| 组件 | Type | Panel | Data | Schematic | Photo | UI | Editorial | Hand-drawn |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| cover | P | S |  |  |  |  | S |  |
| section | P | S |  |  |  |  | P |  |
| closing / statement | P | S |  |  |  |  | S |  |
| collection |  | P |  | S |  |  | S | S |
| comparison |  | P |  | P |  |  | S | S |
| sequence |  | S |  | P |  |  | S | P |
| relationship |  | S |  | P |  |  |  | P |
| media-evidence |  |  |  |  | P | P |  |  |
| quote | P |  |  |  |  |  | P |  |
| metric |  | S | P |  |  |  |  |  |
| chart |  | S | P |  |  |  | S |  |
| table |  | S | P |  |  |  | S |  |

首批只开放渲染器确实消费的组合；例如 photo/UI 目前只服务 `media-evidence`，不能把带素材的 cover 误报为 photo-led。`photo-led` 需要真实素材，`ui-product-led` 需要 `role=ui` 的素材，`data-led` 需要结构化数字。兼容矩阵由 `scripts/design_system.py` 解析，不能手写通过状态。

## 载体支持

| 呈现 | HTML | PPTX |
| --- | --- | --- |
| type / panel / data / schematic | native | native |
| photo / UI-product | native | native picture 对象 |
| editorial-print | native | adapted：省略不可编辑纹理 |
| hand-drawn | native | adapted：以原生线条/shape 近似 |

`native` 与 `adapted` 都必须保持语义、层级、可编辑对象和语言辨识；adapted 必须进入 manifest degradation。未通过真实双载体的 `glass / CRT / pixel / brush` 等扩展不进入生产注册表。

## 组合 preset 与原型

Preset 是已验证的组合便捷入口，不改变底层三轴。Agent 可按内容生成任意兼容组合；“自由”表示允许动态创作，不表示所有笛卡尔积天然有效。

用户未锁定成熟 preset 时，以同一真实内容生成 2～3 个候选 visual-plan；代表页覆盖封面、文字最密页、首个数据或素材页。混合候选后必须生成新的合并 visual-plan 和合并原型，再进入整套制作。

## 不变量

- 页面 ID、顺序、可见内容、notes 与 alt 不随 visual-plan 改变；
- 同一 visual-plan 同时供 HTML 与 PPTX 消费；
- 组合 support、suppression 和 degradation 由注册表计算；
- 组件自身的强组织手段优先于装饰，例如 table 抑制背景网格；
- 中文换行遵循 [排版合同](typography.md)，不能用拆词或无限缩字掩盖布局问题；
- 13 页 showcase 覆盖全部语义叶组件，8 页 pairwise fixture 覆盖全部呈现与四种 treatment；六个基础语言及全部注册组合由 resolver 全矩阵检查，不生成无意义的全笛卡尔积成品。
