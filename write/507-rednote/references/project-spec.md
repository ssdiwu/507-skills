# Rednote Visual Summary Project Spec

`rednote-project.json` 是脚本消费的机器规格。完整结构约束见 `../assets/rednote-project.schema.json`。

## 最小示例

```json
{
  "title": "作品标题",
  "author": "示例作者",
  "visualSystem": "editorial",
  "themePreset": "editorial-paper",
  "excludedContent": [
    {
      "summary": "完整命令说明",
      "reason": "不适合进入观点图卡",
      "destination": "companionCopy"
    }
  ],
  "pages": [
    {
      "type": "cover",
      "point": "中心判断与阅读承诺",
      "sourceMap": "P1 / 标题与中心判断",
      "layout": "split",
      "title": "封面主标题",
      "subtitle": "封面副标题",
      "image": "assets/cover.png"
    },
    {
      "type": "article",
      "point": "本页唯一观点",
      "sourceMap": "P2 / 主稿第 3–4 段",
      "layout": "statement",
      "heading": "观众可见标题",
      "blocks": [
        {"type": "paragraph", "variant": "lead", "text": "支持本页观点的必要说明。"},
        {"type": "quote", "text": "本页关键判断。"}
      ]
    }
  ]
}
```

## 顶层合同

- `visualSystem`：`editorial` 或 `swiss`，整组只使用一套。
- `themePreset`：必须属于当前视觉系统；可选值见 [`styles.md`](styles.md)。
- `theme`：只覆盖七个颜色变量，不改变视觉系统和页面结构。
- `excludedContent`：必填数组，可以为空；每项记录未进入图卡的重要内容及去向。
- `pages`：第一项是封面，后续每项是一张显式观点页，不再自动做长文分页。
- `wechatCovers`：可选；出现时必须同时提供 `main` 与 `share`。

旧 `layoutMode` 和 `stylePreset` 已移除。渲染器遇到旧字段会明确失败，不静默兼容。

## 页面合同

封面与正文都必须填写：

- `point`：本页唯一观点；封面填写中心判断与阅读承诺。
- `sourceMap`：观点和关键证据的来源位置。
- `layout`：当前页面结构。

封面布局：`type`、`split`、`image-led`。

正文布局：`statement`、`evidence`、`comparison`、`steps`、`list`、`data`、`closing`。

`heading` 可以比 `point` 更适合读者阅读，但不能引入第二个观点。每个正文页必须有至少一个 `blocks` 内容块。

## 未入选内容

`excludedContent[].destination` 使用固定值：

- `postBody`：帖子正文。
- `companionCopy`：配套文案或附件说明。
- `series`：后续系列。
- `notUsed`：明确不采用。

## 内容块

- `paragraph`：普通文字；`variant` 可为 `body`、`lead`、`big`、`muted`。
- `note` / `quote`：提示和关键判断。
- `image`：普通照片或视觉证据；显式设置 `fit` 与 `position`。
- `screenshot`：界面、网页、终端或代码截图；`chrome` 可为 `none`、`browser`、`phone`。
- `motion`：动态图片槽；必须提供用户选定的本地短视频和 `durationSec`。
- `cards`：1–3 项并列信息。
- `flow` / `timeline`：2–5 项步骤或演化节点。

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

图片、截图、视频和头像使用相对或绝对本地路径；相对路径以 `rednote-project.json` 所在目录为起点。图片可以使用 `data:` URI，远程 `http://` / `https://` URL 不接受。

## 局部重渲染

只有纯静态小红书图卡可以使用 `--pages 3,5`。未选页面的规格、页数和全局配置必须与上一份 manifest 一致；含动态图片槽或公众号封面对时必须全量重渲染。
