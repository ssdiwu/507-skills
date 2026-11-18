# 507-create 资源声明

本文件是本技能自有文件和直接共有依赖的唯一维护源。files 路径相对本技能目录，uses 路径相对集合根目录；包含按条件读取和运行所需的依赖，不表示每次任务全部调用。

本技能只保存入口、元数据、本声明和专用文字方法；共有脚本及组件放 lib，原始素材、客户资料和生成产物留在获授权的业务或证据位置，不放技能目录。登记文件不能取消这些边界。

```json
{
  "schema": 1,
  "files": [
    "RESOURCES.md",
    "SKILL.md",
    "agents/openai.yaml",
    "references/authorship.md",
    "references/proposal.md",
    "references/prose.md",
    "references/spoken.md"
  ],
  "uses": [
    "lib/README.md",
    "lib/components/tools/export/artifact-receipt.md",
    "lib/components/tools/export/artifact_receipt.py",
    "lib/components/tools/checks/check_prose.py",
    "lib/components/tools/checks/check_spoken.py",
    "lib/components/tools/export/media-adapters.md",
    "lib/components/tools/checks/text-checks.md",
    "lib/components/visual/visual-components.md",
    "lib/components/visual/catalog.json",
    "lib/components/visual/scenes/examples/record-browser/index.tsx",
    "lib/components/visual/scenes/examples/record-browser/records.css",
    "lib/components/visual/package.json",
    "lib/components/visual/scripts/component-library.mjs",
    "lib/components/visual/scripts/component-library.test.mjs",
    "lib/components/visual/scripts/render-artifact.mjs",
    "lib/methods/design/guides/apple-interaction.md",
    "lib/methods/design/guides/artifact-prompts.md",
    "lib/methods/design/guides/containers-and-motion.md",
    "lib/methods/design/guides/interaction-detail.md",
    "lib/methods/design/guides/target-design.md",
    "lib/methods/evidence-and-decisions/alternatives.md",
    "lib/methods/writing/artifact-contract.md",
    "lib/methods/design/artifact-rendering.md",
    "lib/methods/writing/author-and-source.md",
    "lib/methods/writing/author-interview.md",
    "lib/methods/evidence-and-decisions/authority-and-return.md",
    "lib/methods/writing/clear-expression.md",
    "lib/methods/collaboration/continuation.md",
    "lib/methods/evidence-and-decisions/decision-ownership.md",
    "lib/methods/evidence-and-decisions/evidence.md",
    "lib/methods/writing/explanation-progression.md",
    "lib/methods/evidence-and-decisions/external-research.md",
    "lib/methods/engineering/interaction.md",
    "lib/methods/design/media-production.md",
    "lib/methods/design/media-study.md",
    "lib/methods/evidence-and-decisions/question-frontier.md",
    "lib/methods/collaboration/task-coordination.md",
    "lib/methods/writing/title-promises.md",
    "lib/methods/evidence-and-decisions/validation.md",
    "lib/methods/design/visual-direction.md",
    "lib/methods/collaboration/work-records.md"
  ]
}
```
