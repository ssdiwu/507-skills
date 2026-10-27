# 第三方 notices

`507-rednote` 的 HTML、CSS、JavaScript、Python 代码和 fixture 均为本项目原创，不复制外部参考项目的代码、模板、文档正文或视觉资产。下列依赖或环境工具按实际用途记录；浏览器 bundle 内嵌的依赖随本地工作台分发，不进入用户正文、图片、视频或凭据。

| 名称 | 已验证版本 | 来源 | 许可证状态 | 用途 | notice |
| --- | --- | --- | --- | --- | --- |
| Python | 3.14.5 | `https://www.python.org/` | PSF License | 运行规格校验、渲染编排与清单生成 | 外部运行时，不嵌入产物 |
| Pillow | 12.1.0 | PyPI `Pillow` | MIT-CMU | 图片格式转换、联系表和封面对组合预览 | 外部 Python 依赖，不嵌入产物 |
| Google Chrome | 150.0.7871.125 | 系统浏览器 | Google 专有软件 | 本地 HTML 布局检查与截图 | 外部工具，不嵌入产物 |
| FFmpeg / ffprobe | 8.1.1 | `https://ffmpeg.org/`；本机 Homebrew 构建 | GPL-3.0-or-later（当前构建启用 GPL 组件） | 短视频探测、首帧提取与整卡 MOV 合成 | 外部 CLI，不嵌入产物；产物清单记录调用版本 |
| makelive | 0.6.2 | `https://github.com/RhetTbull/makelive` / PyPI `makelive` | MIT | 为 JPG + MOV 配对写入 Live Photo 元数据并生成 `.pvt` | 外部 CLI，不嵌入产物；运行时不自动安装 |
| marked | 18.0.10 | npm `marked` / `https://github.com/markedjs/marked` | MIT | 把本地 `content.md` 解析为 GFM 语义组件 | 嵌入 `runtime/dist/app.js`；许可证见 npm 包 |
| DOMPurify | 3.4.14 | npm `dompurify` / `https://github.com/cure53/DOMPurify` | MPL-2.0 OR Apache-2.0 | 净化 Markdown 产生的浏览器 HTML | 嵌入 `runtime/dist/app.js`；本项目按 Apache-2.0 许可使用 |
| esbuild | 0.28.2 | npm `esbuild` / `https://github.com/evanw/esbuild` | MIT | 维护时将前端源码与依赖打包为离线 runtime bundle | 仅构建依赖，不进入 runtime bundle |
| Adobe Source Han Sans CN Variable | 2.005R | `https://github.com/adobe-fonts/source-han-sans/blob/release/Variable/WOFF2/OTF/Subset/SourceHanSansCN-VF.otf.woff2` | SIL OFL 1.1 | 默认中文连续阅读字体 | 原样内嵌官方 WOFF2；SHA-256 `7087698d52240614659957608d8c4ad446759aee3208409dc9f566412e7af8f4`；许可证见 `runtime/fonts/OFL-Source-Han-Sans.txt` |
| Adobe Source Han Serif CN Variable | 2.003R | `https://github.com/adobe-fonts/source-han-serif/blob/release/Variable/WOFF2/OTF/Subset/SourceHanSerifCN-VF.otf.woff2` | SIL OFL 1.1 | 可选中文编辑阅读字体 | 原样内嵌官方 WOFF2；SHA-256 `808cb3203bb9cdd6b166a8a656a0c7608a7dc2a31c41c2cd0374550cae445471`；许可证见 `runtime/fonts/OFL-Source-Han-Serif.txt` |

版本是本轮验证环境的可检查事实，不是最低或永久锁定版本。两套字体依 SIL OFL 1.1 可用于商业产品、嵌入并随软件再分发，但不得单独出售；再分发时保留版权与许可证，修改版本还需遵守 Reserved Font Name（保留字体名称）条件。本记录不是法律意见。脚本的支持范围与安装方式以 `scripts/README.md` 为准；依赖缺失时必须明确失败，不得自动联网安装。
