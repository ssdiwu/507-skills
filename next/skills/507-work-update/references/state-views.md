# 从同一候选状态生成视图

复杂工作整表可用包内[工作视图脚本](../scripts/work_view.py)，仅依赖Python标准库。输入基线为记录数组，候选为对象：records、viewContract.activeStatuses（按实际数据声明，例如["open"]）、unresolved、priorityAdvice、nextActions、newCandidates。后四项为数组；它们的含义仍由承担者核对。新候选不自动加入现有原记录。

先写一份完整候选，再生成，不手工另写一份表或差异。下面以技能包为当前目录，输入/输出参数换成实际工作位置，不把工作产物写入技能包：

```sh
python3 scripts/work_view.py --baseline baseline.json --candidate outputs/state.json --out-dir outputs/views-v1 --reference-date YYYY-MM-DD
```

当前排序需要时从调用方时间基准传入--reference-date，日期提示只做日粒度比较；带时间、时区或特殊格式保留原值而不猜。提醒已过不代表工作完成，也不自动产生新日期。

生成snapshot.json、views.json、work.md与输入／输出指纹清单；必须使用未存在的输出目录，不能覆盖旧版本。RENDERED只表示视图生成，不授予业务权限或语义接受；错误exit2。脚本只读两个输入、仅写指定输出目录，不访问网络。缺字段显示未提供，显式空日期显示无日期。

受保护字段／身份采用包内[字段对账脚本](../scripts/state_diff.py)和调用方给定的政策，不自行反写政策来消除失败：

```sh
python3 scripts/state_diff.py --baseline baseline.json --candidate outputs/views-v1/snapshot.json --policy caller-policy.json
```

exit0为给定字段范围通过，exit1为拒绝，exit2为输入错误。身份变化、备注语义、来源关联、条件、接受及许可仍分别检查；将具体拒绝回候选修正。政策与字段PASS不替代当前授权真实性。
