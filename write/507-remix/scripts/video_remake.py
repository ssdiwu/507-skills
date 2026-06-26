#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from collections import Counter
from pathlib import Path


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "video-remake"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_title(meta_path: Path) -> str:
    text = load_text(meta_path)
    match = re.search(r"`title`：(.+)", text)
    return match.group(1).strip() if match else meta_path.parent.name


def markdown_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def extract_bullets(section: str) -> list[str]:
    bullets = []
    for line in section.splitlines():
        line = line.strip()
        if line.startswith("- "):
            bullets.append(line[2:].strip())
    return bullets


def collect_source_package(pull_dir: Path) -> dict:
    breakdown_json_path = pull_dir / "breakdown.json"
    breakdown_md_path = pull_dir / "breakdown.md"
    meta_path = pull_dir / "meta.md"
    for path in [breakdown_json_path, breakdown_md_path, meta_path]:
        if not path.exists():
            raise SystemExit(f"缺少必要拉片包文件：{path}")

    breakdown = load_json(breakdown_json_path)
    breakdown_md = load_text(breakdown_md_path)
    title = load_title(meta_path)
    patterns: list[str] = []
    techniques: list[str] = []
    for segment in breakdown.get("segments", []):
        patterns.extend(segment.get("patterns", []))
        techniques.extend(segment.get("techniques", []))

    return {
        "path": str(pull_dir),
        "title": title,
        "videoType": breakdown.get("videoType", "mixed"),
        "oneLineThesis": breakdown.get("oneLineThesis", ""),
        "structure": breakdown.get("structure", []),
        "patterns": patterns,
        "techniques": techniques,
        "visualLanguage": breakdown.get("visualLanguage", {}),
        "segments": breakdown.get("segments", []),
        "humanSummary": markdown_section(breakdown_md, "一句话主旨"),
        "humanBorrowNotes": extract_bullets(markdown_section(breakdown_md, "可借鉴点")),
        "humanDoNotBorrowNotes": extract_bullets(markdown_section(breakdown_md, "不建议借鉴点")),
    }


def synthesize_structure(sources: list[dict]) -> list[dict]:
    order: list[str] = []
    descriptions: dict[str, str] = {}
    for source in sources:
        for item in source["structure"]:
            label = item.get("label")
            if not label:
                continue
            if label not in order:
                order.append(label)
            descriptions.setdefault(label, item.get("summary", ""))
    return [{"label": label, "summary": descriptions.get(label, "")} for label in order]


def beat_goal(label: str, theme: str) -> tuple[str, str]:
    mapping = {
        "hook": (f"用一个高记忆点开场，把{theme}的核心结果先抛出来", "开场先给结果或反差，快速抓住注意力"),
        "pain-points": (f"把{theme}相关的典型痛点拆清楚", "用可数项或连续案例建立问题压力"),
        "reframing": (f"重述问题，给出{theme}的正确观察角度", "从误解切到真正的矛盾或方法入口"),
        "walkthrough": (f"按步骤或模块走查{theme}的关键做法", "讲到哪个概念，就给哪个对应画面"),
        "methodology": (f"把{theme}从技巧上升到可复用方法", "解释为什么这套方式有效，适用边界在哪里"),
        "cta": (f"给出关于{theme}的明确下一步行动", "用一句可执行话术或互动收束全片"),
    }
    return mapping.get(label, (f"推进 {theme} 的下一个信息节拍", "保持结构连续推进"))


