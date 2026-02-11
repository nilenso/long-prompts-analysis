#!/usr/bin/env python3
"""
Annotate prompt files for weight-fighting signals.

Weight-fighting signals:
A) Reminders / nagging
B) Repetition / reiteration
C) Negative prohibitions
D) Forceful / imperative / deontic language
E) Shouting / emphasis
F) Threats / pleading / bribery
G) Over-constraining output format
"""

import os
import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

# Signal detection patterns
SIGNALS = {
    "A_reminders": {
        "name": "Reminders/Nagging",
        "patterns": [
            r"\bremember\b",
            r"\bdon'?t forget\b",
            r"\bas a reminder\b",
            r"\bnote that\b",
            r"\bkeep in mind\b",
            r"\bi repeat\b",
            r"\bfrom now on\b",
            r"\brecall that\b",
            r"\bbe reminded\b",
        ]
    },
    "B_repetition": {
        "name": "Repetition/Reiteration",
        "patterns": [
            r"\bagain\b",
            r"\bonce more\b",
            r"\bto reiterate\b",
            r"\bto repeat\b",
            r"\bas mentioned\b",
            r"\bas stated\b",
            r"\bas noted\b",
            r"\bonce again\b",
        ]
    },
    "C_prohibitions": {
        "name": "Negative Prohibitions",
        "patterns": [
            r"\bdo not\b",
            r"\bdon'?t\b",
            r"\bnever\b",
            r"\bno\s+\w+ing\b",  # "no explaining", "no adding", etc.
            r"\bstop\b",
            r"\bavoid\b",
            r"\bunder no circumstances\b",
            r"\bdo NOT\b",
            r"\bDO NOT\b",
            r"\bNEVER\b",
            r"\brefrain from\b",
            r"\bprohibited\b",
            r"\bforbidden\b",
        ]
    },
    "D_forceful": {
        "name": "Forceful/Imperative/Deontic",
        "patterns": [
            r"\byou must\b",
            r"\bMUST\b",
            r"\balways\b",
            r"\bALWAYS\b",
            r"\brequired\b",
            r"\bREQUIRED\b",
            r"\bstrictly\b",
            r"\bSTRICTLY\b",
            r"\bat all times\b",
            r"\bonly\b.*\band nothing else\b",
            r"\bmandatory\b",
            r"\bshall\b",
            r"\bimperative\b",
            r"\bessential\b",
            r"\bcritical\b",
            r"\bCRITICAL\b",
            r"\bIMPORTANT\b",
            r"\bvery important\b",
            r"\bextremely important\b",
        ]
    },
    "E_shouting": {
        "name": "Shouting/Emphasis",
        "patterns": [
            r"\b[A-Z]{2,}\b",  # Words in ALL CAPS (2+ chars)
            r"!{2,}",  # Multiple exclamation marks
            r"\*\*[^*]+\*\*",  # Bold markdown
            r"_{2}[^_]+_{2}",  # Bold with underscores
        ]
    },
    "F_threats_pleading": {
        "name": "Threats/Pleading/Bribery",
        "patterns": [
            r"\bor else\b",
            r"\bi will\b",
            r"\byou'?d better\b",
            r"\bplease just\b",
            r"\bi beg\b",
            r"\bi swear\b",
            r"\bi'?ll pay\b",
            r"\bi'?ll tip\b",
            r"\bif you don'?t\b",
            r"\bwill be punished\b",
            r"\bwill be penalized\b",
        ]
    },
    "G_overconstrained": {
        "name": "Over-constraining Output",
        "patterns": [
            r"\bonly json\b",
            r"\bONLY JSON\b",
            r"\bno extra words\b",
            r"\bno explanations?\b",
            r"\bend the turn\b",
            r"\bno additional\b",
            r"\bnothing else\b",
            r"\bexactly as\b",
            r"\bverbatim\b",
            r"\bword for word\b",
            r"\bprecisely\b",
            r"\bjust the\b.*\bnothing\b",
        ]
    }
}

# Common false positives to exclude
FALSE_POSITIVE_CONTEXTS = [
    r"if\s+you\s+do\s+not",  # conditional, not prohibition
    r"may\s+or\s+may\s+not",  # neutral statement
]


@dataclass
class SignalMatch:
    signal_type: str
    signal_name: str
    matched_text: str
    start: int
    end: int


@dataclass
class AnnotatedParagraph:
    index: int
    text: str
    signals: List[SignalMatch] = field(default_factory=list)
    is_fighting: bool = False

    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "text": self.text,
            "is_fighting": self.is_fighting,
            "signals": [
                {
                    "type": s.signal_type,
                    "name": s.signal_name,
                    "matched": s.matched_text
                }
                for s in self.signals
            ]
        }


