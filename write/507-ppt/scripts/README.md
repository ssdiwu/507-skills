# 507-ppt 脚本

此目录存放确定性脚本：共享组件与设计令牌、环境探测、`HTML`（网页）结构/交互/截图检查、`PPTX`（PowerPoint 演示文稿）生成/验证、`manifest`（清单）校验、来源报告和样式/内容报告。逐页截图内容检查与联系表使用 `Pillow`（图像处理库）；演示文稿生成和截图使用 `officecli`（办公文档命令行工具）。样例和验证入口见 `../examples/README.md`（样例说明）。
常用入口：`test_design_system.py`、`test_html.sh`、`test_html_browser.sh`、`validate_pptx.py`、`validate_manifest.py`、`validate_provenance.py`、`check_style_content.py`。

`generate_pptx.py`（演示文稿生成脚本）在最终输出的同目录候选文件中生成并关闭演示文稿，调用 `validate_pptx.py`（演示文稿验证脚本）完成结构、格式、备注、替代文本与逐页截图内容验证后才原子替换目标；生成或验证失败时已有文件保持不变。原子替换回归入口为 `python3 -m unittest test_generate_pptx.py`（演示文稿原子替换回归命令）。

脚本不负责决定内容、风格或素材授权；这些由输入合同与 `SKILL.md`（技能说明）约束。所有脚本必须声明运行条件、输入、输出、失败码和最小测试命令；运行时代码、依赖和资产必须在 `../third-party-notices.md`（第三方来源声明）与 `manifest`（清单）中有来源记录。
