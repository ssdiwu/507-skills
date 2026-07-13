# Video Pull 标签词表

`video_breakdown.json` 里的标签使用**封闭词表**。

规则：
- `JSON` 只能使用这里定义过的标签（机器消费）。
- 新观察先写进 `video_breakdown.md`，不要直接发明新标签写进 `JSON`。
- 当某类观察稳定重复出现，再把它提升成正式标签。

## 分组与字段对应

词表分组与 `assets/breakdown.schema.json` 的字段严格对齐，`video_validate_breakdown.py` 会强制归属：

| 词表分组 | 写入位置 |
|---|---|
| `structure/`（叙事与结构） | `segments[].patterns` |
| `camera/`（镜头） | `segments[].techniques`、`visualLanguage.camera` |
| `editing/`（剪辑） | `segments[].techniques`、`visualLanguage.editing` |
| `subtitle/`（字幕） | `segments[].techniques`、`visualLanguage.subtitle` |
| `ui/`（界面） | `segments[].techniques`、`visualLanguage.ui` |

约定：
- `segments[].patterns` 只能放 `structure/` 分组的标签。
- `segments[].techniques` 只能放 `camera/ editing/ subtitle/ ui/` 分组的标签。
- `visualLanguage.{camera,editing,subtitle,ui}` 各子对象只能放同名分组的标签。

---

## structure/（叙事与结构）

- `hook-result-first`：结果先行开场
  - 中文说法：开场先抛结论/数据，再补过程。
  - 实际场景：科普视频第一句「AI 格局要变天」，先用结果吸引再看分析。
- `hook-problem-first`：痛点先行开场
  - 中文说法：开场先抛问题/痛点。
  - 实际场景：教程视频「如果你不用规则文件，越用越乱」先建立问题压力。
- `problem-solution-demo`：问题—方案—演示推进
  - 中文说法：按问题 → 方案 → 演示的结构推进。
  - 实际场景：发现上下文膨胀（问题）→ 立规则文件（方案）→ 演示三文件用法。
- `listicle-step-flow`：列表/步骤推进
  - 中文说法：按编号列表或步骤顺序推进。
  - 实际场景：「第一个是 PRODUCT.md，第二个是 DESIGN.md，第三个是 AGENTS.md」逐条讲。
- `cta-comment-close`：评论号召收束
  - 中文说法：结尾以评论 / 互动号召收束。
  - 实际场景：「如果你还有问题，欢迎评论区」「如果喜欢，点赞关注」。

## camera/（镜头）

- `fixed-medium-close`：固定机位中近景
  - 中文说法：相机不动、人物中近景取景。
  - 实际场景：博主在家对着摄像头口播。
- `single-background`：单一不变背景
  - 中文说法：背景全程基本不变。
  - 实际场景：口播博主背景始终是同一面墙或书架。
- `single-speaker-center`：单人主体居中
  - 中文说法：单人讲述为主，主体稳定居中或近中。
  - 实际场景：单一主播画面，人物位置基本不动。

## editing/（剪辑）

- `hard-cut`：硬切
  - 中文说法：场景之间不淡入淡出，直接跳切。
  - 实际场景：科普视频里从 A 城市 B-roll 直接切到 B 城市 B-roll。
- `beat-paced-reveal`：信息节拍逐步揭示
  - 中文说法：一句一个节拍，按信息点停顿和揭示。
  - 实际场景：「AI 格局要变天」→「具体怎么变呢」→ 给数据，分段揭示。
- `overlay-on-mention`：讲到概念叠画面
  - 中文说法：讲到具体概念时弹出对应画面。
  - 实际场景：讲"斯坦福校园"时切到斯坦福校园 B-roll；讲"数据中心 5427 个"时叠数字面板。
- `return-to-speaker`：回到主讲人镜头
  - 中文说法：讲抽象思路时回到主讲人纯画面。
  - 实际场景：从具体案例切到方法论总结时，画面回到主讲人特写。

## subtitle/（字幕）

- `subtitle-bottom-bar`：底部字幕条
  - 中文说法：画面底部那条字幕横条。
  - 实际场景：科普/口播视频底部贯穿全片的白色字幕。
- `subtitle-green-keyword`：字幕关键词绿色高亮
  - 中文说法：字幕里的关键词使用绿色高亮。
  - 实际场景：教程视频把"PRODUCT.md""三文件"用绿色着重。
- `keyword-memory-anchor`：关键词记忆锚点
  - 中文说法：用特定样式关键词做记忆锚点。
  - 实际场景：「要想富先修路」「修塔不如修路」用大字幕 + 留白做成可记忆金句。

## ui/（界面）

- `ui-overlay-card`：画面叠加 UI 卡片
  - 中文说法：画面上叠加 UI 卡片或截图。
  - 实际场景：教程视频讲"项目规则"时右边弹出 AGENTS.md 卡片。
- `topic-label-top-left`：左上角主题标签
  - 中文说法：左上角有主题标签或系列标签。
  - 实际场景：B 站视频左上角的「麻薯波比呀 bilibili」频道水印。