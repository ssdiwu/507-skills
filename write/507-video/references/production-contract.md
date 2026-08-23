# 视频制作合同

`507-video` 先把上游内容和素材归一为可制作合同。合同描述的是“这一版视频必须成立什么”，不是固定工具模板。

## 最低字段

| 字段 | 要回答的问题 |
| --- | --- |
| `message` | 观众看完应记住的一个核心主张是什么？ |
| `audience` | 给谁看；他们已经知道什么？ |
| `destination` | 平台、画幅、时长、分辨率和交付格式是什么？ |
| `contentSource` | 哪份主稿、旁白内容包、创作包或既有项目是内容真相源？ |
| `timingAuthority` | 真人配音、TTS、录像、音乐还是人工时间线决定节拍？ |
| `assetBoundary` | 哪些素材可用、来源和授权是什么、缺失时怎样降级？ |
| `claimBoundary` | 哪些事实可以说，哪些没有证据不能暗示？ |
| `privacyBoundary` | 哪些账号、路径、会话、人员或业务信息必须删除或遮挡？ |
| `reviewGate` | 用户在哪里审片；什么表达才算当前版本可渲染？ |

用户已经在 brief、storyboard、style lock 或项目 README 中回答的内容直接引用，不再复制成第二事实源。

## 条件制作 profile

通用合同只锁定所有视频都必须成立的字段；特定片种需要新增可验证约束时，使用条件 profile 扩展现有 brief、style lock、storyboard、素材清单和审片记录，不新增总控 skill 或重复状态源。

当目标是用网站、桌面端或移动端产品的真实页面与功能状态制作宣传片时，在项目现有入口记录 `productionProfile: product-promo`，并读取[产品宣传片 profile](product-promo-profile.md)。它追加产品事实源、必须展示功能、设计令牌到 styleframe、功能到镜头映射、真实页面采集、可选镜头语法、音频节拍条件和独立关键帧终检；通用时间基准、Studio 审片门与本地母版停止点保持不变。

## 分镜最小字段

每个节拍至少写清：

- 起止或相对时长；
- 叙事任务；
- 旁白/声音意图；
- 观众看见的画面与字幕；
- 画面所证明的事实；
- 素材来源或待补缺口；
- 进入和离开该节拍的方式。

不要把分镜写成纯镜头清单。没有叙事任务和证据边界的镜头，无法判断该保留还是删除。

## 项目状态

新项目可以采用下列最小角色；已有项目只需提供等价文件，不强制改名：

```text
<video-project>/
├── README.md                 # 入口、运行方式、当前状态
├── BRIEF.md                  # 制作合同
├── STORYBOARD.md             # 节拍、声音、画面与证据
├── STYLE.md                  # 视觉和动效锁定（也可沿用 frame.md / style-lock.md）
├── assets/manifest.json      # 素材角色、来源、授权、状态
├── reviews/                  # 联系表、关键帧和审片记录
├── renders/                  # 带版本的预览与母版
└── DELIVERY.md               # 交付回执
```

项目源代码遵循现有 Remotion 工程结构，不为匹配本目录树移动可运行代码。

## 素材清单

每条素材至少记录：

- 稳定 ID 与在项目内的相对路径；
- `background / inline / broll / overlay / voice / bgm / sfx` 角色；
- 对应节拍；
- 媒体类型、尺寸、时长和状态；
- `user-owned / licensed / generated / public-domain` 等来源与必要 credit；
- 隐私处理、裁切或转码说明；
- `planned / resolved / rejected / replaced` 状态。

付费生成在执行前追加成本估算和用户确认。零外部素材也应允许得到可读的视频，不能为了“画面丰富”静默消费。

## 时间基准

时间基准必须来自真实可测对象：

- 真人配音：以最终清理/变速后的音频为准；
- TTS：以实际生成音频与字幕为准；
- `507-narrate` 配音包：以 `completed` manifest 中逐段 WAV 的实测帧数、起止时间与哈希为准；
- 录像主导：以选定片段的真实入出点为准；
- 音乐主导：以确认后的节拍和段落为准；
- 人工时间线：只用于没有外部主时钟的纯动效项目，并写明依据。

一个项目只有一个主时间基准。其他素材向它对齐；主基准变化后，字幕、转场、composition duration 和预览确认全部失效。

## 设计来源

本合同首先来自实际完成的多场景案例工作流；同时把 [Agents365-ai/video-podcast-maker](https://github.com/Agents365-ai/video-podcast-maker)（仓库当前为 `CC BY-NC 4.0`）作为对照样本，确认 per-video 素材清单、真实媒体对时、Studio 审片、最小重跑和统一验收确有复用价值。这里只独立重写不受表达保护的通用工作方法，不复制其 skill 文本、代码、schema、模板、组件或资产，也不继承其 4K/TTS/发布产品合同。
