# guizang 可逆备份与恢复演练

本日志记录把旧网页 PPT skill 从活动技能发现路径移入非发现备份、并演练恢复的过程。实际部署时把下列占位替换为目标机器的真实路径。

- `SKILLS_DIR`：技能发现根目录（由运行环境提供的占位变量）
- `BACKUP_DIR`：不在技能发现路径中的备份根目录（由运行环境提供的占位变量）

## 移入备份命令（可重复）

```sh
mv "$SKILLS_DIR/guizang-ppt-skill" "$BACKUP_DIR/guizang-ppt-skill"
```

## 恢复命令（可重复）

```sh
mv "$BACKUP_DIR/guizang-ppt-skill" "$SKILLS_DIR/guizang-ppt-skill"
```

## 发现列表扫描命令

```sh
find -L "$SKILLS_DIR" -name SKILL.md -exec dirname {} \; \
  | xargs -n1 basename | sort -u | grep -E 'guizang|507-ppt'
```

## 演练结果（本轮执行）

- 备份态：发现列表含 `507-ppt`，不含 `guizang-ppt-skill`。
- 恢复后：发现列表同时含 `507-ppt` 与 `guizang-ppt-skill`。
- 最终态（恢复演练后再次移入备份）：发现列表含 `507-ppt`，不含 `guizang-ppt-skill`。

恢复可逆，未硬删除。