def synthesize_storyboard(structure: list[dict], theme: str, style: str, sources: list[dict], locked_patterns: list[str], exclude_patterns: list[str]) -> list[dict]:
    storyboard = []
    reusable = ", ".join(locked_patterns[:3]) or "稳定字幕与镜头节奏"
    for item in structure:
        goal, notes = beat_goal(item["label"], theme)
        ref = pick_reference_segment(item["label"], sources)
        if ref is None:
            visual = (
                f"未在输入拉片包中找到与 `{item['label']}` 节拍直接对位的 segment。"
                f"建议在执行时按主题“{theme}”自行设计具体画面与字幕节奏，"
                f"总风格为「{style}」，可补充跨来源共有模式：{reusable}。"
            )
            beat_techniques: list[str] = []
            source_ref = "无来源参考"
        else:
            seg = ref["segment"]
            seg_techniques = [t for t in seg.get("techniques", []) if t not in exclude_patterns]
            seg_visual = re.sub(r"\s+", " ", seg.get("visualChange", "")).strip()
            seg_transcript = re.sub(r"\s+", " ", seg.get("transcript", "")).strip()
            seg_start = seg.get("start", "?")
            seg_end = seg.get("end", "?")
            technique_text = "、".join(f"`{t}`" for t in seg_techniques) or "该段未补充 techniques 标签"
            visual = (
                f"参考源《{ref['source']}》第 {seg_start}-{seg_end} 段的视觉做法：{seg_visual}。"
                f"原文采样：“{seg_transcript[:80]}”。"
                f"该段手法标签：{technique_text}。"
                f"本地总风格「{style}」下请按主题“{theme}”重写画面与字幕；可补充跨来源共有模式：{reusable}。"
            )
            beat_techniques = seg_techniques
            source_ref = f"《{ref['source']}》{seg_start}-{seg_end}"
        storyboard.append({
            "beat": item["label"],
            "goal": goal,
            "visual": visual,
            "notes": notes,
            "sourceRef": source_ref,
            "referenceTechniques": beat_techniques,
        })
    return storyboard


BEAT_TO_PATTERNS = {
    "hook": ["hook-result-first", "hook-problem-first"],
    "pain-points": ["hook-problem-first", "problem-solution-demo"],
    "reframing": ["problem-solution-demo", "hook-problem-first"],
    "walkthrough": ["listicle-step-flow", "problem-solution-demo"],
    "methodology": ["problem-solution-demo"],
    "cta": ["cta-comment-close"],
}


def pick_reference_segment(beat_label: str, sources: list[dict]) -> dict | None:
    """从来源里挑出与当前 beat 最对位的一个 segment。"""
    patterns = BEAT_TO_PATTERNS.get(beat_label, [])
    for source in sources:
        for segment in source.get("segments", []):
            if any(p in segment.get("patterns", []) for p in patterns):
                return {"source": source["title"], "segment": segment}
    return None


def choose_borrowed_patterns(sources: list[dict], include_patterns: list[str], exclude_patterns: list[str]) -> tuple[list[str], list[str]]:
    pattern_counter = Counter()
    technique_presence = Counter()
    for source in sources:
        pattern_counter.update(source["patterns"])
        technique_presence.update(set(source["techniques"]))

    # include 作为白名单：限制自动收集范围为 include_patterns 交集
    include_set = set(include_patterns)
    auto_scope = pattern_counter.keys() if not include_set else (set(pattern_counter.keys()) & include_set)
    borrowed = [pattern for pattern, _count in pattern_counter.most_common() if pattern in auto_scope and pattern not in exclude_patterns]
    for pattern in include_patterns:
        if pattern not in borrowed:
            borrowed.append(pattern)

    locked = [technique for technique, count in technique_presence.most_common() if count == len(sources)]
    return borrowed, locked


def score_note_for_pattern(pattern: str, note: str) -> int:
    keywords = {
        "hook-result-first": ["结果先行", "开场", "背书", "模板"],
        "hook-problem-first": ["痛点", "代入", "混乱", "问题"],
        "problem-solution-demo": ["痛点", "问题重述", "解决", "起手式", "下一句"],
        "listicle-step-flow": ["文件清单", "讲一个文件", "步骤", "三文件"],
        "cta-comment-close": ["结尾", "起手式", "评论"],
    }
    return sum(1 for keyword in keywords.get(pattern, []) if keyword in note)


