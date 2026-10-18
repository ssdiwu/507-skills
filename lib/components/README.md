# 执行脚本与工具说明

本目录同时包含可运行脚本和配套说明，分开列示。当前共有执行脚本为 **10 个**；准确消费者见[catalog](../catalog.json)，随包路径见[packages](../../next/packages.json)。

## 执行脚本

| 脚本 | 确定性工作 | 当前消费者（省略 507- 前缀） |
| --- | --- | --- |
| [check_prose.py](check_prose.py) | 提示书面表达问题；不自动改稿 | compose、adapt |
| [check_spoken.py](check_spoken.py) | 提示讲稿和口播表达问题；不裁决作者接受 | compose、adapt |
| [check_run.py](check_run.py) | 运行指定检查命令并记录输出、退出或超时 | implement、fix、review |
| [render_artifact.py](render_artifact.py) | 生成离线 HTML 图卡、幻灯片阅读页或网站 | compose、adapt |
| [artifact_receipt.py](artifact_receipt.py) | 记录实际文件身份及支持的结构信息 | create、compose、adapt |
| [state_diff.py](state_diff.py) | 按给定政策比较两份状态及字段变化 | work-update |
| [work_view.py](work_view.py) | 从明确工作记录生成快照与文字视图 | work-update |
| [task_view.py](task_view.py) | 从已有记录生成任务、依赖与结果网页 | coordinate、work-update |
| [product_map.py](product_map.py) | 从交互点记录生成可探索的产品地图 | product-map |
| [library_view.py](library_view.py) | 展示明确技能清单，生成或查询名称索引 | skill-design、setup、deliver、coordinate |

## 工具说明

| 文档 | 说明对象 |
| --- | --- |
| [text-checks.md](text-checks.md) | 书面与口播检查器的用法和限制 |
| [task-view.md](task-view.md) | 从既有记录生成任务网页的输入、更新和失败处理 |
| [product-map.md](product-map.md) | 交互点地图的输入模型与输出 |
| [library-view.md](library-view.md) | 库清单展示与名称索引查询 |
| [artifact-receipt.md](artifact-receipt.md) | 文件身份与结构回执 |
| [media-adapters.md](media-adapters.md) | 复用外部制作工具前实际读齐说明，核依赖及目标文件 |

这些 Markdown 说明不构成额外脚本。`render_artifact.py` 的合同在[呈现方法](../methods/artifact-rendering.md)；生成 HTML 不表示已生成 PNG、PPTX 或视频。脚本的确定性结果与权限、语义、视觉质量、实际业务完成分别判断。

## 状态比较与现有用法

`state_diff.py`是`artifact.check`的一个确定性适配：按选定政策比较两份记录快照，报告实际字段变化、身份变化与拒绝原因。仅用Python标准库，只读三个输入文件，JSON写到标准输出，不访问网络、不写业务、不安装技能，也不授予平台权限。它可独立使用；work-update通过清单携带普通生成副本。

```sh
python3 state_diff.py --baseline baseline.json --candidate candidate.json --policy policy.json
```

基线和候选可使用记录数组，或基线唯一包装`{"snapshot":[...]}`、候选唯一包装`{"afterSnapshot":[...]}`。原始模型输出含额外字段时，调用者先提取指定数组并保留原输出版本；不能把多个候选包装混在一起让组件猜。每条记录须有唯一非空字符串id。

政策示例：

```json
{"protectedFields":["deadline"],"preserveIdentities":true,"allowedChanges":[]}
```

受保护字段缺失或未经政策允许的改变会被拒绝；其他变化仍报告。`allowedChanges`只接受精确的`id/field/before/after/basis`记录，旧新值须与实际变化一致，依据非空；重复、冲突、多余或不匹配记录报输入错误。`preserveIdentities`默认true，新增/删除身份拒绝；false时只报告这类变化。

退出码0仅代表政策范围通过，1代表发现违规，2代表输入或运行错误。结果绑定基线、候选和政策文件SHA-256；缺参数、错误JSON/UTF-8、重复键/ID、歧义包装等错误返回JSON，不输出堆栈。`--help`显示命令帮助。

政策及允许记录的语义由原指令或独立审读核定。组件无法判断自然语言是否明确修订、备注是否保留含义、来源是否有关联；不能把它的PASS写成意图确认、整体产物接受或业务写入成功。

```sh
python3 -m unittest discover -s tests -v
```

