# 视频拉片分析手册

## 证据优先级

MiniMax-M3 提供语义锚点和不完整参考；真实时间只能来自本地 ASR、OCR、带 PTS 的帧与 scene-cut。不得把 M3 时间、顺序或方向直接写入最终 `video_breakdown.json`。

## Agent 最终填写顺序

1. 阅读 `analysis/video_understanding_minimax.json`（若非 forced fallback）。
2. 阅读 `analysis/video_locations.json` 和 `analysis/video_frame_observations.json`。
3. 回看 `raw/video_frames_adaptive/`、ASR/OCR 与 scene-cut 证据。
4. 写 `video_meta.md`、`video_transcript.md`、`video_breakdown.md`、`video_breakdown.json`。
5. 执行 `video_validate_breakdown.py --workspace ...`。

最终 segment 必须有正向起止时间、台词、视觉变化和封闭词表标签。没有本地证据的观察只能留在分析简报中。
