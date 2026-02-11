#!/usr/bin/env python3
"""Parse swapping-prompts-swe-tasks.json and produce a CSV summary.

Columns = agents (e.g. opus-empty, opus-codex, gpt-claude, …)
Rows    = tasks  (e.g. untrusted-args, subdomain-blocking, …)
Cells   = "time_seconds / total_tokens"
"""

import json
import csv
import re
import sys
from datetime import datetime
from collections import defaultdict

INPUT = (
    "/Users/srihari/work/nilenso/long-prompts-analysis/"
    "context-viewer-exports/swapping-prompts-swe-tasks.json"
)
OUTPUT = (
    "/Users/srihari/work/nilenso/long-prompts-analysis/"
    "context-viewer-exports/swe-tasks-summary.csv"
)

# Filename pattern: {task}_{model}_{prompt}_{hash}.json[.json]
# task can contain hyphens, model is opus/gpt, prompt is empty/codex/claude
FNAME_RE = re.compile(
    r"^(?P<task>.+?)_(?P<model>opus|gpt)_(?P<prompt>empty|codex|claude)_[0-9a-f]+\.json(?:\.json)?$"
)


def parse_filename(filename):
    """Return (task, agent) from a filename like 'untrusted-args_opus_empty_8f46ba3f.json'."""
    m = FNAME_RE.match(filename)
    if not m:
        return None, None
    task = m.group("task")
    agent = f"{m.group('model')}-{m.group('prompt')}"
    return task, agent


def parse_ts(ts_str):
    """Parse an ISO timestamp string to a datetime."""
    # Handle both with and without trailing Z
    ts_str = ts_str.rstrip("Z")
    return datetime.fromisoformat(ts_str)


def process_file_entry(entry):
    """Extract (task, agent, duration_seconds, total_tokens) from a file entry."""
    filename = entry["filename"]
    task, agent = parse_filename(filename)
    if task is None:
        print(f"WARNING: could not parse filename: {filename}", file=sys.stderr)
        return None

    # Prefer metadata.agent if available, otherwise use filename-derived agent
    meta_agent = (entry.get("metadata") or {}).get("agent")
    if meta_agent:
        agent = meta_agent

    messages = entry.get("conversation", {}).get("messages", [])

    # Collect all timestamps and token counts
    timestamps = []
    total_tokens = 0

    for msg in messages:
        ts = msg.get("timestamp")
        if ts:
            timestamps.append(parse_ts(ts))
        for part in msg.get("parts", []):
            tc = part.get("token_count", 0)
            if tc:
                total_tokens += tc

    if len(timestamps) >= 2:
        duration = (max(timestamps) - min(timestamps)).total_seconds()
    elif len(timestamps) == 1:
        duration = 0
    else:
        duration = None  # no timestamps at all

    return task, agent, duration, total_tokens


def fmt_duration(seconds):
    """Format seconds as mm:ss."""
    if seconds is None:
        return "n/a"
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def fmt_rate(tokens, seconds):
    """Format tokens/second as a rounded float."""
    if seconds is None or seconds == 0 or tokens <= 1:
        return "n/a"
    return f"{tokens / seconds:.1f}"


def main():
    with open(INPUT) as f:
        data = json.load(f)

    # data structure: { files: [ { filename, conversation, metadata, ... }, ... ] }
    files = data.get("files", [])

    # Collect results keyed by (task, agent)
    results = {}
    all_agents = set()
    all_tasks = []
    seen_tasks = set()

    for entry in files:
        result = process_file_entry(entry)
        if result is None:
            continue
        task, agent, duration, total_tokens = result
        results[(task, agent)] = (duration, total_tokens)
        all_agents.add(agent)
        if task not in seen_tasks:
            seen_tasks.add(task)
            all_tasks.append(task)

    # Sort agents in a sensible order
    agent_order = sorted(all_agents, key=lambda a: (
        0 if a.startswith("opus") else 1,
        a,
    ))

    # Write CSV
    with open(OUTPUT, "w", newline="") as f:
        writer = csv.writer(f)

        # Header row
        header = ["task"]
        for agent in agent_order:
            header.append(f"{agent} (time)")
            header.append(f"{agent} (tokens)")
            header.append(f"{agent} (tok/s)")
        writer.writerow(header)

        # Data rows
        for task in all_tasks:
            row = [task]
            for agent in agent_order:
                dur, tok = results.get((task, agent), (None, 0))
                if dur is None or tok <= 1:
                    row.extend(["n/a", "n/a", "n/a"])
                else:
                    row.append(fmt_duration(dur))
                    row.append(tok)
                    row.append(fmt_rate(tok, dur))
            writer.writerow(row)

        # Totals and averages rows
        for row_label, use_avg in [("TOTAL", False), ("AVERAGE", True)]:
            row = [row_label]
            for agent in agent_order:
                durations = []
                tokens = []
                for task in all_tasks:
                    dur, tok = results.get((task, agent), (None, 0))
                    if dur is not None and tok > 1:
                        durations.append(dur)
                        tokens.append(tok)
                if not durations:
                    row.extend(["n/a", "n/a", "n/a"])
                elif use_avg:
                    avg_dur = sum(durations) / len(durations)
                    avg_tok = int(sum(tokens) / len(tokens))
                    row.append(fmt_duration(avg_dur))
                    row.append(avg_tok)
                    row.append(fmt_rate(avg_tok, avg_dur))
                else:
                    row.append(fmt_duration(sum(durations)))
                    row.append(sum(tokens))
                    row.append(fmt_rate(sum(tokens), sum(durations)))
            writer.writerow(row)

    print(f"Wrote {OUTPUT}")
    print(f"  {len(all_tasks)} tasks x {len(all_agents)} agents")
    print(f"  Agents: {', '.join(agent_order)}")
    print()

    # Also print a quick readable table
    col_w = 28
    print(f"{'task':<22}", end="")
    for agent in agent_order:
        print(f"{agent:>{col_w}}", end="")
    print()
    print("-" * (22 + col_w * len(agent_order)))
    for task in all_tasks:
        print(f"{task:<22}", end="")
        for agent in agent_order:
            dur, tok = results.get((task, agent), (None, 0))
            if dur is None or tok <= 1:
                cell = "n/a"
            else:
                cell = f"{fmt_duration(dur)} / {tok} ({fmt_rate(tok, dur)})"
            print(f"{cell:>{col_w}}", end="")
        print()

    print("-" * (22 + col_w * len(agent_order)))
    for row_label, use_avg in [("TOTAL", False), ("AVERAGE", True)]:
        print(f"{row_label:<22}", end="")
        for agent in agent_order:
            durations = []
            tokens = []
            for task in all_tasks:
                dur, tok = results.get((task, agent), (None, 0))
                if dur is not None and tok > 1:
                    durations.append(dur)
                    tokens.append(tok)
            if not durations:
                cell = "n/a"
            elif use_avg:
                avg_dur = sum(durations) / len(durations)
                avg_tok = int(sum(tokens) / len(tokens))
                cell = f"{fmt_duration(avg_dur)} / {avg_tok} ({fmt_rate(avg_tok, avg_dur)})"
            else:
                total_dur = sum(durations)
                total_tok = sum(tokens)
                cell = f"{fmt_duration(total_dur)} / {total_tok} ({fmt_rate(total_tok, total_dur)})"
            print(f"{cell:>{col_w}}", end="")
        print()


if __name__ == "__main__":
    main()