def reason_for_pattern(pattern: str, sources: list[dict], theme: str) -> str:
    source_titles = [source["title"] for source in sources if pattern in source["patterns"]]
    notes = []
    for source in sources:
        if pattern in source["patterns"]:
            notes.extend(source["humanBorrowNotes"])
    notes = sorted(notes, key=lambda note: score_note_for_pattern(pattern, note), reverse=True)
    if notes and score_note_for_pattern(pattern, notes[0]) > 0:
        note = notes[0]
        return f"来自 {'、'.join(source_titles)}；人读拉片指出“{note}”，适合迁移到“{theme}”的同类信息节拍。"
    if source_titles:
        return f"来自 {'《'.join(source_titles) + '》'};本来源的「可借鉴点」未覆盖此模式的细化观察，建议执行时自行设计或参考标签词表。"
    return f"仅显式 include;本来源未提供对应人读观察，建议执行时参考标签词表自行设计。"


def detect_conflicts(sources: list[dict], borrowed: list[str]) -> list[str]:
    conflicts = []
    video_types = {source["videoType"] for source in sources}
    if len(video_types) > 1:
        conflicts.append(f"输入来源的视频类型不一致：{', '.join(sorted(video_types))}。重组时需要明确谁负责结构，谁只负责局部手法。")
    if "hook-result-first" in borrowed and "hook-problem-first" in borrowed:
        conflicts.append("开场同时出现 result-first 与 problem-first，两者不宜并用，需要人为选一个开场主策略。")
    if any("ui-overlay-card" in source["techniques"] for source in sources) and any("ui-overlay-card" not in source["techniques"] for source in sources):
        conflicts.append("并非所有来源都依赖 UI 叠加；如果混用，需要明确 UI 是主表达还是辅助表达。")
    return conflicts


def write_brief(path: Path, project_name: str, theme: str, platform: str, duration: str, style: str):
    path.write_text(
        f"# Brief\n\n- 项目名：{project_name}\n- 主题：{theme}\n- 平台：{platform}\n- 时长：{duration}\n- 风格：{style}\n\n目标：基于多个拉片包的共同方法，重组出一个新的原创视频方向，而不是直接复刻某一条样片。\n",
        encoding="utf-8",
    )


