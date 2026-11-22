# 本地任务交付核对

AI 将已谈妥的交付、等待条件和用户决定写入任务已有的进度记录。先在对话里说明变化。项目续办先读项目指定的 `PROGRESS.md`，私有任务细节按项目约定保存在库外任务目录。任务根取实际可核对文件的共同根目录。

记录中保留一个顶格的 `delivery-json` 代码块，至少登记一项交付。用户修订的原话和适用范围保存在相邻正文，更新前读回当前版本。任务名称、文件位置和验收词取自本次约定。

```delivery-json
{
  "schema": 1,
  "decisions": {"brief_approved": false},
  "items": [
    {"id":"brief","title":"负责人简报","scope":"authorized","checks":[{"type":"nonempty_file","path":"brief.md"}]},
    {"id":"checklist","title":"执行清单","scope":"authorized","when":"brief_approved","checks":[{"type":"text_contains","path":"checklist.md","value":"登记位置"}]}
  ]
}
```

在阶段返回、交付前或用户主动提醒时运行。`--record` 使用相对任务根的路径。

```sh
python3 "$SKILLS_ROOT/lib/components/tools/checks/delivery_check.py" --task-root "$TASK_DIR" --record PROGRESS.md
```

改动受记录保护的交付文件后，同步重算并更新引用的指纹或回执清单，再逐项校验；未完成同步和校验前，不把“其余文件未变”当作状态已更新。模拟确认只解除对应交付的等待，不改变实机或现场验收状态；这类项保持延期并写明待核内容。对话回报与唯一记录及实际文件状态一致。

未发现 `missing` 项时退出 0，存在 `missing` 项时退出 1，输入或读取错误退出 2。按每项 `status` 说明核对结果。`satisfied` 表示登记的证据已满足，`waiting`、`deferred`、`needs_decision` 和 `cancelled` 分别表示等待、延期、待决定和取消。文件存在、文字命中或标题匹配的回执只覆盖对应条件。用户的授权、原话与决定状态是否一致，仍需执行者核对。
