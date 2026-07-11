# 视频拉片脚本

所有视频流水线脚本使用小写 `snake_case` 与 `video_` 前缀。

| 脚本 | 职责 |
|---|---|
| `video_pull.py` | 公共编排入口：取得视频、ASR、scene-cut、M3、定位、抽帧、图片理解、分析简报 |
| `video_understand_minimax.py` | MiniMax-M3 Files API + `/anthropic/v1/messages` 整段视频理解 |
| `video_locate_segments.py` | 10 秒 1 帧定位索引和本地证据候选窗口 |
| `video_extract_adaptive_frames.py` | 对候选窗口有界加密抽帧 |
| `video_describe_key_frames.py` | 关键帧图片理解 |
| `video_prepare_analysis.py` | 写 video_* 最终模板与分析简报 |
| `video_validate_breakdown.py` | 校验最终包并写入 `video_completed` |
| `video_asr_faster_whisper.py` / `video_ocr_tesseract.py` | 本地证据叶子工具 |

`MiniMax_API_KEY` 必须由进程环境导出。脚本不读取、source 或打印 `~/.zshrc`。M3 失败默认使拉片失败；`--force-local-fallback` 只跳过 M3 **整段视频理解**，图片理解仍需 `MiniMax_API_KEY`。
