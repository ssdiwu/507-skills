# Rednote Project Spec

`rednote-project.json` 是脚本消费的机器规格。完整结构约束见 `../assets/rednote-project.schema.json`。

## 文章模式最小示例

```json
{
  "mode": "article",
  "title": "作品标题",
  "author": "示例作者",
  "visualSystem": "swiss",
  "themePreset": "swiss-blue",
  "excludedContent": [],
  "pages": [
    {
      "type": "cover",
      "point": "文章的中心判断与阅读承诺",
      "sourceMap": "主稿标题",
      "layout": "type",
      "title": "封面主标题",
      "subtitle": "封面副标题"
    },
    {
      "type": "article",
      "sourceMap": "主稿第 1–5 段与图 1",
      "blocks": [
        {"type": "paragraph", "text": "原文正文，保持措辞和顺序。"},
        {"type": "heading", "text": "原文小节标题"},
        {"type": "paragraph", "text": "标题可以出现在页面中段。"},
        {"type": "screenshot", "src": "assets/evidence.png", "chrome": "none", "fit": "contain", "position": "center"}
      ]
    }
  ]
}
```

## 顶层合同

- `mode`：必须显式选择 `article` 或 `summary`。用户只要求小红书图文时使用 `article`；只有明确要求提炼时使用 `summary`。
- `visualSystem`：`editorial` 或 `swiss`，整组只使用一套。
- `themePreset`：必须属于当前视觉系统；可选值见 [`styles.md`](styles.md)。
- `theme`：只覆盖七个颜色变量，不改变视觉系统和页面结构。
- `excludedContent`：必填数组。文章模式必须为空；摘要模式每项记录未进入图卡的重要内容及去向。
- `pages`：第一项是独立封面，后续为物理正文页。文章模式中的这些页，是打平旧分页后由连续内容流经真实浏览器高度编译出的结果；旧 `pages` 分组、小节边界和估算页数不得直接沿用。摘要模式先形成显式观点页。
- `wechatCovers`：可选；出现时必须同时提供 `main` 与 `share`。

旧 `layoutMode` 和 `stylePreset` 已移除。渲染器遇到旧字段会明确失败，不静默兼容。

## 文章模式页面合同

封面仍填写 `point`、`sourceMap` 和 `layout`，因为它需要明确阅读承诺和构图。正文页只填写：

- `sourceMap`：当前页覆盖的原文段落和证据位置。
- `blocks`：按原文顺序排列的正文、原小节标题、列表、图片、截图与图注。

文章正文页不接受 `point`、`layout` 或页级 `heading`。小节标题使用 `heading` 内容块，因此可以出现在页面中段。正文不渲染页眉、页码、逐页标题、头像或摘要卡片；封面为 1500×2000，正文页为 1440×2400。

规格中的物理页必须已经是实际分页结果，而不是待验证候选。页数变化只有在全量渲染后，规格页数、清单 `pageCount`、实际 JPG 数量和联系表页数完全一致，清单 `renderedPages` 是 1 到末页的完整序列，且文件名连续、没有旧页残留时才成立。局部重渲染不改变页数，`renderedPages` 只记录本次重渲染页面。

## 摘要模式页面合同

摘要模式正文页必须填写：

- `point`：本页唯一观点。
- `sourceMap`：观点与关键证据的来源位置。
- `layout`：`statement`、`evidence`、`comparison`、`steps`、`list`、`data` 或 `closing`。
- `heading`：可选的观众可见标题，不得引入第二个观点。
- `blocks`：服务本页观点的证据和说明。

两种模式的每个正文页都必须有至少一个 `blocks` 内容块。

## 未入选内容

文章模式不允许未入选内容，`excludedContent` 必须为 `[]`。以下去向只适用于摘要模式：

`excludedContent[].destination` 使用固定值：

- `postBody`：帖子正文。
- `companionCopy`：配套文案或附件说明。
- `series`：后续系列。
- `notUsed`：明确不采用。

## 内容块

- `paragraph`：普通文字；文章模式默认统一正文层级，摘要模式可使用 `body`、`lead`、`big`、`muted`。
- `heading`：原文已有的小节标题；`level` 为 2 或 3。文章模式中可出现在任意正文位置。
- `list`：原文列表；`items` 为 1–12 个字符串，`ordered` 可选。
- `note` / `quote`：提示和关键判断。
- `image`：普通照片或视觉证据；显式设置 `fit` 与 `position`。
- `screenshot`：界面、网页、终端或代码截图；`chrome` 可为 `none`、`browser`、`phone`。
- `motion`：动态图片槽；必须提供用户选定的本地短视频和 `durationSec`。
- `cards`：1–3 项并列信息。
- `flow` / `timeline`：2–5 项步骤或演化节点。

文章模式只接受 `paragraph`、`heading`、`list`、`note`、`quote`、`image`、`screenshot` 与 `motion`；`cards`、`flow`、`timeline` 属于摘要表达，不得用来把原文重新包装成课件。

`motion` 的 `durationSec` 必须在 1–5 秒，`posterTimeSec` 必须位于 `startSec` 与片段结束之间。每页最多一个动态图片槽。

## 公众号封面对

```json
{
  "wechatCovers": {
    "main": {
      "point": "同一中心判断",
      "sourceMap": "P1 / 主封面",
      "layout": "split",
      "title": "接近完整的标题",
      "image": "assets/cover.png"
    },
    "share": {
      "point": "同一中心判断",
      "sourceMap": "P1 / 分享封面",
      "layout": "type",
      "title": "更短的方形标题"
    }
  }
}
```

`main` 与 `share` 分别构图，不能把 21:9 机械裁成 1:1。

## 本地素材

图片、截图、视频和头像使用相对或绝对本地路径；相对路径以 `rednote-project.json`（项目规格）所在目录为起点。图片可以使用 `data: URI`（内嵌数据统一资源标识符），远程 `http:// / https:// URL`（网页传输网址）不接受。清单只记录可迁移的相对引用；位于规格目录外的绝对来源写为 `external-file:<文件名>`（外部文件标识），并以 `SHA-256`（摘要）确认内容，不写入本机绝对路径。

## 局部重渲染

只有纯静态小红书图卡可以使用 `--pages 3,5`（指定页面参数）。未选页面的规格、页数和全局配置必须与上一份 `manifest`（清单）一致；页数变化时必须全量重渲染，在候选目录完成页面、联系表与清单验证后再发布并清除旧页。含动态图片槽或公众号封面对时也必须全量重渲染。
