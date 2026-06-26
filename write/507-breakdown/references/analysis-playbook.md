# 507 Video Pull 分析落盘手册

当 `scripts/video_pull.py run` 完成后，Agent 按以下顺序把证据包写成真正的拉片包。脚本输出的 `breakdown.md/json` 只是模板，不是最终分析。

## 1. 先核验证据是否足够

必须先读：
- `raw/manifest.json`：确认 `status`、`textEvidenceSource`、每一步成功/失败原因。
- `transcript.md`：确认最终文字来源进入人读文档。
- `raw/windows.jsonl`：确认分析层小窗是否存在。
- `raw/contact_sheets/`：先看整体节奏与画面变化。
- `raw/frames_uniform/` / `raw/frames_scenecut/`：遇到小字、UI、字幕样式、镜头细节时回看原始帧。

如果文字证据缺失，必须失败并说明平台字幕、ASR、OCR 分别拿到了什么/没拿到什么，不写台词推断。
如果视觉证据缺失，只能写文字结构分析，不得输出具体视觉标签。

## 2. 判定视频类型

`video_type`（视频类型）由 Agent 基于文字和画面共同判断，脚本不得默认填写。

`breakdown.json` 的 `videoType` 只能是以下 schema 枚举之一：

| 枚举值 | 中文 | 含义 |
|---|---|---|
| `talking-head` | 口播类 | 单人/少数人稳定口播为主，讲故事或评论。 |
| `tutorial` | 教程类 | 口播 + 操作/文件/UI/步骤讲解为主。 |
| `narrative` | 叙事类 | 连续观点推进，无主讲人镜头，靠 B-roll + 字幕驱动。 |
| `promo` | 宣传类 | 产品/品牌/项目宣传片。 |
| `mixed` | 混合/兜底 | 证据不足或类型不稳定时的保守兑底。 |

可以人工覆盖，但必须在 `meta.md` 说明覆盖原因。

## 3. 先读文字，再看画面

顺序固定：
1. 读 `transcript.md`，划出信息功能变化点。
2. 看 `raw/contact_sheets/`，确认镜头/字幕/UI/节奏变化。
3. 回看少量关键原始帧确认细节。
4. 再写最终 `breakdown.md/json`。

禁止只凭 transcript 输出 `fixed-medium-close`、`ui-overlay-card`、`subtitle-green-keyword` 等视觉标签。
禁止只看联系图就脑补台词。

## 4. 写 `meta.md`

至少写清：
- `title`
- `video_type`
- `status`
- `text_evidence_source`
- 当前 workspace
- 主要证据文件
- 明显限制（如 ASR 错字多、OCR 只覆盖画面文字、scene-cut 帧过少）

## 5. 写 `breakdown.md`

固定用“前半总结 + 后半时间轴表格”混合形态：
- 一句话主旨
- 视频类型
- 叙事与结构
- 视听语言
- 可借鉴点
- 不建议借鉴点（如有）
- 时间轴拆解表

人读版可以写未进入封闭词表的新观察，但必须说明证据来自文字、联系图还是原始帧。

### 时间轴表格的标签写法

**约定**：标签列同时给英文+中文含义，使用 `` `英文标签`（中文说法） `` 格式。

- 英文标签：必须取自 `references/tag-vocabulary.md` 封闭词表，且与 `breakdown.json` 完全一致（不发明、不改名）。
- 中文说法：取自词表对应标签的「中文说法」一行，用于人读解释。
- 表格里使用顿号或空格分隔多个标签，不限定一种分隔符。

示例：

```markdown
| 时间 | 手法标签 |
|---|---|
| 00:00-00:23 | `hook-result-first`（结果先行开场）、`subtitle-bottom-bar`（底部字幕条）、`hard-cut`（硬切） |
| 00:23-01:30 | `hook-problem-first`（痛点先行开场）、`overlay-on-mention`（讲到概念叠画面） |
```

这样：
- 人读：看到标签立刻知道是什么手法。
- 机读：`breakdown.md` 里的英文标签与 `breakdown.json` 一一对应，人工修订时间轴时不会破坏机器消费。
- 校验：`validate_breakdown.py` 只读 `breakdown.json`，不受 `breakdown.md` 中的中文注释干扰。

## 6. 写 `breakdown.json`

`breakdown.json` 给机器消费，必须保守、稳定、可重组：
- `videoType` 必填，且只能用 schema 枚举。
- `oneLineThesis` 必填。
- `structure` 用高层结构段。
- `visualLanguage` 只写已被画面证据确认的标签。
- `segments` 使用语义合并后的最终段。
- `patterns` 与 `techniques` 只能使用 `references/tag-vocabulary.md` 已定义词表。

未覆盖词表的新现象只写入 `breakdown.md`，不要发明新标签写进 JSON。

## 7. 两层分段怎么落

分析层：
- 小窗来自 `raw/windows.jsonl`。
- 小窗只用于降低 Agent 输入负载和定位证据。

输出层：
- 最终段按语义合并。
- 不按固定 10 秒硬切。
- 不给最终段设硬上限。
- 一个最终段必须表达一个完整信息功能，对应 `structure`（叙事结构）数组中的某个 `label`：

| label | 中文 | 含义 |
|---|---|---|
| `hook` | 钩子/开场 | 开头抓住注意力的一级节拍。 |
| `pain-points` | 痛点 | 描述问题/压力，让观众代入。 |
| `reframing` | 重述问题 | 从误解切到真正的矛盾或方法入口。 |
| `walkthrough` | 走查 | 按步骤/模块走查关键做法。 |
| `methodology` | 方法论 | 从技巧上升到可复用方法。 |
| `cta` | 行动号召 | 结尾要求观众下一步操作。 |

## 8. 最低完成条件

一个合格拉片包至少满足：
- `meta.md` 说明视频类型、证据来源、限制。
- `transcript.md` 承接最终文字证据。
- `breakdown.md` 有前半总结和后半时间轴。
- `breakdown.json` 符合 schema，且标签来自封闭词表。
- 视觉判断能追溯到 `raw/contact_sheets/` 或关键原始帧。
