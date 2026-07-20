# 507-ppt：视觉幻灯片制作

`507-ppt` 是 `write/` 中的视觉制作 skill。它消费 `507-stage` 已收口的成熟逐页内容包，输出可编辑 `.pptx` 或离线单文件 HTML；不承担演讲内容编排。

## 目录

- `SKILL.md`：触发、边界、端到端制作合同。
- `references/`：工作流、视觉系统、风格、来源、载体 recipe、产物 manifest 与测试合同。
- `scripts/`：环境探测、PPTX 生成/验证、HTML 结构检查和浏览器截图入口。
- `examples/`：同内容的 PPTX/HTML 样例、逐页截图和 manifest。

## 视觉系统

组件、设计方向与载体映射由 [`references/design-system.md`](references/design-system.md) 定义，具体注册表位于 `scripts/design_system.py`。首批八个组件覆盖封面、章节、图文、并列、对比、流程、指标与收束；六个设计方向组合配色、字体、形状与密度令牌。

所有公开组件与设计方向均以同一 JSON（数据格式）内容包生成 HTML 与 `.pptx`。两种载体的效果可以不同，但页面 ID、可见内容、notes（讲者备注）、素材替代文本与风格辨识必须对应。

## 许可证与来源

本 skill 随仓库采用 MIT 许可。实现受 [来源与许可证合同](references/provenance.md) 约束：运行时代码、依赖和资产必须具有可检查的来源与 notice；任何第三方依赖须记录版本、来源、用途和许可证。

## 验证

- HTML：结构、交互、视觉截图、响应式、减少动态、无 WebGL/static fallback 与无障碍检查。
- PPTX：officecli schema、format issues、speaker notes、图片 alt text、字体角色与逐页截图检查。
- 系统：`system-showcase.json` 覆盖所有组件，`test_design_system.py` 校验每个设计方向的令牌完整性和 HTML 映射。
- 最终：同内容的瑞士/杂志 × HTML/`.pptx` 四象限联系表和独立来源审核。

具体命令和 fixture 在对应 recipe 与 `scripts/README.md` 中维护。