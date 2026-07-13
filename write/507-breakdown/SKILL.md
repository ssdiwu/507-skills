---
name: 507-breakdown
description: "视频拉片 skill：将一个视频经 MiniMax-M3 整段理解、本地文本定位、受限视觉搜索、自适应抽帧与图片证据回写核验，产出可供 remix 消费的 video_* 拉片包。Use when user mentions 拉片, 拆视频, 视频借鉴, 视频取证, 怎么剪, 视频结构分析, breakdown, video breakdown, transcript extraction. 普通本地视频总结走 pi-sense，不走本 skill。"
---

# 视频拉片（breakdown）

把一个视频编译成可核验、可复用的拉片包。它不是快速总结：MiniMax-M3 先理解整段视频，本地证据再确认关键时间与画面。

## 输入与产物

一次处理一个 URL 或本地视频，输出到 `05-视频拉片/<video-id>/`：

```text
video_meta.md
video_transcript.md
video_breakdown.md
video_breakdown.json
raw/video_manifest.json
analysis/video_understanding_minimax.json
analysis/video_locations.json
analysis/video_frame_observations.json
analysis/video_analysis_brief.md
```

只接受新 `video_*` 契约；不兼容旧包。

## 流程

1. 取得视频与本地 ASR、scene-cut、OCR 证据。
2. 默认调用 MiniMax-M3 整段理解；从环境变量 `MiniMax_API_KEY` 读取密钥，不读取 `.zshrc`。
3. 用 ASR/OCR 命中定位语义锚点；每 10 秒 locator、PTS 帧和 scene-cut 仅提供受限视觉搜索点，须由图片锚点命中回写定位。
4. 对候选窗口有界加密抽帧（默认 2fps），并对关键帧做图片理解；接受带 Markdown（标记语言）围栏的 JSON（数据格式）响应，严格校验回显锚点、肯定可见性与非空证据，但不要求证据逐字复述锚点。
5. 汇总分析简报；agent 基于本地证据填写最终 `video_breakdown.*`。
6. `video_validate_breakdown.py --workspace ...` 通过后才标记 `video_completed`。

## 时间红线

M3 的时间、顺序与方向只作未验证参考。最终时间窗只能来自本地 ASR、OCR、带 PTS 的帧与 scene-cut；没有证据不得猜时间。

## 失败与强制兜底

M3 是默认必经阶段；失败时命令非零退出并保留工作区。只有显式 `--force-local-fallback` 才可跳过 M3 **整段视频理解**，改走本地 locator + 自适应抽帧降级；但图片理解仍需 `MiniMax_API_KEY`，未导出密钥时无法完成。完成包必须记录 `forced_local_fallback` 与限制。

## 脚本

```bash
python3 scripts/video_pull.py run --video <url-or-path> --output-dir 05-视频拉片
python3 scripts/video_validate_breakdown.py --workspace 05-视频拉片/<video-id>
```

脚本均使用小写 snake_case，视频流水线文件以 `video_` 开头。详情见 `scripts/README.md` 与 `references/analysis-playbook.md`。
