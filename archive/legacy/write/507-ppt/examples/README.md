# 507-ppt 验收样例

本目录同时保留兼容样例与三轴系统样例：

- `collaboration-swiss.html` / `collaboration-magazine.html`：由 legacy content v1 与旧 preset 入口重建，证明旧调用仍可迁移；它们不是底层样式分类。
- `system-showcase.html` / `system-showcase.pptx`：由同一 content v3 与 visual-plan 生成，覆盖 13 个语义叶组件、6 类代表呈现、受控 treatment、表格背景网格抑制、原生可编辑 chart/table 和 phrase-aware 中文换行。
- `presentation-pairwise.html` / `presentation-pairwise.pptx`：八页逐一覆盖八类视觉呈现与四种 treatment，同时压测双序列 chart 和三素材 UI 页；PPTX 中 editorial-print 与 hand-drawn 明示为 adapted，其余为 native。
- `system-showcase.visual-plan.json`：随产物交付的视觉决定，不与内容包混写。
- `system-prototypes/`：同一真实内容的 3 个 candidate、联系表与 `approved-prototype-manifest.json`，展示推荐、用户选择与文件哈希绑定的顺序；混合时必须另建合并原型再批准。
- `system-showcase.*.manifest.json`、`presentation-pairwise.*.manifest.json` 与 evidence/report 文件：逐页记录输入、计划、组合、载体支持、截图、中文换行和验证结果。

`test_html.sh` 在临时目录重建当前 v3，并用真实 Chrome 覆盖 showcase/pairwise 的逐页无转场 capture、交互、mobile、无 JavaScript、reduced-motion、JS failure、中文行数与 table 背景抑制。HTML evidence 内的 `browser-report.json` 绑定成品/内容/计划哈希和 producer 环境；PPTX 通过 officecli 生成并保留逐页 evidence 截图，不能用截图冒充可编辑 chart/table。样例记录只说明其指定输入和环境的结果，不能自动证明本轮新作品通过。

样例只使用公开 fixture 和项目内原创 CSS/SVG 素材；任何实际第三方素材必须在 `../third-party-notices.md` 和对应 manifest 中登记。
