---
name: 507-remix
description: "视频借鉴重组 skill。只消费一个或多个 video_completed 的 507-breakdown 拉片包，提取可借鉴的结构、叙事、镜头、字幕与节奏模式，明确不借内容和身份，再重组为原创视频创作包与工具无关的 prompt-pack.json；不读取原视频、不做取证、不直接渲染成片。Use when user mentions 视频借鉴重组, 原创创作包, 视频二创, remix, video remake, recombine, 借这个视频的手法."
---

# 视频借鉴重组（remix）

把一个或多个已完成拉片包中的**创作手法**重新组合成原创视频创作包。

它借结构、节奏与视听语言，不复制来源视频的主题表达、逐句文案、人物身份、品牌资产或独特画面。

## 输入合同

每个来源必须是 `507-breakdown` 的完成包：

```text
raw/video_manifest.json   # status=video_completed
video_meta.md
video_breakdown.md
video_breakdown.json
```

同时需要目标主题、平台、时长、风格和项目名。能从已确认创意或用户请求确定时直接使用；这些内容仍涉及用户意图且未确定时，先进入 `507-grill`，不要让用户选择 skill 名称。

旧文件名和未完成拉片包没有 fallback（回退）或迁移路径。

## 不覆盖什么

- 原视频下载、字幕、OCR（文字识别）、时间定位或画面取证 → `507-breakdown`；
- 从视频内容提炼观点、经验或写作碎片 → `507-mine`；
- 选定主题背后的候选中心判断 → `507-fuse` / `507-grill`；
- 生图、生视频、剪辑、配音、字幕烧录或最终发布。

## 输出合同

在 `03-作品/{选题}/视频/{project-name}/` 生成：

```text
README.md
brief.md
borrow-map.md
structure.md
storyboard.md
style-lock.md
prompt-pack.json
```

- `borrow-map.md`：逐项说明借什么、为什么、如何改造、明确不借什么及来源冲突；
- `structure.md` / `storyboard.md`：原创主题下的结构节拍和画面目标；
- `style-lock.md`：后续执行应保持的视听模式；
- `prompt-pack.json`：符合 `assets/prompt-pack.schema.json` 的工具无关创作蓝图，不包含来源包与模型绑定信息。

## 工作流程

1. 校验每个输入包的四个文件及 `video_completed` 状态。
2. 读取拉片包中的结构、patterns（模式）、techniques（手法）、视觉语言和“可借 / 不建议借”说明。
3. 先锁定目标主题、平台、时长与风格；需要用户决定的部分进入 `507-grill` 后返回。
4. 选择跨来源可迁移手法，主动排除逐句文案、独特人物/品牌、来源主题结论与互相冲突的模式。
5. 运行脚本生成创作包；多个来源重复传入 `--pull-dir`：

```bash
python3 scripts/video_remake.py run \
  --pull-dir 05-视频拉片/<video-a> \
  --pull-dir 05-视频拉片/<video-b> \
  --project-name <name> \
  --theme <theme> \
  --platform <platform> \
  --duration <duration> \
  --style <style> \
  --output-dir 03-作品/<选题>/视频
```

6. 从人读版和机器版两侧验收；不直接把生成包交给视频执行器。

## 验收

- 所有输入 manifest 均为 `video_completed`，没有绕过新契约；
- 七个输出文件齐全，`prompt-pack.json` 可解析并符合 schema 的必填字段；
- `borrow-map.md` 同时列出借用、锁定、明确不借和冲突处理，不是来源功能摘要；
- storyboard 每个节拍服务当前原创主题，来源片段只作手法参考；
- prompt pack 不含原视频逐句内容、人物/品牌仿冒要求、来源路径或模型专属字段；
- 目标、结构、storyboard、style lock 与 prompt pack 前后一致。

## 完成与接力

- **完成信号**：原创创作包通过输入契约、完整性、一致性与原创边界验收。
- **产物**：人读版创作包和工具无关 `prompt-pack.json`；不包含最终视频。
- **候选出口**：需要补拉片证据时返回 `507-breakdown`；主题或内容材料不足时进入 `507-mine` / `507-fuse` / `507-grill` 后返回；创作包成熟后进入相应视频制作、剪辑或生成工作流；只需蓝图时直接结束。
- **回退条件**：来源包不完整、目标未确认或只能通过复制来源内容才能成立时停止，不生成伪原创包。

## 红线

- 不读取原视频绕过 breakdown；
- 不复制逐句文案、独特镜头内容、人物身份或品牌资产；
- 不把多个来源机械拼接成 storyboard；
- 不把创作包声称为已渲染成片。
