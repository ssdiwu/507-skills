# 507-remix 约束

只消费 `video_completed` 的 507-breakdown 新拉片包：`raw/video_manifest.json`、`video_meta.md`、`video_breakdown.md`、`video_breakdown.json`。不兼容旧文件名，不读取原视频，不重跑取证。

验证：`python3 -m py_compile scripts/video_remake.py`，并用 completed fixture 运行 `video_remake.py run`。
