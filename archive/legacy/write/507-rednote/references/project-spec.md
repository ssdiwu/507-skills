# RedNote 项目状态合同

当前 runtime 使用三个职责分离的文件。完整机器约束见 [`visual-plan.schema.json`](../assets/visual-plan.schema.json) 与 [`paged-content.schema.json`](../assets/paged-content.schema.json)。

## `content.md`

保存最终可见平台稿与标准 Markdown 结构。它不保存页码、逐页布局、组件坐标或渲染 HTML。

## `visual-plan.json`

保存：

- `mode: article | summary`；
- 整组唯一基础 `designLanguage`；
- 按语义组件解析的 `presentations`；
- 受控 `treatments`；
- `fontFamily`、正文字号、行距、字符占用宽度与页面留白；
- 封面文字、本地素材引用和 page chrome。

`presetId` 是快捷入口，不替代已解析三轴字段。相对素材路径以作品的 `小红书/` 目录为根；远程 URL 不接受。

## `paged-content.json`

只由 runtime 写入，记录：

- `content.md`、`visual-plan.json` 与 runtime 身份；
- 固定 1500×2000 输出画布；
- 页面顺序、自然/强制/组件续页原因；
- 页面实际可见正文与独立 page chrome；
- 语义组件 fragment、来源范围、续页位置和几何测量；
- 页面 overflow 验证。

任一分页输入哈希变化后，旧 `paged-content.json` 立即过期，必须由 runtime 重新生成。`content.md` 与 `visual-plan.json` 只是输入例子；runtime 运行程序、本地素材等实际分页输入也包括在内，不能只检查正文和视觉计划。`fontSet` 绑定 runtime 内嵌字体与许可证的固定 SHA-256；字体选择或字符占用宽度变化也会使分页过期。Agent 不得根据字符数或旧页面手写更新它。

## 旧 `rednote-project.json`

旧文件把视觉系统、主题、逐页布局和物理 `pages/blocks` 混为输入，只用于一次性迁移以及尚未迁出的动态媒体/公众号后处理。新 article 项目不得以它作为正文或分页的当前依据；迁移完成后删除旧主路径。
