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
| `officecli` | 1.0.139 | `https://d.officecli.ai`（官方安装源） | 商业 CLI，未附带公开 OSS LICENSE 文件；作为外部工具调用 | 生成/验证 `.pptx`（schema、issues、notes、alt、截图） | 产物不依赖；`.pptx` 可在标准 Office 编辑器独立打开 |
| `browser-act-cli` | 0.1.30 | PyPI `browser-act-cli`、`https://www.browseract.com` | PyPI METADATA 未声明 License 字段；作为外部 CLI 调用 | HTML 浏览器交互与 a11y 断言 | 产物不依赖；HTML 可离线打开 |
| Pillow | 12.1.0 | PyPI `Pillow` | HPND / PIL License（本地安装元数据） | 生成四象限 contact sheet；不嵌入 HTML/PPTX | 仅开发工具；不随产物分发 |
| Google Chrome | 150.0.7871.125 | 系统浏览器 | Google 专有软件 | HTML 截图与退化/响应式测试 | 产物不依赖；HTML 可离线打开 |

不明许可证的项不得内嵌进产物；上表工具仅作环境工具使用，不改变交付物的许可证状态。
