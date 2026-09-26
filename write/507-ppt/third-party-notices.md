# 第三方 notices

`507-ppt` 的完成依据是当前仓库、产物与命令输出。本台账按两类记录来源：交付物内嵌的第三方项，以及生成/验证用的外部工具。两类都必须可检查版本、来源、许可证状态、用途与 notice。

## 1. 交付物内嵌的第三方项

当前 HTML 与 PPTX 样例**不内嵌**任何第三方运行时代码、远程资源、字体或外部视觉资产。产物交付后不依赖下列工具运行（HTML 可离线打开，PPTX 为静态文件）。

| 名称 | 版本 | 来源 | 许可证 | 用途 | 离线嵌入与 notice 位置 |
| --- | --- | --- | --- | --- | --- |
| `workbench.svg` | 1 | `assets/workbench.svg` | 本项目原创，MIT 仓库许可证 | 公开 fixture 的抽象工作台示意图（PPTX 使用） | 文件随 skill 交付；不适用额外 third-party notice |

若后续向内嵌产物加入第三方项，许可证必须为 MIT、Apache-2.0、BSD、ISC、CC0 或等价宽松许可证，并在此补全字段。

## 2. 生成/验证用外部工具

下列外部 CLI/浏览器只在生成或测试时调用，不嵌入交付物。它们是环境工具，而非产物运行依赖。

| 名称 | 版本 | 来源 | 许可证状态 | 用途 | notice |
| --- | --- | --- | --- | --- | --- |
| `officecli`（办公文档命令行工具） | 1.0.149（样例重建与 CI） | `https://d.officecli.ai`（官方安装源）；[固定版本](https://github.com/iOfficeAI/OfficeCLI/releases/tag/v1.0.149) | Apache-2.0（[1.0.149 LICENSE](https://github.com/iOfficeAI/OfficeCLI/blob/v1.0.149/LICENSE)）；作为外部工具调用 | 生成/验证 `.pptx`（PowerPoint 演示文稿）的 schema（结构模式）、issues（问题）、notes（讲者备注）、alt（替代文本）与截图；CI 读回与代表页生成 | 产物不依赖；CI 的 Linux x64 二进制按官方 SHA-256 校验，不随仓库分发；`.pptx` 可在标准 Office 编辑器独立打开 |
| Pillow（图像处理库） | 12.1.0 | PyPI（Python 包索引）`Pillow`（安装包） | HPND / PIL License（许可证，本地安装元数据） | 检查逐页截图内容并生成四象限 contact sheet（联系表）；不嵌入 HTML（网页）/PPTX（PowerPoint 演示文稿） | 仅开发工具；不随产物分发 |
| `websockets`（WebSocket 客户端） | 16.0 | PyPI（Python 包索引）`websockets`（安装包） | BSD-3-Clause | 通过 Chrome DevTools Protocol 执行 HTML 验收及 SVG 备用 PNG 生成；不嵌入产物 | 仅开发工具；HTML 可离线打开 |
| Google Chrome | 154.0.8037.57（本次 PPTX 备用图与 showcase 证据） | 系统浏览器 | Google 专有软件 | HTML 截图、交互、退化、换行测试及 SVG 栅格化 | 产物不依赖；各批证据的实际版本写入 browser report 与 provenance report |
| Noto CJK 字体 | Ubuntu `fonts-noto-cjk` 包；实际安装版本见 CI 渲染证据中的 `font-package-version.txt` | [上游项目](https://github.com/notofonts/noto-cjk)；Ubuntu 系统包源 | SIL Open Font License 1.1（[Sans](https://github.com/notofonts/noto-cjk/blob/main/Sans/LICENSE)、[Serif](https://github.com/notofonts/noto-cjk/blob/main/Serif/LICENSE)） | Linux CI 的中文渲染与 SVG 栅格化备用字体 | 仅安装于 CI 环境；不复制或嵌入 PPTX/HTML，字体清单随 CI 证据保留 |

不明许可证的项不得内嵌进产物；上表工具仅作环境工具使用，不改变交付物的许可证状态。
