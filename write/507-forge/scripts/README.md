# `507-forge` 书面检查脚本

`check_prose.py` 对已经完成初稿和人工逐遍审计的中文 Markdown / 文本稿做只读提醒。它检测重复对比、名词化、强表达信号、排比、连词与标点密度、句长变化、重复开场、短段和多套借喻，不修改文件。

运行条件：Python 3.10 或更高版本；只使用标准库。

## 运行

```bash
python3 write/507-forge/scripts/check_prose.py 稿件.md
python3 write/507-forge/scripts/check_prose.py --json 稿件.md
```

使用 `-` 可从标准输入读取。脚本会屏蔽 frontmatter（文档元数据）、代码、链接目标、HTML、引用块和 Markdown 标题，避免把来源原文或机器字段当成作者正文。

## 结果边界

- 所有表达发现都是 `review（人工复核）` 或 `metric（统计提醒）`，不会仅因命中返回失败；
- 对比句、冒号和破折号按密度提醒，单次出现不构成问题；
- 脚本不能判断材料是否充足、事实是否成立、作者说话位置是否真实，也不能代替完整通读；
- `0` 表示脚本成功完成，包括存在提醒；`2` 表示文件无法读取或没有可检查的中文正文。

## 测试

```bash
python3 write/507-forge/scripts/test_check_prose.py
```

测试只使用合成文本，不包含个人 vault、客户内容或未授权作品。
