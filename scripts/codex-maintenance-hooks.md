# 未启用的 Codex 结束一致性检查候选

副本编辑保护已撤除：不再配置 `PreToolUse`，不再读取生成目标映射或拒绝编辑。原有“修改维护源、生成副本、检查一致性”的维护流程保留。

目前只保留 [Stop 示例](../templates/codex-maintenance-hooks.example.json)、[结束检查源码](codex_maintenance_hooks.py)及对应测试，作为尚未采用的候选。未找到交付时实际漏跑包一致性检查的确证，不据模拟测试通过推荐安装。没有创建 `.codex/hooks.json` 或修改个人配置。

## 保留范围及限制

`Stop` 比较包检查输入的路径集合与内容，变化时调用原有 `scripts/package_skills.py check`，不执行 `sync`、`build` 或安装。首次 Stop 只记录基线，因此无法检查本会话第一次结束前的变化；移除前置钩子后不补建替代采集机制，不承诺首轮检查覆盖。候选保持未启用，不继续扩展。

检查超时30秒；失败反馈最后至多3000字符，首次请求继续处理，相同内容不重复。已在结束续办中时只警告。检查期间输入变化不缓存通过。缓存损坏重建基线并警告，不继承通过。

监测 `lib/`、`skills/`、`tests/`、`scripts/package_skills.py`、包清单、适配脚本及处置清单引用的旧入口文件，忽略字节码缓存。状态按仓库、会话、子Agent身份隔离在系统临时目录的用户私有目录，不是交付证据库。

仅支持 `fcntl` 的 macOS／Linux；真实宿主加载、事件字段与结束行为未验证。不拦截文件编辑或 Shell 写入。结构检查不证明技能行为、独立审查或用户接受。没有自动检查时继续按[现有维护说明](../skills/README.md#资源维护与构建)执行。

## 撤除验证

```sh
python3 -B -m unittest discover -s tests -p 'test_codex_maintenance_hooks.py' -v
```

只复验撤除后的剩余检查逻辑、JSON协议和示例不含副本保护；真实检查器漂移及原 `sync` 修复仅在临时仓库中运行。旧独审报告保留为历史，不能作为撤除后的当前通过结果。
