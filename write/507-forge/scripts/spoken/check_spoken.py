#!/usr/bin/env python3
"""Advisory checks for Chinese talks, course scripts, and narration drafts."""

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
    re.compile(r"(?:并)?不是[^。！？\n]{1,70}(?:而是|，(?:更|才)?是)"),
    re.compile(r"并非[^。！？\n]{1,70}而是"),
    re.compile(r"不在于[^。！？\n]{1,70}而在于"),
    re.compile(r"(?:你|大家|我们)以为[^。！？\n]{1,70}(?:其实|后来才|才发现)"),
    re.compile(r"(?:表面(?:上)?|看似)[^。！？\n]{1,70}(?:实际(?:上)?|其实|实则)"),
)

TRANSITIONS = (
    "接下来我们",
    "接下来来看",
    "值得注意的是",
    "需要指出的是",
    "总的来说",
    "综上所述",
    "换句话说",
    "更重要的是",
    "还有一层",
    "首先",
    "其次",
    "最后",
)

ABSTRACT_TERMS = (
    "赋能",
    "闭环",
    "体系",
    "生态",
    "全链路",
    "底层逻辑",
    "顶层设计",
    "认知跃迁",
    "价值释放",
    "方法论",
    "结构性机会",
)

WRITTEN_META = (
    "本文将",
    "如下所示",
    "见下图",
    "上文提到",
    "下文将",
    "本章节",
    "本小节",
    "如前所述",
)

