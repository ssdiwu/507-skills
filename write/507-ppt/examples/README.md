# 507-ppt 验收样例

`collaboration-baseline.json` 的四页内容当前生成两种 PPTX 与两种单文件 HTML：瑞士风、杂志风各一份。每个产物有 manifest、固定视口截图；PPTX 有 officecli 验证，HTML 可运行 `../scripts/test_html.sh` 重建 normal、reduced-motion/mobile 与 no-JS 截图。`contact-sheet.png` 为四象限 2×2 联系表，可用 Pillow 重新拼接（取 PPTX/HTML 各一份封面截图）。

样例只使用公开 fixture 和项目内原创 CSS/SVG 素材；任何实际第三方素材必须在 `../third-party-notices.md` 和对应 manifest 中登记。