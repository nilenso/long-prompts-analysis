#!/usr/bin/env python3
"""Generate release-changes.json: for each model release, diff the nearest
prompt files before and after the release date and produce a summary."""

import csv
import difflib
import json
import os
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
TOKENS_CSV = Path(__file__).parent / "cc-prompts-tokens.csv"
RELEASES_CSV = Path(__file__).parent / "model-releases.csv"
OUTPUT = Path(__file__).parent / "release-changes.json"

# Lines matching these patterns are noise in diffs (version headers, dates, temp paths)
NOISE_RE = re.compile(
    r"^(#\s*Claude Code Version|Release Date:|#\s*User Message|/private/tmp/|/tmp/|/var/folders/)",
    re.IGNORECASE,
)


def load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def load_releases(path):
    rows = []
    with open(path, newline="") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("model"):
                continue
            last = line.rfind(",")
            vendor = line[last + 1 :].strip()
            rest = line[:last]
            second_last = rest.rfind(",")
            date = rest[second_last + 1 :].strip()
            label = rest[:second_last].strip()
            rows.append({"model": label, "release_date": date, "vendor": vendor})
    return rows


def prompt_file_path(row):
    if row["prompt_name"] == "claude-code":
        return DATA_DIR / "claude-code" / row["filename"]
    return DATA_DIR / "codex" / row["filename"]


def read_lines(path):
    try:
        return open(path).readlines()
    except FileNotFoundError:
        return []


def is_noise(line):
    stripped = line.lstrip("+-").strip()
    return bool(NOISE_RE.match(stripped))


def compute_diff(before_path, after_path):
    """Return (lines_added, lines_removed, added_lines_text, removed_lines_text)."""
    a = read_lines(before_path)
    b = read_lines(after_path)
    diff = list(difflib.unified_diff(a, b, lineterm=""))

    added, removed = [], []
    for line in diff:
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            continue
        if line.startswith("+"):
            content = line[1:]
            if not is_noise(content):
                added.append(content)
        elif line.startswith("-"):
            content = line[1:]
            if not is_noise(content):
                removed.append(content)

    return len(added), len(removed), added, removed


def extract_section_headers(lines):
    """Pull markdown headers from diff lines."""
    headers = []
    for line in lines:
        stripped = line.strip()
        m = re.match(r"^(#{1,3})\s+(.+)", stripped)
        if m:
            headers.append(m.group(2).strip())
    return headers


def generate_summary(added_lines, removed_lines):
    """Build a human-readable summary from diff content."""
    parts = []

    added_headers = extract_section_headers(added_lines)
    removed_headers = extract_section_headers(removed_lines)

    if added_headers:
        parts.append("Added sections: " + "; ".join(added_headers))
    if removed_headers:
        parts.append("Removed sections: " + "; ".join(removed_headers))

    # Look for significant added content patterns
    significant_adds = []
    for line in added_lines:
        s = line.strip()
        # Tool names, feature names, important keywords
        if re.match(r"^-\s+\*\*", s) or re.match(r'^"[A-Z]', s):
            # Bold list items or quoted feature names
            clean = re.sub(r"\*\*", "", s).lstrip("- ").strip()
            if len(clean) > 5 and len(clean) < 120:
                significant_adds.append(clean)

    if significant_adds and not added_headers:
        items = significant_adds[:5]
        parts.append("Added: " + "; ".join(items))

    significant_removes = []
    for line in removed_lines:
        s = line.strip()
        if re.match(r"^-\s+\*\*", s) or re.match(r'^"[A-Z]', s):
            clean = re.sub(r"\*\*", "", s).lstrip("- ").strip()
            if len(clean) > 5 and len(clean) < 120:
                significant_removes.append(clean)

    if significant_removes and not removed_headers:
        items = significant_removes[:5]
        parts.append("Removed: " + "; ".join(items))

    if not parts:
        n_add = len([l for l in added_lines if l.strip()])
        n_rem = len([l for l in removed_lines if l.strip()])
        if n_add or n_rem:
            bits = []
            if n_add:
                bits.append(f"{n_add} lines added")
            if n_rem:
                bits.append(f"{n_rem} lines removed")
            parts.append("; ".join(bits))

    return "; ".join(parts) if parts else "Minor changes"


def prompt_vendor(prompt_name):
    """Match the vendor logic from the frontend."""
    return "anthropic" if prompt_name == "claude-code" else "openai"


def main():
    tokens_rows = load_csv(TOKENS_CSV)
    releases = load_releases(RELEASES_CSV)

    # Group prompt rows by prompt_name, sorted by date then version
    by_name = {}
    for r in tokens_rows:
        by_name.setdefault(r["prompt_name"], []).append(r)
    for name in by_name:
        by_name[name].sort(key=lambda r: r["release_date"])

    # Determine date range of our data
    all_dates = [r["release_date"] for r in tokens_rows]
    min_date = min(all_dates)
    max_date = max(all_dates)

    output = []
    for rel in releases:
        rd = rel["release_date"]
        # Only process releases within our data range (with some slack)
        if rd < min_date or rd > max_date:
            continue

        changes = []
        for prompt_name, prompt_rows in by_name.items():
            # Only include prompts whose vendor matches the model release vendor
            if prompt_vendor(prompt_name) != rel["vendor"]:
                continue

            # Find nearest before (strictly before release date) and
            # after (on or after release date), so that prompt versions
            # shipping on the same day as the model are the "after".
            before = None
            after = None
            for r in prompt_rows:
                if r["release_date"] < rd:
                    before = r
                elif after is None:
                    after = r

            if not before or not after:
                continue

            before_path = prompt_file_path(before)
            after_path = prompt_file_path(after)

            if not before_path.exists() or not after_path.exists():
                continue

            lines_added, lines_removed, added_text, removed_text = compute_diff(
                before_path, after_path
            )

            # Skip if no meaningful diff
            if lines_added == 0 and lines_removed == 0:
                continue

            before_tokens = int(before["tokens"])
            after_tokens = int(after["tokens"])

            summary = generate_summary(added_text, removed_text)

            changes.append(
                {
                    "prompt_name": prompt_name,
                    "before_version": before["version"],
                    "after_version": after["version"],
                    "before_tokens": before_tokens,
                    "after_tokens": after_tokens,
                    "token_delta": after_tokens - before_tokens,
                    "lines_added": lines_added,
                    "lines_removed": lines_removed,
                    "summary": summary,
                }
            )

        output.append(
            {
                "model": rel["model"],
                "release_date": rd,
                "vendor": rel["vendor"],
                "changes": changes,
            }
        )

    # Sort by release date
    output.sort(key=lambda x: x["release_date"])

    with open(OUTPUT, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(output)} releases to {OUTPUT}")
    for entry in output:
        n = len(entry["changes"])
        print(f"  {entry['release_date']} {entry['model']}: {n} prompt changes")


if __name__ == "__main__":
    main()
