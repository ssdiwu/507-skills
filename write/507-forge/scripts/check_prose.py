#!/usr/bin/env python3
"""Advisory checks for Chinese prose. Reports shapes; never rewrites text."""

from __future__ import annotations

import argparse
import collections
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


PIVOT_PATTERNS = (
    re.compile(r"(?:并)?不是[^。！？\n]{1,90}(?:而是|，(?:更|才)?是)"),
    re.compile(r"并非[^。！？\n]{1,90}而是"),
    re.compile(r"不在于[^。！？\n]{1,90}而在于"),
    re.compile(r"与其说[^。！？\n]{1,90}(?:不如说|倒不如|毋宁)"),
    re.compile(r"(?:你|人们|大家|我(?:们)?)以为[^。！？\n]{1,80}(?:其实|后来才|才发现|才知道)"),
    re.compile(r"(?:表面(?:上)?|看似)[^。！？\n]{1,80}(?:实际(?:上)?|其实|实则)"),
    re.compile(r"[^，。！？\n]{1,18}不重要，(?:真正)?(?:重要|要紧)的是"),
)

NOMINALIZATION_PATTERNS = (
    re.compile(r"进行(?:了|一次|一场|着)?[^。，！？\n]{0,12}(?:调整|优化|升级|分析|讨论|沟通|梳理|复盘|迭代|探索|尝试|思考|规划)"),
    re.compile(r"实现了?[^。，！？\n]{0,16}(?:提升|增长|突破|转变|跃升|落地)"),
    re.compile(r"完成了?对[^。，！？\n]{0,18}的"),
    re.compile(r"起到了?[^。，！？\n]{0,14}作用"),
    re.compile(r"具有[^。，！？\n]{0,12}(?:意义|价值)"),
)

STRONG_TERMS = (
    "说白了",
    "说穿了",
    "先说结论",
    "值得注意的是",
    "需要指出的是",
    "从某种意义上说",
    "底层逻辑",
    "顶层设计",
    "降本增效",
    "内容矩阵",
    "全链路",
    "组合拳",
)

LYRIC_WORDS = (
    "安放",
    "抵达",
    "微光",
    "褶皱",
    "丰盈",
    "滚烫",
    "轻盈",
    "赤裸",
    "剥开",
)

CONJUNCTIONS = (
    "因为",
    "所以",
    "但是",
    "然而",
    "同时",
    "此外",
    "而且",
    "并且",
    "因此",
    "不仅",
)

REPEATED_OPENERS = (
    "其实",
    "不过",
    "当然",
    "所以",
    "但是",
    "后来",
    "当时",
    "很多人",
    "问题是",
    "更重要的是",
    "说到这里",
)