def split_into_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs by blank lines."""
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Split by one or more blank lines
    paragraphs = re.split(r'\n\s*\n', text)

    # Clean up and filter empty paragraphs
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    return paragraphs


def detect_signals(text: str) -> List[SignalMatch]:
    """Detect weight-fighting signals in text."""
    matches = []

    for signal_type, signal_info in SIGNALS.items():
        for pattern in signal_info["patterns"]:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Skip common false positives
                is_false_positive = False
                context_start = max(0, match.start() - 20)
                context_end = min(len(text), match.end() + 20)
                context = text[context_start:context_end]

                for fp_pattern in FALSE_POSITIVE_CONTEXTS:
                    if re.search(fp_pattern, context, re.IGNORECASE):
                        is_false_positive = True
                        break

                if not is_false_positive:
                    matches.append(SignalMatch(
                        signal_type=signal_type,
                        signal_name=signal_info["name"],
                        matched_text=match.group(),
                        start=match.start(),
                        end=match.end()
                    ))

    # Deduplicate matches at same position
    seen = set()
    unique_matches = []
    for m in matches:
        key = (m.start, m.end, m.matched_text.lower())
        if key not in seen:
            seen.add(key)
            unique_matches.append(m)

    return unique_matches


def annotate_paragraph(index: int, text: str) -> AnnotatedParagraph:
    """Annotate a single paragraph for weight-fighting signals."""
    signals = detect_signals(text)

    # Determine if paragraph is "fighting" based on signal presence and density
    # A paragraph is considered "fighting" if it has significant signals
    is_fighting = len(signals) > 0

    return AnnotatedParagraph(
        index=index,
        text=text,
        signals=signals,
        is_fighting=is_fighting
    )


def process_file(filepath: Path) -> Tuple[str, List[AnnotatedParagraph]]:
    """Process a single file and return annotated paragraphs."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    paragraphs = split_into_paragraphs(content)
    annotated = [annotate_paragraph(i, p) for i, p in enumerate(paragraphs)]

    return filepath.name, annotated


def format_annotated_output(filename: str, paragraphs: List[AnnotatedParagraph]) -> str:
    """Format annotated paragraphs as readable text output."""
    lines = []
    lines.append(f"# Analysis: {filename}")
    lines.append(f"# Total paragraphs: {len(paragraphs)}")
    fighting_count = sum(1 for p in paragraphs if p.is_fighting)
    lines.append(f"# Paragraphs with weight-fighting signals: {fighting_count}")
    lines.append(f"# Percentage: {fighting_count/len(paragraphs)*100:.1f}%")
    lines.append("=" * 80)
    lines.append("")

    for para in paragraphs:
        # Header with annotation
        if para.is_fighting:
            signal_types = list(set(s.signal_type for s in para.signals))
            signal_names = list(set(s.signal_name for s in para.signals))
            lines.append(f"## [PARAGRAPH {para.index}] [FIGHTING: YES]")
            lines.append(f"## Signals detected: {', '.join(signal_names)}")
            matched_texts = list(set(f'"{s.matched_text}"' for s in para.signals))
            lines.append(f"## Matched: {', '.join(matched_texts[:10])}")  # Limit to 10
        else:
            lines.append(f"## [PARAGRAPH {para.index}] [FIGHTING: NO]")

        lines.append("")
        lines.append(para.text)
        lines.append("")
        lines.append("-" * 80)
        lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point."""
    input_dir = Path("/Users/srihari/work/nilenso/long-prompts-analysis/data/prompts/filtered")
    output_dir = Path("/Users/srihari/work/nilenso/long-prompts-analysis/data/prompts/annotated")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each .txt file
    txt_files = list(input_dir.glob("*.txt"))

    all_results = {}

    for filepath in txt_files:
        print(f"Processing: {filepath.name}")
        filename, annotated = process_file(filepath)
        all_results[filename] = [p.to_dict() for p in annotated]

        # Write annotated text output
        output_text = format_annotated_output(filename, annotated)
        output_path = output_dir / f"{filepath.stem}_annotated.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_text)

        # Print summary
        fighting_count = sum(1 for p in annotated if p.is_fighting)
        print(f"  - {len(annotated)} paragraphs, {fighting_count} with weight-fighting signals")

    # Write JSON summary
    json_output = output_dir / "all_annotations.json"
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)

    print(f"\nOutput written to: {output_dir}")


if __name__ == "__main__":
    main()
