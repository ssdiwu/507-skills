# 507 Breakdown

`507-breakdown` 将单个视频编译为可复核的拉片包：MiniMax-M3 给整段语义参考，本地 ASR、OCR、PTS 帧和 scene-cut 确认真实时间，再对关键窗口做自适应抽帧和图片理解。

## 完成契约

只有 `video_validate_breakdown.py --workspace <workspace>` 通过后，工作区才是 `video_completed`，可由 `507-remix` 消费。

```text
05-视频拉片/<video-id>/
├── video_meta.md
├── video_transcript.md
├── video_breakdown.md
├── video_breakdown.json
├── raw/video_manifest.json
└── analysis/
```

旧 `meta.md` / `breakdown.json` 包不兼容。

## 使用

```bash
python3 scripts/video_pull.py run --video <url-or-path> --output-dir 05-视频拉片
# agent 根据 analysis/video_analysis_brief.md 和本地证据填写最终 video_breakdown.*
python3 scripts/video_validate_breakdown.py --workspace 05-视频拉片/<video-id>
```

MiniMax-M3 为默认必经步骤，使用 `MiniMax_API_KEY` 环境变量。显式 `--force-local-fallback` 只跳过 M3 **整段视频理解**，但图片理解仍需 `MiniMax_API_KEY`；未导出密钥时无法完成拉片。
