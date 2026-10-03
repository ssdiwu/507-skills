# `507-stage` 口播检查脚本

`check_spoken.py` 对已经形成完整初稿的讲稿、课程口播和视频旁白做只读提醒。它检测一口气过长、对比句与转场密度、抽象词、书面元话语、重复开场、句长过齐，以及需要单独确认读法的缩写、版本和百分比。

运行条件：Python 3.10 或更高版本；只使用标准库。

## 运行

```bash
python3 write/507-stage/scripts/check_spoken.py 讲稿.md
python3 write/507-stage/scripts/check_spoken.py --json 讲稿.md
```

使用 `-` 可从标准输入读取。脚本会屏蔽 frontmatter（文档元数据）、代码、链接目标、引用块、Markdown 标题和独立 section / slide ID，避免把制作标记当成口播正文。

## 结果边界

- 所有发现都需要结合现场、页面、讲者备注和旁白职责人工复核，不自动改稿；
- 对比句按密度和聚集位置提醒，真实比较与教学区分可以保留；
- 脚本不能判断案例是否真实、页面或画面是否完成举证，也不能替代朗读和实际计时；
- `0` 表示脚本成功完成，包括存在提醒，不表示口播已经通过朗读或事实检查；`2` 表示文件无法读取或没有可检查的中文口播。

## 测试

```bash
python3 write/507-stage/scripts/test_check_spoken.py
```

测试只使用合成文本，不包含个人 vault、客户内容或未授权作品。
