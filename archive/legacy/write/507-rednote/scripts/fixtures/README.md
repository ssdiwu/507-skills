# 测试样本

- `sample-project.json`：覆盖视觉摘要、来源映射、排除内容去向、编辑杂志视觉系统、观点页布局、截图块和公众号封面对的本地烟测规格；它检查合成输入下的输出，不代表真实作品已经验收。
- `sample-article-project.json`：旧 `rednote-project.json` 文章模式迁移 fixture；保留用于一次性兼容验证，不再代表当前 3:4 runtime 合同，不能用它的兼容通过代替当前运行程序的检查。
- `sample-runtime-content.md`：覆盖新 runtime 的连续正文、页中标题、列表、代码、表格、流程图、本地图片、完整 URL 与强制分页。
- `sample-runtime-summary.md`：覆盖同一 runtime 中以强制分页分隔、每段一个标题且完整落在一页的视觉摘要合同。
- `sample.svg`：不含外部素材的占位图，用于验证本地图片内嵌和截图框处理。

动态图片槽测试在临时目录中用 `ffmpeg` 生成合成视频，不向仓库提交二进制 fixture。