REPEATED_OPENERS = (
    "所以",
    "但是",
    "其实",
    "接下来",
    "然后",
    "我们来看",
    "大家可以看到",
    "这里",
    "这一步",
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    line: int | None = None


@dataclass(frozen=True)
class Segment:
    position: int
    text: str
    han: int


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


def mask_non_spoken(text: str) -> str:
    """Mask metadata, code, links, blockquotes, and page headings."""

    patterns = (
        re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", re.DOTALL),
        re.compile(r"```.*?```", re.DOTALL),
        re.compile(r"`[^`\n]*`"),
        re.compile(r"\]\([^\n)]*\)"),
        re.compile(r"https?://[^\s)>]+"),
        re.compile(r"<[^>\n]+>"),
        re.compile(r"^[ \t]*>.*$", re.MULTILINE),
        re.compile(r"^[ \t]*#{1,6}[ \t]+.*$", re.MULTILINE),
        re.compile(r"^[ \t]*\[(?:SECTION|SLIDE):[^\]]+\][ \t]*$", re.MULTILINE | re.IGNORECASE),
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
    for term in terms:
        found.extend((match.start(), term) for match in re.finditer(re.escape(term), text))
    return sorted(found)


def _sentence_matches(text: str) -> list[re.Match[str]]:
    return [
        match
        for match in re.finditer(r"[^。！？!?\n]+(?:[。！？!?]|$)", text)
        if han_count(match.group()) >= 4
    ]


def _segments(text: str) -> list[Segment]:
    segments: list[Segment] = []
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
        if count >= 4:
            segments.append(Segment(position, clean, count))
    return segments


def _length_cv(lengths: list[int]) -> float | None:
    if len(lengths) < 10:
        return None
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return None
    variance = sum((length - mean) ** 2 for length in lengths) / len(lengths)
    return math.sqrt(variance) / mean


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


def analyze(text: str) -> Report:
    spoken = mask_non_spoken(text)
    total_han = han_count(spoken)
    findings: list[Finding] = []
    sentences = _sentence_matches(spoken)
    lengths = [han_count(match.group()) for match in sentences]

    long_sentences = [match for match in sentences if han_count(match.group()) > 46]
    if long_sentences:
        findings.append(
            Finding(
                "review",
                "long-breath",
                f"发现 {len(long_sentences)} 个超过 46 个汉字的句子；朗读确认是否需要回气或回找主语。",
                line_number(text, long_sentences[0].start()),
            )
        )

    pivots = _unique_matches(spoken, PIVOT_PATTERNS)
    pivot_limit = max(2, total_han // 1200)
    pivot_cluster = _max_cluster((match.start() for match in pivots), 600)
    if len(pivots) > pivot_limit or pivot_cluster >= 3:
        findings.append(
            Finding(
                "review",
                "pivot-density",
                f"对比/翻案形状共 {len(pivots)} 处，提醒线 {pivot_limit} 处，六百字内最多 {pivot_cluster} 处；检查是否在重复制造转折。",
                line_number(text, pivots[0].start()),
            )
        )

    transitions = _term_positions(spoken, TRANSITIONS)
    transition_density = (len(transitions) * 1000 / total_han) if total_han else 0.0
    if len(transitions) >= 4 or (total_han >= 500 and transition_density > 6):
        samples = "、".join(dict.fromkeys(term for _, term in transitions[:6]))
        findings.append(
            Finding(
                "review",
                "transition-density",
                f"显式转场词共 {len(transitions)} 处：{samples}。检查能否让案例、动作或问题自然接力。",
                line_number(text, transitions[0][0]),
            )
        )

    abstract_terms = _term_positions(spoken, ABSTRACT_TERMS)
    abstract_density = (len(abstract_terms) * 1000 / total_han) if total_han else 0.0
    if len(abstract_terms) >= 3 and abstract_density > 3:
        samples = "、".join(dict.fromkeys(term for _, term in abstract_terms[:8]))
        findings.append(
            Finding(
                "review",
                "abstract-density",
                f"抽象或汇报词共 {len(abstract_terms)} 处：{samples}。检查是否已有案例动作承重。",
                line_number(text, abstract_terms[0][0]),
            )
        )

    written_meta = _term_positions(spoken, WRITTEN_META)
    if written_meta:
        samples = "、".join(dict.fromkeys(term for _, term in written_meta))
        findings.append(
            Finding(
                "review",
                "written-meta",
                f"发现可能泄漏到口播的书面元话语：{samples}。确认它是否真的会被说出口。",
                line_number(text, written_meta[0][0]),
            )
        )

    cv = _length_cv(lengths)
    if cv is not None and cv < 0.38:
        findings.append(
            Finding(
                "metric",
                "sentence-length-variation",
                f"{len(lengths)} 个句子的长度变异系数为 {cv:.2f}；检查口播是否被同一节拍压齐。",
            )
        )

    segments = _segments(spoken)
    opener_counts: collections.Counter[str] = collections.Counter()
    opener_positions: dict[str, int] = {}
    for segment in segments:
        value = segment.text.lstrip("“‘\"（(")
        for opener in REPEATED_OPENERS:
            if value.startswith(opener):
                opener_counts[opener] += 1
                opener_positions.setdefault(opener, segment.position)
                break
    repeated = [(opener, count) for opener, count in opener_counts.items() if count >= 4]
    if repeated:
        details = "、".join(f"{opener} {count} 次" for opener, count in repeated)
        first_position = min(opener_positions[opener] for opener, _ in repeated)
        findings.append(
            Finding(
                "metric",
                "repeated-openers",
                f"口播段开场重复：{details}。检查是否在用固定转场代替内容推进。",
                line_number(text, first_position),
            )
        )

    pronunciation_patterns = (
        re.compile(r"(?<![A-Za-z])[A-Z]{2,8}(?![A-Za-z])"),
        re.compile(r"(?<![A-Za-z0-9])[vV]?\d+(?:\.\d+){1,3}(?![A-Za-z0-9])"),
        re.compile(r"\d+(?:\.\d+)?%"),
    )
    pronunciation = _unique_matches(spoken, pronunciation_patterns)
    pronunciation_values = list(dict.fromkeys(match.group() for match in pronunciation))
    if pronunciation:
        samples = "、".join(pronunciation_values[:10])
        findings.append(
            Finding(
                "metric",
                "pronunciation-candidates",
                f"发现 {len(pronunciation_values)} 个不同发音候选、共出现 {len(pronunciation)} 次：{samples}。确认缩写、版本和数字的自然读法。",
                line_number(text, pronunciation[0].start()),
            )
        )

    metrics: dict[str, int | float] = {
        "han": total_han,
        "segments": len(segments),
        "sentences": len(sentences),
        "long_sentences": len(long_sentences),
        "pivots": len(pivots),
        "transitions": len(transitions),
        "abstract_terms": len(abstract_terms),
        "pronunciation_candidates": len(pronunciation_values),
        "pronunciation_mentions": len(pronunciation),
    }
    if cv is not None:
        metrics["sentence_length_cv"] = round(cv, 3)
    return Report(metrics, findings)


def _read_text(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _print_text(report: Report) -> None:
    print("，".join(f"{key}={value}" for key, value in report.metrics.items()))
    if not report.findings:
        print("未发现当前检查器覆盖的高密度口播形状。")
        return
    print("\n需要人工判断")
    for finding in report.findings:
        location = f"第 {finding.line} 行，" if finding.line else ""
        print(f"- [{finding.severity}] {finding.code}：{location}{finding.message}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查中文讲稿与旁白的可说性和重复形状")
    parser.add_argument("path", help="Markdown 或文本文件；使用 - 从标准输入读取")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args(argv)
    try:
        text = _read_text(args.path)
    except (OSError, UnicodeError) as error:
        print(f"无法读取稿件：{error}", file=sys.stderr)
        return 2
    if han_count(mask_non_spoken(text)) == 0:
        print("没有检测到可检查的中文口播。", file=sys.stderr)
        return 2
    report = analyze(text)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        _print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
