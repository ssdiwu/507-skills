# 507-breakdown 约束

## 定位

MiniMax-M3 必经理解与本地证据核验的视频拉片 skill。最终时间只能由本地 ASR、OCR、PTS 帧与 scene-cut 证明。

## 关键边界

- MiniMax 请求适配独立维护，所需运行时依赖必须在本目录显式声明。
- 只从环境变量 `MiniMax_API_KEY` 读取密钥；不读取或输出 `.zshrc`。
- 默认 M3 失败非零；仅 `--force-local-fallback` 可跳过整段理解。
- 只写/读 video_* 新工作区契约；不兼容旧包。
- `video_validate_breakdown.py` 是写入 `video_completed` 的唯一入口。

## 验证

先跑 `python3 -m py_compile scripts/*.py`，再跑 fixture、无 key、真实 M3 与 E2E 测试（见 `scripts/README.md`）。
