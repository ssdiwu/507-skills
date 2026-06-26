# 接口并行脑暴配方

给 inspection 第③步选定加深候选后，需要对加深后的模块"Design It Twice"（出自 Ousterhout——第一个想法往往不是最优）时，用这个配方**并行 spawn 3 个 pi 子进程**，各自设计**截然不同**的接口，再对比。

## 为什么不装第三方扩展

pi 原生就支持 `pi -p` 非交互递归自调用，零安装、零外部代码审计、完全可控；实时进度 TUI 在这个一次性脑暴场景下无价值。

## 配方（已从官方 `examples/extensions/subagent` 源码验证）

```bash
tmpdir=$(mktemp -d)
# 接口设计者角色定义（内联，避免命令行转义/长度问题）
cat > "$tmpdir/role.md" <<'EOF'
你是接口设计者。严格用架构词汇（module/interface/seam/adapter/leverage/depth）。
产出：1)接口（类型+不变量+错误模式+顺序） 2)调用者用法示例
3)接缝背后藏什么 4)依赖策略与 adapter 5)权衡（哪里杠杆高、哪里薄）。
EOF

designs=(
  "最小接口:目标 1-3 个入口,最大化每个入口的杠杆"
  "最大灵活:支持多种用例和扩展"
  "优化常见调用者:让默认路径极简"
)
for i in "${!designs[@]}"; do
  ( pi --mode text -p --no-session --tools read,grep,find,ls \
       --append-system-prompt "$tmpdir/role.md" \
       "约束【${designs[$i]}】。为这个加深候选设计接口: <这里贴候选描述>。按格式输出。" \
       > "$tmpdir/design-$i.md" 2>"$tmpdir/err-$i.log"
    echo $? > "$tmpdir/code-$i" ) &
done
wait
```

## 收集与对比

读 `$tmpdir/design-*.md`，按这些维度对比：

- **interface simplicity（接口简洁）**：方法数、参数形状、学习成本
- **depth（接口处杠杆）**：小接口是否真的藏住大量行为
- **locality（改动集中点）**：后续修改是否更集中
- **seam placement（接缝放置）**：变化被隔离在什么位置
- **ease of correct use vs misuse（易正确使用 vs 易误用）**：调用者是否容易踩坑

然后给 opinionated 推荐（哪些设计元素可组合就提 hybrid）。507 要的是强判断，不是菜单。**不要按"实现起来省不省事"排序**；优先看接口是否深、稳、难误用。

## 参数说明

- `--mode text`：纯文本输出，脑暴对比足够，主 LLM 直接读。
- `--no-session`：临时，不污染历史。
- `--tools read,grep,find,ls`：**只读白名单**，子进程改不了代码，天然安全。
- 3 个 `&` + `wait`：简单并行，不引入复杂调度。
- **失败不阻塞**：某子进程非 0 退出（看 `$tmpdir/code-$i` 和 err log），就报告"设计 N 失败，用其余对比"，不中断。

## 清理

对比完 `rm -rf "$tmpdir"`。