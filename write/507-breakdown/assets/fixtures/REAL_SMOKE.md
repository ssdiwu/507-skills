# MiniMax-M3 真实 smoke test 证据

- 日期：2026-07-10
- 请求路径：MiniMax Files API `https://api.minimaxi.com/v1/files/upload` → `https://api.minimaxi.com/anthropic/v1/messages`
- 认证：仅运行时环境变量 `MiniMax_API_KEY`；本目录不包含密钥或请求 header。

## 可复现小视频

`m3_smoke_synthetic_20260710/` 包含由 `scripts/test_minimax_adapter.py --evidence-dir ...` 真实调用生成的：

- `video_synthetic_8s.mp4`：ffmpeg 生成的 8 秒输入视频
- `workspace/raw/video_manifest.json`：包含输入 SHA-256 和 `video_understood`
- `workspace/analysis/video_understanding_minimax.json`：真实模型输出
- `run.log`：适配器结构验证通过的输出
- `no_key.log`：无密钥失败契约通过的输出

重新生成：

```bash
export MiniMax_API_KEY=...
python3 scripts/test_minimax_adapter.py \
  --evidence-dir assets/fixtures/m3_smoke_synthetic_20260710
```

## 真实内容视频

`m3_understanding_9router.json` 是对本机 9router 竖屏视频的真实 M3 输出。原始视频不纳入仓库；fixture 的 `provenance.videoHash` 是输入 SHA-256，可供持有同一文件的人核对。
