# 第三方 notices

`507-rednote` 的 HTML、CSS、Python 代码和 fixture 均为本项目原创，不复制外部参考项目的代码、模板、文档正文或视觉资产。下列项目只作为生成或验证时调用的环境工具；它们不被嵌入单文件 HTML、JPG、MOV 或 `.pvt` 交付物中。

| 名称 | 已验证版本 | 来源 | 许可证状态 | 用途 | notice |
| --- | --- | --- | --- | --- | --- |
| Python | 3.14.5 | `https://www.python.org/` | PSF License | 运行规格校验、渲染编排与清单生成 | 外部运行时，不嵌入产物 |
| Pillow | 12.1.0 | PyPI `Pillow` | MIT-CMU | 图片格式转换、联系表和封面对组合预览 | 外部 Python 依赖，不嵌入产物 |
| Google Chrome | 150.0.7871.125 | 系统浏览器 | Google 专有软件 | 本地 HTML 布局检查与截图 | 外部工具，不嵌入产物 |
| FFmpeg / ffprobe | 8.1.1 | `https://ffmpeg.org/`；本机 Homebrew 构建 | GPL-3.0-or-later（当前构建启用 GPL 组件） | 短视频探测、首帧提取与整卡 MOV 合成 | 外部 CLI，不嵌入产物；产物清单记录调用版本 |
| makelive | 0.6.2 | `https://github.com/RhetTbull/makelive` / PyPI `makelive` | MIT | 为 JPG + MOV 配对写入 Live Photo 元数据并生成 `.pvt` | 外部 CLI，不嵌入产物；运行时不自动安装 |

版本是本轮验证环境的可检查事实，不是最低或永久锁定版本。脚本的支持范围与安装方式以 `scripts/README.md` 为准；依赖缺失时必须明确失败，不得自动联网安装。
