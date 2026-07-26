# 507-narrate：本地配音生成

`507-narrate` 位于 `write/` 的声音制作接缝：上游消费 `507-stage` 的成熟视频旁白内容包，下游向 `507-video` 交付具有真实时长的配音包。它不写稿、不创建声音身份、不制作视频，也不发布。

## 目录

- `SKILL.md`：触发条件、输入门、授权边界、制作流程与出口合同。
- `scripts/voicebox_narrate.py`：使用 Python 标准库调用 Voicebox 本地 REST API。
- `scripts/test_voicebox_narrate.py`：不访问网络的确定性单元测试。
- `scripts/README.md`：命令、批量输入格式、运行条件和验证方式。
- `agents/openai.yaml`：支持相应宿主时使用的界面元数据。

## 为什么不使用 MCP

Voicebox 的 REST API 已覆盖健康检查、声音档案读取、生成任务、SSE 状态和音频下载。配音是参数明确、可验证的确定性操作，直接调用 REST API 更容易记录输入、等待状态、验证文件和形成 timing manifest；本 skill 不需要把 Voicebox 注册成长期 MCP 服务。

## 默认预设与模型选择

脚本通过 `capabilities` 命令读取当前服务器的 OpenAPI schema（接口模式），动态展示可选择的 engine、model size 和 language。`daily` 与 `precision` 只固定当前默认工作流；预设之外的候选能力仍以实时接口为准。

本地工作流提供两套经过实际对比后确定的 preset（预设）：

| preset | engine / model | 最终速度 | 用途 |
| --- | --- | --- | --- |
| `daily` | Qwen 0.6B | `1.2×`，保留音高 | 默认日常旁白 |
| `precision` | Qwen 1.7B | `1.2×`，保留音高 | 更重视清楚咬字 |

未指定 preset 时使用 `daily`。两个 preset 都默认 `1.2×`；显式的 `engine`、`model_size` 和 `speed` 会覆盖 preset。变速只压缩既有节奏，不会修复错误断句，输入旁白仍应使用短句和明确标点。

选择仍受组合约束：

- cloned profile（克隆声音档案）与 preset profile（预设声音档案）支持的引擎不同；
- 某些引擎只支持部分语言；
- `0.6B / 1.7B / 1B / 3B` 等大小属于不同引擎家族，不能任意交叉；
- 服务器枚举是候选集合，最终兼容性由 Voicebox 实际请求校验。

需要在预设之外选择速度和质量时，以同一句短样本比较候选，再锁定完整批次。

## 配音包

批量输入是 UTF-8 JSON：

```json
{
  "language": "zh",
  "preset": "daily",
  "sections": [
    {"id": "hook", "text": "第一段旁白。", "instruct": "自然、清楚"},
    {"id": "proof", "text": "第二段旁白。"}
  ]
}
```

输出目录包含逐段最终 WAV 和 `narration-manifest.json`。manifest 使用默认 `1.2×` 或显式覆盖速度处理后的真实音频帧数累计段落起止时间，并记录 preset、原始/最终时长、speed、正文/音频哈希、生成 ID、engine 和 model size；它是 `507-video` 的声音时间交接，不是逐字字幕对齐文件。

## 运行条件

- Python 3.10+，REST 客户端只使用标准库；
- FFmpeg，用于 `atempo` 保留音高变速；
- 已安装并完成首次设置的 Voicebox；
- Voicebox 中已存在由人确认、当前用途已获授权的声音档案；
- 默认服务地址为 `http://127.0.0.1:17493`，可用 `VOICEBOX_URL` 或 `--server-url` 覆盖；
- macOS 可以自动打开 Voicebox；其他平台先手动启动应用或服务。

个人声音样本、档案、生成音频和项目 manifest 都是本地产物，不属于此公开仓库内容。