METAPHOR_FIELDS = {
    "温度": ("降温", "升温", "冷却", "余温"),
    "生死战争": ("杀死", "死因", "枪响", "开火", "战场", "弹药"),
    "建筑灾害": ("坍塌", "崩塌", "地基", "砖头", "支柱", "废墟"),
    "仓储": ("仓库", "库房", "入库", "取货", "库存"),
    "道路竞赛": ("赛道", "跑道", "岔路", "十字路口", "终点线", "门票"),
    "机器器官": ("齿轮", "引擎", "发动机", "血管", "骨架", "肌肉"),
    "海洋航行": ("蓝海", "浪潮", "潮水", "航船", "灯塔", "彼岸"),
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None


@dataclass(frozen=True)
class Paragraph:
    position: int
    text: str
    han: int
    sentences: int


@dataclass
class Report:
    metrics: dict[str, int | float]
    findings: list[Finding]


def han_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def _mask_match(match: re.Match[str]) -> str:
    return "".join("\n" if char == "\n" else " " for char in match.group())


def mask_non_prose(text: str) -> str:
    """Mask metadata and quoted/non-prose Markdown while preserving positions."""

    patterns = (
        re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", re.DOTALL),
        re.compile(r"```.*?```", re.DOTALL),
        re.compile(r"`[^`\n]*`"),
        re.compile(r"\]\([^\n)]*\)"),
        re.compile(r"https?://[^\s)>]+"),
        re.compile(r"<[^>\n]+>"),
        re.compile(r"^[ \t]*>.*$", re.MULTILINE),
        re.compile(r"^[ \t]*#{1,6}[ \t]+.*$", re.MULTILINE),
    )
    masked = text
    for pattern in patterns:
        masked = pattern.sub(_mask_match, masked)
    return masked


def _unique_matches(text: str, patterns: Iterable[re.Pattern[str]]) -> list[re.Match[str]]:
    matches: list[re.Match[str]] = []
    occupied: list[tuple[int, int]] = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            start, end = match.span()
            if any(start < old_end and end > old_start for old_start, old_end in occupied):
                continue
            matches.append(match)
            occupied.append((start, end))
    return sorted(matches, key=lambda match: match.start())


def _term_positions(text: str, terms: Iterable[str]) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    occupied: list[tuple[int, int]] = []
    for term in sorted(terms, key=len, reverse=True):
        for match in re.finditer(re.escape(term), text):
            start, end = match.span()
            if any(start < old_end and end > old_start for old_start, old_end in occupied):
                continue
            found.append((start, term))
            occupied.append((start, end))
    return sorted(found)


def _sentence_matches(text: str) -> list[re.Match[str]]:
    return [
        match
        for match in re.finditer(r"[^。！？!?\n]+(?:[。！？!?]|$)", text)
        if han_count(match.group()) >= 4
    ]


def _sentence_length_cv(text: str) -> tuple[float, int] | None:
    lengths = [han_count(match.group()) for match in _sentence_matches(text)]
    if len(lengths) < 12:
        return None
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return None
    variance = sum((length - mean) ** 2 for length in lengths) / len(lengths)
    return math.sqrt(variance) / mean, len(lengths)


def _paragraphs(text: str) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    cursor = 0
    for block in re.split(r"\n\s*\n", text):
        position = text.find(block, cursor)
        if position < 0:
            continue
        cursor = position + len(block)
        clean = re.sub(r"[*_`]", "", block).strip()
        if not clean or re.match(r"^(?:[-+*]|\d+[.、])\s", clean):
            continue
        count = han_count(clean)
        if count < 4:
            continue
        sentences = max(1, len(re.findall(r"[。！？!?]", clean)))
        paragraphs.append(Paragraph(position, clean, count, sentences))
    return paragraphs


def _anaphora_matches(text: str) -> list[re.Match[str]]:
    matches: list[re.Match[str]] = []
    for sentence in _sentence_matches(text):
        clauses = [
            clause.strip()
            for clause in re.split(r"[，、；,;]", sentence.group())
            if han_count(clause) >= 3
        ]
        run = 1
        for previous, current in zip(clauses, clauses[1:]):
            if previous[:2] == current[:2] and re.match(r"[\u4e00-\u9fff]{2}", current):
                run += 1
                if run >= 3:
                    matches.append(sentence)
                    break
            else:
                run = 1
    return matches


def _max_cluster(positions: Iterable[int], distance: int) -> int:
    values = sorted(positions)
    best = 0
    right = 0
    for left, start in enumerate(values):
        right = max(right, left)
        while right < len(values) and values[right] - start <= distance:
            right += 1
        best = max(best, right - left)
    return best


def _metaphor_cluster(text: str, distance: int = 800) -> tuple[int, set[str]] | None:
    hits: list[tuple[int, str]] = []
    for field, words in METAPHOR_FIELDS.items():
        for word in words:
            hits.extend((match.start(), field) for match in re.finditer(re.escape(word), text))
    hits.sort()
    for index, (start, _) in enumerate(hits):
        window = [hit for hit in hits[index:] if hit[0] - start <= distance]
        fields = {field for _, field in window}
        if len(fields) >= 3:
            return start, fields
    return None


def analyze(text: str) -> Report:
    prose = mask_non_prose(text)
    total_han = han_count(prose)
    findings: list[Finding] = []

    pivots = _unique_matches(prose, PIVOT_PATTERNS)
    pivot_limit = max(2, total_han // 1500)
    pivot_cluster = _max_cluster((match.start() for match in pivots), 800)
    if len(pivots) > pivot_limit or pivot_cluster >= 3:
        findings.append(
            Finding(
                "review",
                "pivot-density",
                f"对比/翻案形状共 {len(pivots)} 处，提醒线 {pivot_limit} 处，八百字内最多 {pivot_cluster} 处；逐项确认是真实比较还是重复抬价。",
                line_number(text, pivots[0].start()),
            )
        )

    nominalizations = _unique_matches(prose, NOMINALIZATION_PATTERNS)
    if nominalizations:
        findings.append(
            Finding(
                "review",
                "nominalization",
                f"发现 {len(nominalizations)} 处可能的名词化表达；检查能否写回具体主体和动作。",
                line_number(text, nominalizations[0].start()),
            )
        )

    strong_terms = _term_positions(prose, STRONG_TERMS)
    if strong_terms:
        samples = "、".join(dict.fromkeys(term for _, term in strong_terms[:6]))
        findings.append(
            Finding(
                "review",
                "strong-signals",
                f"发现 {len(strong_terms)} 处强表达信号：{samples}。有具体功能时保留，没有承重时降调。",
                line_number(text, strong_terms[0][0]),
            )
        )

    anaphoras = _anaphora_matches(prose)
    if anaphoras:
        findings.append(
            Finding(
                "review",
                "anaphora",
                f"发现 {len(anaphoras)} 处三项以上同构排比；检查是否由材料需要，而非统一节拍。",
                line_number(text, anaphoras[0].start()),
            )
        )

    lyric_terms = _term_positions(prose, LYRIC_WORDS)
    if len(lyric_terms) >= 2:
        samples = "、".join(dict.fromkeys(term for _, term in lyric_terms))
        findings.append(
            Finding(
                "review",
                "lyric-density",
                f"抒情偏好词共 {len(lyric_terms)} 处：{samples}。写具体事物时保留，包装抽象概念时改回事实。",
                line_number(text, lyric_terms[0][0]),
            )
        )

    conjunctions = _term_positions(prose, CONJUNCTIONS)
    conjunction_density = (len(conjunctions) * 1000 / total_han) if total_han else 0.0
    if total_han >= 600 and conjunction_density > 8:
        findings.append(
            Finding(
                "metric",
                "conjunction-density",
                f"连词密度每千字 {conjunction_density:.1f} 个；检查能否由语序和事理承担部分连接。",
                line_number(text, conjunctions[0][0]),
            )
        )

    cv_result = _sentence_length_cv(prose)
    if cv_result and cv_result[0] < 0.42:
        findings.append(
            Finding(
                "metric",
                "sentence-length-variation",
                f"{cv_result[1]} 个句子的长度变异系数为 {cv_result[0]:.2f}；检查句长是否被同一模具压齐。",
            )
        )

    heavy_de = [
        match
        for match in _sentence_matches(prose)
        if han_count(match.group()) >= 38 and match.group().count("的") >= 4
    ]
    heavy_de_limit = max(1, total_han // 1500)
    if len(heavy_de) > heavy_de_limit:
        findings.append(
            Finding(
                "metric",
                "heavy-modifiers",
                f"有 {len(heavy_de)} 个长句包含四个以上“的”；检查主干是否来得太晚。",
                line_number(text, heavy_de[0].start()),
            )
        )

    paragraphs = _paragraphs(prose)
    opener_counts: collections.Counter[str] = collections.Counter()
    opener_positions: dict[str, int] = {}
    for paragraph in paragraphs:
        value = paragraph.text.lstrip("“‘\"（(")
        for opener in REPEATED_OPENERS:
            if value.startswith(opener):
                opener_counts[opener] += 1
                opener_positions.setdefault(opener, paragraph.position)
                break
    repeated = [(opener, count) for opener, count in opener_counts.items() if count >= 4]
    if repeated:
        details = "、".join(f"{opener} {count} 次" for opener, count in repeated)
        first_position = min(opener_positions[opener] for opener, _ in repeated)
        findings.append(
            Finding(
                "metric",
                "repeated-openers",
                f"段落开场重复：{details}。检查是否在用固定路标推进。",
                line_number(text, first_position),
            )
        )

    streak: list[Paragraph] = []
    for paragraph in paragraphs:
        if paragraph.han <= 24 and paragraph.sentences <= 1:
            streak.append(paragraph)
            if len(streak) >= 4:
                findings.append(
                    Finding(
                        "metric",
                        "short-paragraph-streak",
                        f"连续 {len(streak)} 个短促单句段；检查是否在排队喊结论。",
                        line_number(text, streak[0].position),
                    )
                )
                break
        else:
            streak = []

    highlights = list(re.finditer(r"[「『][^」』\n]{1,8}[」』]", prose))
    highlight_limit = max(3, total_han // 700)
    if len(highlights) > highlight_limit:
        findings.append(
            Finding(
                "metric",
                "highlight-density",
                f"短高亮词组共 {len(highlights)} 处，提醒线 {highlight_limit} 处；检查是否在批量命名或制造金句。",
                line_number(text, highlights[0].start()),
            )
        )

    metaphor_cluster = _metaphor_cluster(prose)
    if metaphor_cluster:
        position, fields = metaphor_cluster
        findings.append(
            Finding(
                "review",
                "metaphor-cluster",
                f"八百字内出现 {len(fields)} 套借喻：{'、'.join(sorted(fields))}。检查是否需要回到本义。",
                line_number(text, position),
            )
        )

    colon_count = prose.count("：") + prose.count(":")
    dash_count = len(re.findall(r"[—–]", prose))
    colon_density = (colon_count * 1000 / total_han) if total_han else 0.0
    dash_density = (dash_count * 1000 / total_han) if total_han else 0.0
    if total_han >= 600 and colon_count >= 8 and colon_density > 8:
        findings.append(
            Finding(
                "metric",
                "colon-density",
                f"冒号密度每千字 {colon_density:.1f} 个；检查是否用提示性标点代替句子推进。",
            )
        )
    if total_han >= 600 and dash_count >= 5 and dash_density > 4:
        findings.append(
            Finding(
                "metric",
                "dash-density",
                f"破折号密度每千字 {dash_density:.1f} 个；检查是否承担了过多补充和抬高语气。",
            )
        )

    metrics: dict[str, int | float] = {
        "han": total_han,
        "paragraphs": len(paragraphs),
        "pivots": len(pivots),
        "nominalizations": len(nominalizations),
        "strong_signals": len(strong_terms),
        "conjunctions_per_1000": round(conjunction_density, 2),
        "colons": colon_count,
        "dashes": dash_count,
    }
    if cv_result:
        metrics["sentence_length_cv"] = round(cv_result[0], 3)
        metrics["sentences"] = cv_result[1]
    return Report(metrics, findings)


def _read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _print_text(report: Report) -> None:
    metric_line = "，".join(f"{key}={value}" for key, value in report.metrics.items())
    print(metric_line)
    if not report.findings:
        print("未发现当前检查器覆盖的高密度表达形状。")
        return
    print("\n需要人工判断")
    for finding in report.findings:
        location = f"第 {finding.line} 行，" if finding.line else ""
        print(f"- [{finding.severity}] {finding.code}：{location}{finding.message}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查中文书面稿的重复表达与模型化形状")
    parser.add_argument("path", help="Markdown 或文本文件；使用 - 从标准输入读取")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args(argv)
    try:
        text = _read_text(args.path)
    except (OSError, UnicodeError) as error:
        print(f"无法读取稿件：{error}", file=sys.stderr)
        return 2
    if han_count(mask_non_prose(text)) == 0:
        print("没有检测到可检查的中文正文。", file=sys.stderr)
        return 2
    report = analyze(text)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        _print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