测试覆盖拒绝无允许依据的日期变化、允许精确对应的变化、字段缺失、身份/JSON/政策错误、非保护字段报告及缺命令参数。

## 单状态工作视图

work_view.py从基线记录数组与一个候选对象（records、显式viewContract.activeStatuses及按需的unresolved/priorityAdvice/nextActions/newCandidates数组）生成snapshot.json、views.json、work.md和输入/输出SHA-256清单。只用Python标准库；只读输入、仅写不存在的指定输出目录，不访问网络或业务平台。

```sh
python3 work_view.py --baseline baseline.json --candidate state.json --out-dir views-v1 --reference-date 2026-10-12
```

reference-date由调用方给定，可选，仅比较支持的YYYY-MM-DD日历日期；缺日期与显式null分别保留，带时刻/时区的值保留原文，不猜测新日期或截止。提醒已过不表示完成。activeStatuses决定视图划分，退出活跃视图不表示业务完成，新增候选不自动成为原事项。

输出RENDERED只表示派生成功，exit2表示输入/运行错误；拒绝重复键、重复ID、缺身份/标题/状态、无明确活跃状态或已有输出目录。Markdown单元格转义；JSON输出保留数据原值。字段对账继续独立执行，权限/正文语义由当前承担者核对。

两个组件的唯一源为本目录，work-update/scripts副本通过next的生成工具维护。脚本不创建任务系统、日志技能或路由器。


## 创作与工程组件

- check_run.py接受--argv-json、--cwd、--log-dir、--timeout及可重复--source，记录一个真实检查命令、退出/超时、日志指纹及源前后。目录已存在拒绝覆盖。退出0/1/2分别是命令成功、命令失败、准备/运行输入错误；选择断言、业务判定与授权仍由消费者承担。
- render_artifact.py接受--input与新的--out-dir，按artifact-rendering合同生成cards/deck/site离线HTML、原内容与指纹清单。来源ID须可解析，文本转义；现有输出拒绝覆盖。仅证明HTML生成，实际阅读需看最终页面，不生成PNG/PPTX/视频。
- check_prose.py、check_spoken.py从已发布forge原样提取为唯一源，接受文本路径与--json；只读提示，不自动重写或裁决接受。原算法与断言保留，旧目录继续作为来源/回退，尚未退出旧技能。

所有脚本仅标准库；共有说明text-checks.md和设计提示按清单携带普通副本。现有字段组件的语义许可限制保留；本轮没有通过它判授权。脚本行为检查位于tests，运行python3 -m unittest discover -s lib/components/tests -v。

## 从既有过程记录生成任务网页

[task_view.py](task_view.py)按[组件合同](task-view.md)读取明确JSON数组路径或Markdown唯一标题下的任务表，以字段映射生成任务、依赖、报告状态与验收记录分开的离线网页。当前消费者是coordinate/work-update；无需网页时不运行。

原记录修改后用同一组件与输出根重生成；历史版本保留，当前入口更新，坏输入或手改生成文件拒绝。渲染器能力变化形成新身份，不能直接编辑HTML补状态或布局。只读投影与版本登记不是新的工作日志、任务数据库或授权来源，也不会自动派工、联网或发布。

## 当前库投影与实际成品回执

[library_view](library-view.md)按显式维护清单输出当前实现、旧30处置与待补；[artifact_receipt](artifact-receipt.md)记录实际文件身份与所列结构，媒体制作沿[工具适配](media-adapters.md)。前者不判业务效果，后者不判渲染、语义或接受。精确消费者以catalog与packages为准。

library_view另提供按名查询：`--index-file`配合`--lookup`只读一个生成声明索引，返回当前、旧来源或未知，退出分别为0／1，输入错误为2。查询可在单包外移后运行，不访问作者清单、兄弟技能、安装目录或网络。`--emit-index`是维护者的源投影模式，需要显式的四项源输入；打包检查核索引与现行声明一致，不能用旧快照冒充当前入口。两个模式与权限界限见[合同](library-view.md)。

## 从同一交互点记录生成地图

[product_map.py](product_map.py)按[合同](product-map.md)验证交互点、关系、路径与三维证据，从一份JSON生成包含树、筛选、详情、关系和路径的离线网页。源码声明与运行观察分开，未知及相反条件并存；结构与生成成功不证明语义或产品接受。更新同一记录后用新输出目录重生成，旧网页保持不变；现有目录拒绝覆盖。
