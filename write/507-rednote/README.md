# 小红书图文（rednote）

`507-rednote` 把已经成立的书面作品改编为小红书 3:4 图片文章。

它先锁定中心判断与论证链，再按主稿章节生成 `copy-spec.md` 和结构化 `rednote-project.json`；长文由浏览器按真实排版高度从页头自动填到页脚，放不下的段落才移到新页，最后导出 1500×2000 JPG、联系表和渲染清单。续页默认不重复标题。

## 目录

- `SKILL.md`：触发、流程、边界与验收。
- `references/`：逻辑文案、18 套样式、项目规格和视觉复核方法。
- `assets/rednote-project.schema.json`：渲染输入契约。
- `scripts/`：样式预览、本地 HTML 生成、Chrome 截图、尺寸检查与联系表生成。

本 skill 不负责长文成稿、单张 AI 配图或小红书发布；对应能力分别交给 `507-forge`、`image-workflow` 和发布工具。
