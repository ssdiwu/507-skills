# 当前技能库与旧能力去向投影

skill-design需要核对库级当前实现、历史来源及待补能力时采用。不用于普通业务任务，不成为总控或技能自动路由。仅标准库，只读显式source-root和三个JSON输入，JSON输出到标准输出；不安装、发消息或写业务。

```sh
python3 scripts/library_view.py --source-root <待核库> --packages <入口清单> --catalog <共有资源清单> --dispositions <逐项处置记录>
```

入口清单采用本库packages.json的skills/name/source/role/files/shared结构；catalog含methods/components及真实consumers；处置记录含schema、date、legacy、pending、historicalPlanning。每个旧项有id/source/decision/reason/retained/dropped/targets/consumers/verification，decision为retain/merge/drop。保留动作与放弃机制分开，不用旧名字数量判断完整。

输入必须是普通文件，拒绝重复JSON键、重复身份、越界／软链／缺资源、消费者不一致、旧common/code/write实际SKILL清单缺项及保留方法没有当前消费者。成功为SOURCE_PROJECTED、exit0，输入错误为INPUT_ERROR、exit2。它核明确来源的存在和指纹，不替代打包检查、语义审查、宿主发现或业务效果。

当前数据由真实清单生成，安装／发现由各自回执另核。历史85候选和旧试跑保持原版本，不随源码补强冒称已验证新版本。网页只消费组件输出；记录变化后重生成，布局和交互不足修改网页生成组件，再验证并重生成，不能直接编辑生成HTML。
