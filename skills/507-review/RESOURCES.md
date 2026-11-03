# 507-review 资源声明

本文件是本技能自有文件和直接共有依赖的唯一维护源。files 路径相对本技能目录，uses 路径相对集合根目录；包含按条件读取和运行所需的依赖，不表示每次任务全部调用。

本技能只保存入口、元数据、本声明和专用文字方法；共有脚本及组件放 lib，原始素材、客户资料和生成产物留在获授权的业务或证据位置，不放技能目录。登记文件不能取消这些边界。

```json
{
  "schema": 1,
  "files": [
    "RESOURCES.md",
    "SKILL.md",
    "agents/openai.yaml"
  ],
  "uses": [
    "lib/README.md",
    "lib/components/check_run.py",
    "lib/methods/artifact-contract.md",
    "lib/methods/author-and-source.md",
    "lib/methods/authority-and-return.md",
    "lib/methods/continuation.md",
    "lib/methods/engineering-evidence.md",
    "lib/methods/evidence.md",
    "lib/methods/interaction-map.md",
    "lib/methods/prompt-instruction-audit.md",
    "lib/methods/validation.md"
  ]
}
```
