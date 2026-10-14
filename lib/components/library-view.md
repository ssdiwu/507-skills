# 当前库投影与技能名查询

skill-design核对库级当前实现、历史来源及待补能力时采用来源投影。setup、deliver、coordinate接续旧引用时只查询包内索引；查询可在没有作者仓库和兄弟技能的位置运行。仅标准库、只读，输出到标准输出；不安装、发消息、写业务或执行候选。

## 查询包内声明

```sh
python3 scripts/library_view.py --index-file references/shared/skill-entry-index.md --lookup 507-git
```

名字按字面查询；当前声明、旧来源声明、索引外名字分别返回CURRENT_DECLARATION_FOUND、LEGACY_DECLARATION_FOUND、UNKNOWN_NAME。0表示找到了声明，1表示名字不在索引，2表示输入／运行错误；都不是任务或授权通过。重复JSON键／身份、未知消费者、错误路径或索引结构拒绝。

输出保留原处置、保留动作、退出机制及当前候选的职责与入口声明。runtimeAvailability保持NOT_CHECKED，actionAuthority保持UNCHANGED；不检查或写用户安装目录。根据原目标选择必要职责，核对其宿主存在性与完整合同，不把全部候选排成链。旧名与当前名相同时优先当前声明，旧来源另列；未知名不猜替代。

索引是由维护源生成的快照，不是第二份手工映射。更新技能合同或旧处置后重新生成并校核，打包检查拒绝旧索引；只编辑来源，不手改包内副本。完整来源投影仍要求下面明确提供的资料，不隐式寻找作者目录。

## 维护源投影与索引生成

```sh
python3 scripts/library_view.py --source-root <待核库> --packages <入口清单> --catalog <共有资源清单> --dispositions <逐项处置记录>
```

同一命令加--emit-index输出声明索引Markdown。维护者先在新位置生成候选、核对后切换共有源，再生成包内副本；索引不携带依赖自身的包文件指纹。普通查询不需要这些源参数。

入口清单采用本库packages.json的skills/name/source/role/files/shared结构；catalog含methods/components及真实consumers；处置记录含schema、date、legacy、pending、historicalPlanning。每个旧项有id/source/decision/reason/retained/dropped/targets/consumers/verification，decision为retain/merge/drop。保留动作与放弃机制分开，不用旧名字数量判断完整。

输入必须是普通文件，拒绝重复JSON键、重复身份、越界／软链／缺资源、消费者不一致、旧common/code/write实际SKILL清单缺项及保留方法没有当前消费者。成功为SOURCE_PROJECTED、exit0，输入错误为INPUT_ERROR、exit2。它核明确来源的存在和指纹，不替代打包检查、语义审查、宿主发现或业务效果。

当前数据由真实清单生成，安装／发现由各自回执另核。历史85候选和旧试跑保持原版本，不随源码补强冒称已验证新版本。网页只消费组件输出；记录变化后重生成，布局和交互不足修改网页生成组件，再验证并重生成，不能直接编辑生成HTML。
