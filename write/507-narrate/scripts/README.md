# 507-narrate 脚本

`voicebox_narrate.py` 是 Voicebox REST API 的确定性本地客户端。它不调用 MCP，不直接启动应用包内的 `voicebox-server`，也不创建或删除声音档案。

## 命令

先满足 [目录说明](../README.md) 中的运行条件。生成前必须已有当前用途的声音授权和人已试听确认的声音档案；读取能力与健康状态不代表获得声音授权。以下命令从 `507-narrate/` 目录运行：

```bash
python3 scripts/voicebox_narrate.py health
python3 scripts/voicebox_narrate.py profiles
python3 scripts/voicebox_narrate.py capabilities
```

生成单段配音：

```bash
python3 scripts/voicebox_narrate.py generate \
  --text "这是一段测试旁白。" \
  --output output/test.wav \
  --profile "已确认的声音档案" \
  --language zh \
  --preset daily \
  --authorized-voice
```

批量生成：

```bash
python3 scripts/voicebox_narrate.py batch \
  --input narration.json \
  --output-dir output/narration-v1 \
  --authorized-voice
```

批量 JSON 可以在顶层提供 `profile`、`preset`、`language`、`engine`、`model_size`、`speed`、`seed`、`instruct`、`normalize`、`max_chunk_chars` 与 `crossfade_ms`；命令行显式值优先。每个 section 必须包含唯一、可用于文件名的 `id` 和非空 `text`，可单独覆盖 `instruct`。

## 行为与失败码

- 默认只连接本机回环地址；可信远程服务必须显式传入 `--allow-remote`。
- 服务离线时，macOS 默认执行系统级应用打开动作并等待健康；`--no-auto-start` 可禁止。
- `generate` 和 `batch` 必须提供 `--authorized-voice`。
- 输出已存在时退出码为 1；只有 `--force` 才允许替换。
- 客户端通过 SSE 等待生成任务进入 terminal status（终态）。只有成功终态才下载音频；失败、取消、超时、下载错误或 WAV 无有效帧均退出 1。
- Voicebox 原始 WAV 会在本地临时目录中通过 FFmpeg `atempo` 做保留音高变速；只有最终 WAV 被写入交付路径。
- 批量任务逐段写入 partial manifest；全部成功后才把状态改为 `completed`。

## 默认预设与参数优先级

默认 `daily` 使用 Qwen 0.6B；`precision` 使用 Qwen 1.7B。两者的最终速度都默认是 `1.2×`，并通过 FFmpeg 保留音高。可用 `--preset precision` 切换清晰咬字模式，也可用 `--speed`、`--engine` 或 `--model-size` 显式覆盖；优先级是命令行、批量 JSON、preset。

先运行 `capabilities` 获取当前服务器实际枚举。枚举值之间没有隐含笛卡尔积，组合不兼容时以服务器错误为准，不自动换模型掩盖失败。当前脚本接受 `0.5–2.0×` 速度；变速后的最终 WAV 时长与哈希才写入视频时间基准。

## 测试

单元测试不连接 Voicebox：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v scripts/test_voicebox_narrate.py
```

本机集成 smoke test（冒烟测试）会真实生成声音，只能使用本人或明确授权的档案：

```bash
python3 scripts/voicebox_narrate.py generate \
  --text "这是一段本地配音测试。" \
  --output /tmp/voicebox-smoke.wav \
  --preset daily \
  --authorized-voice
```

需要同时验证分段输出与累计 timing manifest 时，可把 `smoke-sections.json` 作为 `batch --input`；测试产物应写入临时目录，不提交生成音频、声音档案信息或 manifest。
