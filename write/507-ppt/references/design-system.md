# 视觉系统合同

`507-ppt` 的公开视觉系统由 `scripts/design_system.py` 中的**页面组件**与**设计方向**组成。两者都是共享输入合同的一部分：HTML 与 `.pptx` 必须消费同一份 JSON（JSON 数据格式）内容包，并保持页面 ID、可见文本、notes（讲者备注）和素材替代文本对应。

## 组件

首批组件：`cover`、`section`、`image-text`、`three-part`、`comparison`、`process`、`metric`、`quote`。

每个页面必须有 `id`、`kind`、`goal`、`notes`（或明确 `noNotes`）；组件额外必填字段、项目数量与素材 `alt`（替代文本）由 `validate_deck` 校验。组件服务内容关系，不能仅因颜色、左右翻转或装饰变化新增。

## 设计方向

当前方向：`swiss`、`magazine`、`cobalt`、`clay`、`forest`、`noir`。每项都声明：纸面色、正文色、强调色、中文/拉丁/元数据字体、形状圆角和密度。

方向可改变视觉表达，不能改变输入内容、页面顺序、讲者备注或素材语义。HTML 以 CSS（层叠样式表）变量映射；`.pptx` 以字体角色、色彩、版式和形状映射。复杂效果可按载体降级，但公开组件和方向必须在两种载体中均可用。

## 验证

`test_design_system.py` 以 `fixtures/system-showcase.json` 覆盖全部组件，并确保每个方向具备完整且互异的令牌集合。生成后用 `check_style_content.py` 复核可见文本与方向标记；载体验证继续遵循各 recipe（制作与验证说明）。