def write_borrow_map(path: Path, sources: list[dict], borrowed: list[str], locked: list[str], exclude_patterns: list[str], conflicts: list[str], theme: str):
    lines = ["# Borrow Map", "", "## 来源", ""]
    for source in sources:
        lines.append(f"- `{source['title']}`：`{source['path']}`")
        if source["humanSummary"]:
            lines.append(f"  - 人读摘要：{source['humanSummary'].splitlines()[0]}")
    lines.extend(["", "## 借什么，以及为什么借", ""])
    if borrowed:
        for pattern in borrowed:
            lines.append(f"- `{pattern}`：{reason_for_pattern(pattern, sources, theme)}")
    else:
        lines.append("- （无自动借用项；需要用户显式指定或补充更完整的拉片包）")
    lines.extend(["", "## 怎么借", ""])
    lines.append("- 只借信息组织、镜头/字幕/UI 的表达手法，不借原视频的具体文案、案例、成本数字或品牌语境。")
    lines.append("- 如果不同来源类型冲突，优先选择一个来源负责主结构，其余来源只作为局部手法参考。")
    lines.extend(["", "## 风格锁定项", ""])
    if locked:
        for item in locked:
            lines.append(f"- `{item}`")
    else:
        lines.append("- （无跨所有来源共同出现的稳定风格锁定项）")
    lines.extend(["", "## 明确不借", ""])
    if exclude_patterns:
        for pattern in exclude_patterns:
            lines.append(f"- `{pattern}`：用户显式排除，后续结构与分镜不得依赖该模式。")
    do_not_borrow_notes = [note for source in sources for note in source["humanDoNotBorrowNotes"]]
    if do_not_borrow_notes:
        for note in do_not_borrow_notes:
            lines.append(f"- {note}")
    if not exclude_patterns and not do_not_borrow_notes:
        lines.append("- （无显式排除项）")
    lines.extend(["", "## 冲突与混用提醒", ""])
    if conflicts:
        for item in conflicts:
            lines.append(f"- {item}")
    else:
        lines.append("- 当前输入未发现明显冲突项。")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_structure(path: Path, structure: list[dict]):
    lines = ["# Structure", "", "## 节拍顺序", ""]
    for index, item in enumerate(structure, start=1):
        lines.append(f"{index}. `{item['label']}`：{item['summary']}")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_storyboard(path: Path, storyboard: list[dict]):
    lines = ["# Storyboard", ""]
    for index, beat in enumerate(storyboard, start=1):
        lines.extend([
            f"## Beat {index}｜{beat['beat']}",
            f"- 目标：{beat['goal']}",
            f"- 画面：{beat['visual']}",
            f"- 备注：{beat['notes']}",
            "",
        ])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_style_lock(path: Path, style: str, locked: list[str]):
    lines = ["# Style Lock", "", f"- 总风格：{style}", "- 以下模式在后续执行层应优先保持：", ""]
    if locked:
        for item in locked:
            lines.append(f"- `{item}`")
    else:
        lines.append("- （无跨所有来源共同出现的稳定锁定项）")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_project_readme(path: Path, project_name: str, theme: str, platform: str, duration: str, style: str, sources: list[dict], borrowed: list[str], locked: list[str]):
    source_lines = [f"- `{source['title']}`：`{source['path']}`" for source in sources]
    borrowed_lines = [f"- `{p}`" for p in borrowed] or ["- （无）"]
    locked_lines = [f"- `{t}`" for t in locked] or ["- （无）"]
    content = f"""# Remake 创作包说明

本目录是 `507-video-remake` 的一次重组创作包产出。

## 创作目标

- 项目名：`{project_name}`
- 主题：{theme}
- 平台：{platform}
- 时长：{duration}
- 风格：{style}

## 来源拉片包

{chr(10).join(source_lines)}

## 推荐阅读顺序

1. **`brief.md`**：目标四要素 + 一句话总目标。
2. **`borrow-map.md`**：详细说明借什么、为什么借、怎么借、明确不借、冲突提醒。**这是人读版的精华。**
3. **`structure.md`**：结构节拍顺序（hook / pain-points / reframing / walkthrough / methodology / cta）。
4. **`storyboard.md`**：每个节拍的目标、画面参考、备注。
5. **`style-lock.md`**：后续执行层须优先保持的视听语言与模式。
6. **`prompt-pack.json`**：工具无关的结构化创作蓝图，供后续执行器消费（不含 `sources` 字段、不绑定模型）。

## 借鉴项与锁定项

**借用项**（来源拉片包里提取的结构/叙事模式）：
{chr(10).join(borrowed_lines)}

**锁定项**（跨所有来源共同出现、后续执行须优先保持的视听模式）：
{chr(10).join(locked_lines)}

## 标签术语速查

本创作包中的英文标签对应中文含义（完整版见 `507-video-pull/references/tag-vocabulary.md`）：

**叙事与结构（借什么）**
- `hook-result-first`：结果先行开场。
- `hook-problem-first`：痛点先行开场。
- `problem-solution-demo`：问题—方案—演示推进。
- `listicle-step-flow`：列表/步骤顺序推进。
- `cta-comment-close`：评论号召收束。

**镜头 / 剪辑 / 字幕 / 界面（锁定什么）**
- `fixed-medium-close`：固定机位中近景。
- `single-background`：单一不变背景。
- `single-speaker-center`：单人主体稳定居中。
- `hard-cut`：硬切转场。
- `beat-paced-reveal`：信息节拍逐步揭示。
- `overlay-on-mention`：讲到概念叠画面。
- `return-to-speaker`：回到主讲人镜头。
- `subtitle-bottom-bar`：底部字幕条。
- `subtitle-green-keyword`：字幕关键词绿色高亮。
- `keyword-memory-anchor`：关键词记忆锚点。
- `ui-overlay-card`：画面叠加 UI 卡片。
- `topic-label-top-left`：左上角主题/系列标签。

## 下一步

- 需要调整创作方向：重跑 `video_remake.py run` 并传新的主题/平台/时长/风格或 include/exclude 参数。
- 需要重新合并不同拉片包：多 `--pull-dir` 重新运行。
- 需要进后续执行层（如生图、生视频）：把 `prompt-pack.json` 喂给对应工具，注意其是工具无关的。
"""
    path.write_text(content, encoding="utf-8")


