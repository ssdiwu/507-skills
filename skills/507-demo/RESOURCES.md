# 507-demo 资源声明

本文件是本技能自有文件和直接共有依赖的唯一维护源。files 路径相对本技能目录，uses 路径相对集合根目录；包含按条件读取和运行所需的依赖，不表示每次任务全部调用。

本技能只保存入口、元数据、本声明和专用文字方法；共有脚本及组件放 lib，原始素材、客户资料和生成产物留在获授权的业务或证据位置，不放技能目录。登记文件不能取消这些边界。

```json
{
  "schema": 1,
  "files": [
    "RESOURCES.md",
    "SKILL.md",
    "agents/openai.yaml",
    "references/composition.md",
    "references/motion.md",
    "references/source.md",
    "references/verification.md"
  ],
  "uses": [
    "lib/README.md",
    "lib/components/visual-components.md",
    "lib/components/visual-runtime.md",
    "lib/components/visual-runtime/LICENSE",
    "lib/components/visual-runtime/UPSTREAM.json",
    "lib/components/visual-runtime/package.json",
    "lib/components/visual-runtime/references/choreography.md",
    "lib/components/visual-runtime/references/craft.md",
    "lib/components/visual-runtime/references/framing.md",
    "lib/components/visual-runtime/references/kit.md",
    "lib/components/visual-runtime/references/motion.md",
    "lib/components/visual-runtime/references/rehearse.md",
    "lib/components/visual-runtime/references/review.md",
    "lib/components/visual-runtime/scripts/render-artifact.mjs",
    "lib/methods/artifact-rendering.md"
  ]
}
```
