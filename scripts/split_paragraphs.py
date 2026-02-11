#!/usr/bin/env python3
"""
Split prompt files into paragraphs and output numbered JSON for annotation.
"""

import os
import re
import json
from pathlib import Path


def split_into_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs by blank lines."""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    paragraphs = re.split(r'\n\s*\n', text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    return paragraphs


def main():
    input_dir = Path("/Users/srihari/work/nilenso/long-prompts-analysis/data/prompts/filtered")
    output_dir = Path("/Users/srihari/work/nilenso/long-prompts-analysis/data/prompts/paragraphs")
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in input_dir.glob("*.txt"):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        paragraphs = split_into_paragraphs(content)

        # Create structured output for annotation
        output = {
            "source_file": filepath.name,
            "total_paragraphs": len(paragraphs),
            "paragraphs": [
                {
                    "index": i,
                    "text": p,
                    "is_fighting": None,  # To be filled in
                    "signals": [],        # To be filled in
                    "notes": ""           # To be filled in
                }
                for i, p in enumerate(paragraphs)
            ]
        }

        output_path = output_dir / f"{filepath.stem}_paragraphs.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"{filepath.name}: {len(paragraphs)} paragraphs -> {output_path.name}")


if __name__ == "__main__":
    main()
