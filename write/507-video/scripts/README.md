# 507-video 合同回归

`test_contract.py` 检查产品宣传片仍作为 `507-video` 的条件 profile，必需字段、相邻 skill 边界、独立终检与 Studio 渲染门没有从公开合同中漂移。

```bash
python3 -B -m unittest -v write/507-video/scripts/test_contract.py
```

该测试只验证耐久合同结构；真实视频的 Studio 审片、渲染、音画与设备播放仍在具体项目中验收。
