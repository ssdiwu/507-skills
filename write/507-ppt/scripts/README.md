# 507-ppt 脚本

此目录存放确定性脚本：共享组件与设计令牌、环境探测、HTML 结构/交互/截图检查、PPTX 生成/验证、manifest 校验、来源报告和样式/内容报告。联系表由 Pillow 生成，样例和验证入口见 `../examples/README.md`。
常用入口：`test_design_system.py`、`test_html.sh`、`test_html_browser.sh`、`validate_pptx.py`、`validate_manifest.py`、`validate_provenance.py`、`check_style_content.py`。

脚本不负责决定内容、风格或素材授权；这些由输入合同与 `SKILL.md` 约束。所有脚本必须声明运行条件、输入、输出、失败码和最小测试命令；运行时代码、依赖和资产必须在 `../third-party-notices.md` 与 manifest 中有来源记录。