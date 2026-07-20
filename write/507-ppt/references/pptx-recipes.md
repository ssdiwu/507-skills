# PPTX recipe

## 环境路由

运行 `python3 scripts/probe_environment.py`：输出 `officecli: true` 时默认载体为 `.pptx`；`--simulate-missing-officecli` 输出 HTML 路由。脚本不安装依赖。

## 生成

```bash
python3 scripts/generate_pptx.py --style swiss --output examples/collaboration-swiss.pptx
python3 scripts/generate_pptx.py --style magazine --output examples/collaboration-magazine.pptx
```

生成器消费公开 fixture 的四页页面种类：封面、图文、三项结构、引用收束；每页写 speaker notes，图文页写本地 SVG 的 alt text。字体按中文/拉丁角色分别设置；瑞士风使用无衬线与单锚点色，杂志风使用 Songti/Georgia 标题角色、暖色与深浅节奏。

## 验证

```bash
python3 scripts/validate_pptx.py examples/collaboration-swiss.pptx
python3 scripts/validate_pptx.py examples/collaboration-magazine.pptx
```

验证器检查 OpenXML schema、0 format issues、图片 alt text 与每页 notes。生成脚本后的固定逐页截图和页面映射存入对应 manifest，作为溢出和内容对照证据。