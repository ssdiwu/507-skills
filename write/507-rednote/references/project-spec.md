# Rednote Project Spec

`rednote-project.json` 是脚本消费的机器规格。完整约束见 `../assets/rednote-project.schema.json`。

## 最小示例

```json
{
  "title": "作品标题",
  "author": "示例作者",
  "avatar": "assets/avatar.png",
  "layoutMode": "longform",
  "stylePreset": "newspaper",
  "pages": [
    {
      "type": "cover",
      "kicker": "眉题",
      "title": "封面主标题",
      "subtitle": "封面副标题",
      "image": "assets/cover.png"
    },
    {
      "type": "article",
      "heading": "正文页标题",
      "sourceMap": "主稿第 3–4 段 / 论证链第 1 步",
      "blocks": [
        {"type": "paragraph", "variant": "lead", "text": "正文。"},
        {"type": "quote", "text": "本页关键判断。"}
      ]
    }
  ]
}
```

## 分页模式

- `layoutMode: longform`（默认）：`pages` 只描述章节和段落顺序。浏览器按实际字号、图片高度和安全区自动填满物理页；章节标题与第一段作为整体排版，但只在这组内容放不下时换页，不强制章节另起一页。最终页数见 `render-manifest.json`。
- `layoutMode: cards`：`pages` 与最终图片一一对应，适合清单、流程、对比等“一页一观点”内容。

长文不得为了控制页数提前把段落切成稀疏小页。需要保留来源映射时，每个逻辑块继续填写 `sourceMap`，脚本会合并到实际物理页。`closing: true` 会绑定最后两段与结论框，并对倒数页面做密度再平衡，避免结论或图片孤悬。

## 样式

- `stylePreset` 选择整套外观；可选值与适用场景见 [`styles.md`](styles.md)。
- 未填写时使用 `editorial-default`。
- 同一项目只选一个主样式；换样式不改逻辑文案。
- `theme` 只用于覆盖颜色变量，不替代样式预设。

## 页面类型

- `cover`：封面。支持眉题、主标题、副标题、作者和主图。
- `article`：正文页。`heading` 可选；有标题表示章节首页，省略标题表示承接上一页的长文续页。续页仍必须填写 `sourceMap`。

长文默认按章节连续跨页，不要为了每个物理页都显示标题而填写 `heading`。只有清单、流程、对比等独立卡片页才适合每页标题。

## 内容块

- `paragraph`：普通段落；`variant` 可为 `body`、`lead`、`big`、`muted`。
- `note`：浅色提示块。
- `quote`：深色结论块。
- `image`：本地图片；支持 `height`、`fit`、`position`、`caption`。
- `cards`：1–3 个卡片；适合对比、阶段或并列信息。
- `flow`：2–4 个顺序节点。
- `timeline`：2–5 个时间/演化节点。

文字支持少量安全标记：

- `**文字**`：加粗。
- `==文字==`：绿色强调。
- `` `文字` ``：行内代码。

不接受任意 HTML。图片只接受本地相对/绝对路径或 `data:` URI，不接受 `http://` / `https://`。

## 图片路径

相对路径以 `rednote-project.json` 所在目录为起点。为了让作品可迁移，优先把头像和证据图复制到作品目录，再写相对路径。

## 局部重渲染

完成过一次全量渲染后，若只修改局部页面且页数、主题、头像等全局配置未变化，可传 `--pages 4,6,7`。页码按 `pages` 数组从 1 开始，包括封面；联系表和渲染清单会基于全部页面重建。页数或全局视觉变化必须全量重渲染。
