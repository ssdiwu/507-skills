---
name: 507-ppt
description: 原创视觉幻灯片制作：把已收口的逐页内容用可组合页面组件与设计令牌生成可编辑 .pptx 或独立单文件 HTML，并完成双载体验证。Use when user mentions 制作 PPT、生成 pptx、做成幻灯片、做 HTML deck、网页演示、slides rendering、presentation visual design、瑞士风 PPT、杂志风 PPT；内容仍需编排、讲稿或逐页稿未收口时使用 507-stage，不使用本 skill。
license: MIT
compatibility: 生成 .pptx 需要已可用的 officecli；生成 HTML 需要可写文件系统。HTML 的浏览器截图、交互和动态验证需要本机 Chrome/Chromium 或等价浏览器。
---

# 视觉幻灯片（507-ppt）

将**成熟逐页内容包**制作为可演示、可验证的视觉成品。支持可编辑 `.pptx` 与离线单文件 HTML；页面组件、配色、字体、形状与密度令牌组成独立视觉系统，并在两种载体上保持内容映射与风格辨识。

先读 [工作流合同](references/workflow-contract.md)、[视觉系统合同](references/design-system.md)、[风格合同](references/style-contracts.md) 和 [来源与许可证合同](references/provenance.md)。它们是本 skill 的实现边界。

## 不覆盖什么

- 不写讲稿、不决定演讲主线、不把草稿硬排成幻灯片；内容未收口返回 `507-stage`。
- 不制作小红书图卡；该任务进入 `507-rednote`。
- 不支持 legacy `.ppt`；只输出 `.pptx` 或单文件 HTML。
- 不自动安装 officecli、浏览器、字体或第三方依赖。
- 不复制任何受限外部演示 skill 的模板、样式、脚本、版式、验证器或资产。

## 输入门

开始前检查成熟逐页内容包是否具备：页面认知目标、观众可见内容、speaker notes 或无备注声明、受众/场景/时长，以及有授权的素材。

若缺其中任一项：说明缺口并返回 `507-stage`，不以视觉选择替代内容决定。

## 载体与设计方向选择

1. 用户已指定 `.pptx` 或 HTML：优先遵守。
2. 未指定：探测 officecli；可用则优先 `.pptx`，不可用则生成单文件 HTML。
3. 用户指定 `.pptx` 但 officecli 不可用：报告能力缺失，等待用户提供环境或改选 HTML；不自动安装。
4. 用户未指定方向：根据内容推荐——事实、产品、分析和方法论优先 `swiss` / `cobalt` / `forest`；叙事、品牌、人文、设计和观点表达优先 `magazine` / `clay`；需要强声明时选 `noir`。
5. 方向与载体只定义实现，不改变已经确认的页面认知目标和内容边界；公开组件与方向必须同时可用于 HTML 与 `.pptx`。

## 制作流程

### 1. 建立产物计划

在目标目录创建或更新产物清单，记录：输入内容版本、载体、风格、页面映射、素材授权/替代文本、验证状态和失败回退。

### 2. 生成 `.pptx`

仅在 officecli 已可用时执行：

- 使用 `officecli help` 核对属性，不猜命令；
- 每页写入 speaker notes；图片写入有意义的 alt text；
- 分别设置中文、拉丁和等宽字体角色；
- 按风格合同制作，不将 HTML 结构机械翻译为 PowerPoint；
- `save` 或 `close` 后运行 schema、format issues、notes、alt text 与逐页截图检查。

PPTX 规则、命令、样例与验证参考 [PPTX recipe](references/pptx-recipes.md)。

### 3. 生成 HTML

HTML 必须是离线可打开的单文件：

- DOM 保留所有标题、正文、图表说明和导航语义；WebGL/Canvas 只做装饰；
- 提供键盘、滚轮、触控和可聚焦按钮/索引导航；
- 支持无 WebGL、失败 JS、静态模式和 `prefers-reduced-motion`；
- 内嵌的第三方代码必须经许可证核验、保留 notice，并在来源清单记录；
- 运行结构、交互、视觉、响应式、无障碍和退化检查。

HTML runtime、版式和验证规则参考 [HTML recipe](references/html-recipes.md)。

### 4. 交付与回退

交付产物本身和验证清单：载体、风格、页面数、素材/alt、notes、验证命令、结果、已知降级。

- officecli 缺失：仅在用户未锁定 `.pptx` 时退到 HTML；
- 浏览器或 WebGL 缺失：保留可读静态 HTML，并报告未完成的视觉验证；
- 字体或素材缺失：不伪装为已验证，使用已授权 fallback 或停在缺口；
- 验证失败：保留失败证据，最小修复后重跑，不修改测试阈值来掩盖问题。

## 完成与接力

- **完成信号**：产物可打开；内容与输入包逐页对应；选择的风格可辨识；该载体要求的自动与视觉检查通过；产物清单与验证记录齐全。
- **产物**：`.pptx` 或单文件 HTML、素材和来源/notice（如有）、产物清单、验证报告、联系表或逐页截图。
- **候选出口**：用户进行视觉迭代时继续本 skill；内容需要调整时回 `507-stage`；成品可直接交付；将书面主稿改为社媒图文时进入 `507-rednote`。
- **回退条件**：内容未收口、来源/授权不清、用户要求的载体能力缺失或验证未通过时，不宣称完成。