def run_pipeline(args):
    source_dirs = [Path(item).expanduser().resolve() for item in args.pull_dir]
    sources = [collect_source_package(path) for path in source_dirs]

    output_root = Path(args.output_dir).expanduser().resolve()
    ensure_dir(output_root)
    project_dir = output_root / slugify(args.project_name)
    preserved_verification = None
    verification_path = project_dir / "verification.md"
    if project_dir.exists() and not args.force:
        raise SystemExit(f"输出目录已存在：{project_dir}\n如需覆盖，请显式传 --force")
    if project_dir.exists() and args.force:
        if verification_path.exists():
            preserved_verification = verification_path.read_text(encoding="utf-8", errors="ignore")
        shutil.rmtree(project_dir)
    ensure_dir(project_dir)
    if preserved_verification is not None:
        verification_path.write_text(preserved_verification, encoding="utf-8")

    borrowed, locked = choose_borrowed_patterns(sources, args.include_pattern or [], args.exclude_pattern or [])
    conflicts = detect_conflicts(sources, borrowed)
    structure = synthesize_structure(sources)
    storyboard = synthesize_storyboard(structure, args.theme, args.style, sources, locked, args.exclude_pattern or [])

    write_brief(project_dir / "brief.md", args.project_name, args.theme, args.platform, args.duration, args.style)
    write_borrow_map(project_dir / "borrow-map.md", sources, borrowed, locked, args.exclude_pattern or [], conflicts, args.theme)
    write_structure(project_dir / "structure.md", structure)
    write_storyboard(project_dir / "storyboard.md", storyboard)
    write_style_lock(project_dir / "style-lock.md", args.style, locked)
    write_project_readme(project_dir / "README.md", args.project_name, args.theme, args.platform, args.duration, args.style, sources, borrowed, locked)

    prompt_pack = {
        "projectName": args.project_name,
        "target": {
            "theme": args.theme,
            "platform": args.platform,
            "duration": args.duration,
            "style": args.style,
        },
        "borrowedPatterns": borrowed,
        "lockedPatterns": locked,
        "structure": structure,
        "storyboard": storyboard,
    }
    (project_dir / "prompt-pack.json").write_text(json.dumps(prompt_pack, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"projectDir": str(project_dir), "sources": [str(path) for path in source_dirs]}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="507 Video Remake 创作包生成器")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="读取多个拉片包并生成创作包")
    run_parser.add_argument("--pull-dir", required=True, action="append", help="一个 `507-video-pull` 工作区")
    run_parser.add_argument("--project-name", required=True)
    run_parser.add_argument("--theme", required=True)
    run_parser.add_argument("--platform", required=True)
    run_parser.add_argument("--duration", required=True)
    run_parser.add_argument("--style", required=True)
    run_parser.add_argument("--include-pattern", action="append")
    run_parser.add_argument("--exclude-pattern", action="append")
    run_parser.add_argument("--output-dir", required=True, help="输出根目录，应指向作品主轴 works/{选题}/视频/")
    run_parser.add_argument("--force", action="store_true")

    args = parser.parse_args()
    if args.command == "run":
        run_pipeline(args)
        return
    parser.print_help()


if __name__ == "__main__":
    main()
