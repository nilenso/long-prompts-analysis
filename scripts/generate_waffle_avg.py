#!/usr/bin/env python3
"""
Generate an HTML file with waffle charts showing average token distribution
per agent across SWE benchmark tasks.
"""

import json
import re
from collections import defaultdict
import math

# --- Configuration ---
INPUT_FILE = "/Users/srihari/work/nilenso/long-prompts-analysis/context-viewer-exports/swapping-prompts-swe-tasks.json"
OUTPUT_FILE = "/Users/srihari/work/nilenso/long-prompts-analysis/context-viewer-exports/swe-tasks-waffle-avg.html"

AGENTS = ["opus_empty", "opus_claude", "opus_codex", "gpt_claude", "gpt_codex"]

AGENT_LABELS = {
    "opus_empty": "Opus + Empty Prompt",
    "opus_claude": "Opus + Claude Prompt",
    "opus_codex": "Opus + Codex Prompt",
    "gpt_claude": "GPT + Claude Prompt",
    "gpt_codex": "GPT + Codex Prompt",
}

# Canonical category order and colors
CATEGORIES = [
    "understand.read-requirements",
    "understand.read-tests",
    "explore.search-files",
    "explore.read-source",
    "explore.read-section",
    "explore.search-keywords",
    "explore.delegate-exploration",
    "explore.read-tests",
    "plan.update-tasks",
    "implement.apply-patch",
    "implement.write-code",
    "implement.create-file",
    "verify.run-tests-verify",
    "verify.run-tests-specific",
    "complete.update-tasks",
    "analyze.run-tests-diagnostic",
    "analyze.check-environment",
]

COLORS = {
    "understand.read-requirements": "#4E79A7",
    "understand.read-tests": "#59A14F",
    "explore.search-files": "#F28E2B",
    "explore.read-source": "#E15759",
    "explore.read-section": "#76B7B2",
    "explore.search-keywords": "#EDC948",
    "explore.delegate-exploration": "#B07AA1",
    "explore.read-tests": "#9C755F",
    "plan.update-tasks": "#FF9DA7",
    "implement.apply-patch": "#AF7AA1",
    "implement.write-code": "#BAB0AC",
    "implement.create-file": "#D4A6C8",
    "verify.run-tests-verify": "#86BCB6",
    "verify.run-tests-specific": "#8CD17D",
    "complete.update-tasks": "#B6992D",
    "analyze.run-tests-diagnostic": "#499894",
    "analyze.check-environment": "#D37295",
}


def identify_agent(filename):
    """Extract agent identifier from filename."""
    for agent in AGENTS:
        if f"_{agent}_" in filename or filename.startswith(f"{agent}_"):
            return agent
    # Handle patterns like "task_opus_empty_hash"
    for agent in AGENTS:
        parts = agent.split("_")
        # Check if both parts appear in sequence
        pattern = f"_{parts[0]}_{parts[1]}_"
        if pattern in filename:
            return agent
    return None


def main():
    # Load JSON
    print("Loading JSON file...")
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    comparison = data["analytics"]["componentComparison"]
    print(f"Found {len(comparison)} entries in componentComparison")

    # Group by agent
    agent_entries = defaultdict(list)
    for entry in comparison:
        filename = entry["filename"]
        agent = identify_agent(filename)
        if agent is None:
            print(f"WARNING: Could not identify agent for {filename}")
            continue
        agent_entries[agent].append(entry)

    # Print grouping info
    for agent in AGENTS:
        entries = agent_entries[agent]
        print(f"  {agent}: {len(entries)} entries")
        for e in entries:
            print(f"    {e['filename']} totalTokens={e['totalTokens']}")

    # Compute averages per agent
    agent_averages = {}
    for agent in AGENTS:
        entries = agent_entries[agent]
        # Filter out broken entries (gpt with totalTokens == 1)
        valid_entries = []
        for e in entries:
            if agent.startswith("gpt") and e["totalTokens"] == 1:
                print(f"  Skipping broken entry: {e['filename']}")
                continue
            valid_entries.append(e)

        n = len(valid_entries)
        if n == 0:
            print(f"  WARNING: No valid entries for {agent}")
            continue

        # Sum componentTokens
        cat_sums = defaultdict(float)
        total_sum = 0
        turn_sum = 0
        msg_sum = 0
        for e in valid_entries:
            total_sum += e["totalTokens"]
            turn_sum += e["turnCount"]
            msg_sum += e["messageCount"]
            for cat, tokens in e["componentTokens"].items():
                cat_sums[cat] += tokens

        # Compute averages
        avg_cats = {cat: cat_sums[cat] / n for cat in cat_sums}
        avg_total = total_sum / n
        avg_turns = turn_sum / n
        avg_msgs = msg_sum / n

        agent_averages[agent] = {
            "avg_categories": avg_cats,
            "avg_total_tokens": avg_total,
            "avg_turn_count": avg_turns,
            "avg_message_count": avg_msgs,
            "valid_task_count": n,
        }

        print(f"\n  {agent} averages (over {n} valid tasks):")
        print(f"    Total tokens: {avg_total:.0f}")
        print(f"    Turn count: {avg_turns:.1f}")
        print(f"    Message count: {avg_msgs:.1f}")
        for cat in CATEGORIES:
            if cat in avg_cats:
                print(f"    {cat}: {avg_cats[cat]:.0f}")

    # --- Generate HTML ---
    print("\nGenerating HTML...")

    # Build waffle data for each agent
    TOTAL_SQUARES = 100
    COLS = 10

    def compute_waffle(avg_cats, avg_total):
        """Compute waffle square allocation for categories."""
        # Only include categories with nonzero average
        active_cats = [(cat, avg_cats.get(cat, 0)) for cat in CATEGORIES if avg_cats.get(cat, 0) > 0]
        if not active_cats:
            return []

        total = sum(v for _, v in active_cats)

        # First pass: proportional allocation
        raw = [(cat, (val / total) * TOTAL_SQUARES) for cat, val in active_cats]

        # Give at least 1 square to any category present
        allocated = []
        remainder_pool = 0
        for cat, raw_count in raw:
            if raw_count > 0 and raw_count < 1:
                allocated.append((cat, 1, raw_count))
                remainder_pool -= (1 - raw_count)
            else:
                allocated.append((cat, int(raw_count), raw_count - int(raw_count)))
                remainder_pool += raw_count - int(raw_count)

        current_total = sum(a[1] for a in allocated)
        remaining = TOTAL_SQUARES - current_total

        # Distribute remaining squares by largest remainder
        if remaining > 0:
            # Sort by fractional remainder descending
            indexed = [(i, a[2]) for i, a in enumerate(allocated)]
            indexed.sort(key=lambda x: -x[1])
            for j in range(min(remaining, len(indexed))):
                i = indexed[j][0]
                cat, count, frac = allocated[i]
                allocated[i] = (cat, count + 1, frac)
        elif remaining < 0:
            # Remove squares from those with smallest remainder
            indexed = [(i, a[2]) for i, a in enumerate(allocated) if a[1] > 1]
            indexed.sort(key=lambda x: x[1])
            for j in range(min(-remaining, len(indexed))):
                i = indexed[j][0]
                cat, count, frac = allocated[i]
                allocated[i] = (cat, count - 1, frac)

        # Build flat list of squares
        squares = []
        for cat, count, _ in allocated:
            for _ in range(count):
                squares.append(cat)

        return squares

    # Collect all categories that appear across all agents for the legend
    all_cats_used = set()
    for agent in AGENTS:
        if agent in agent_averages:
            for cat, val in agent_averages[agent]["avg_categories"].items():
                if val > 0:
                    all_cats_used.add(cat)

    legend_cats = [c for c in CATEGORIES if c in all_cats_used]

    # Build HTML
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SWE Tasks - Average Token Distribution (Waffle Charts)</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: #f5f5f5;
    color: #333;
    padding: 32px;
  }
  h1 {
    text-align: center;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #222;
  }
  .subtitle {
    text-align: center;
    font-size: 14px;
    color: #666;
    margin-bottom: 28px;
  }
  .legend {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 12px 20px;
    margin-bottom: 32px;
    padding: 16px 24px;
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    max-width: 1100px;
    margin-left: auto;
    margin-right: auto;
  }
  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 500;
    color: #444;
    white-space: nowrap;
  }
  .legend-swatch {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    flex-shrink: 0;
  }
  .charts-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 24px;
    max-width: 1400px;
    margin: 0 auto;
  }
  .chart-card {
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 20px 24px 24px;
    width: 320px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }
  .chart-title {
    font-size: 15px;
    font-weight: 600;
    margin-bottom: 6px;
    color: #222;
  }
  .chart-stats {
    font-size: 12px;
    color: #888;
    margin-bottom: 14px;
    line-height: 1.6;
  }
  .chart-stats span {
    display: inline-block;
    margin-right: 12px;
  }
  .chart-stats .stat-value {
    font-weight: 600;
    color: #555;
  }
  .waffle-grid {
    display: grid;
    grid-template-columns: repeat(10, 24px);
    gap: 2px;
  }
  .waffle-cell {
    width: 24px;
    height: 24px;
    border-radius: 3px;
    cursor: default;
    position: relative;
  }
  .waffle-cell:hover {
    outline: 2px solid #333;
    outline-offset: 0px;
    z-index: 1;
  }
  .waffle-cell[title] {
    cursor: help;
  }
  .breakdown {
    margin-top: 14px;
    font-size: 11px;
    color: #666;
    line-height: 1.8;
  }
  .breakdown-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .breakdown-swatch {
    width: 10px;
    height: 10px;
    border-radius: 2px;
    flex-shrink: 0;
  }
  .breakdown-label {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .breakdown-value {
    font-weight: 600;
    color: #444;
    white-space: nowrap;
  }
</style>
</head>
<body>
<h1>SWE Tasks: Average Token Distribution by Agent</h1>
<p class="subtitle">Each square represents ~1% of total average tokens. Hover for category details.</p>
""")

    # Legend
    html_parts.append('<div class="legend">\n')
    for cat in legend_cats:
        label = cat.upper()
        color = COLORS.get(cat, "#ccc")
        html_parts.append(f'  <div class="legend-item"><div class="legend-swatch" style="background:{color}"></div>{label}</div>\n')
    html_parts.append('</div>\n\n')

    # Charts
    html_parts.append('<div class="charts-container">\n')
    for agent in AGENTS:
        if agent not in agent_averages:
            continue
        avg = agent_averages[agent]
        avg_cats = avg["avg_categories"]
        avg_total = avg["avg_total_tokens"]
        avg_turns = avg["avg_turn_count"]
        avg_msgs = avg["avg_message_count"]
        valid_n = avg["valid_task_count"]

        squares = compute_waffle(avg_cats, avg_total)

        label = AGENT_LABELS.get(agent, agent)

        html_parts.append(f'<div class="chart-card">\n')
        html_parts.append(f'  <div class="chart-title">{label}</div>\n')
        html_parts.append(f'  <div class="chart-stats">\n')
        html_parts.append(f'    <span>Avg tokens: <span class="stat-value">{avg_total:,.0f}</span></span>\n')
        html_parts.append(f'    <span>Avg turns: <span class="stat-value">{avg_turns:.1f}</span></span>\n')
        html_parts.append(f'    <span>Avg messages: <span class="stat-value">{avg_msgs:.1f}</span></span>\n')
        html_parts.append(f'    <br><span>Valid tasks: <span class="stat-value">{valid_n}/10</span></span>\n')
        html_parts.append(f'  </div>\n')

        # Waffle grid
        html_parts.append(f'  <div class="waffle-grid">\n')
        for sq in squares:
            color = COLORS.get(sq, "#ccc")
            pct = (avg_cats.get(sq, 0) / avg_total * 100) if avg_total > 0 else 0
            title = f"{sq.upper()}: {avg_cats.get(sq, 0):,.0f} tokens ({pct:.1f}%)"
            html_parts.append(f'    <div class="waffle-cell" style="background:{color}" title="{title}"></div>\n')
        html_parts.append(f'  </div>\n')

        # Breakdown list
        html_parts.append(f'  <div class="breakdown">\n')
        # Sort categories by token count descending
        sorted_cats = sorted(
            [(cat, avg_cats.get(cat, 0)) for cat in CATEGORIES if avg_cats.get(cat, 0) > 0],
            key=lambda x: -x[1]
        )
        for cat, val in sorted_cats:
            color = COLORS.get(cat, "#ccc")
            pct = (val / avg_total * 100) if avg_total > 0 else 0
            html_parts.append(f'    <div class="breakdown-item">')
            html_parts.append(f'<div class="breakdown-swatch" style="background:{color}"></div>')
            html_parts.append(f'<span class="breakdown-label">{cat.upper()}</span>')
            html_parts.append(f'<span class="breakdown-value">{val:,.0f} ({pct:.1f}%)</span>')
            html_parts.append(f'</div>\n')
        html_parts.append(f'  </div>\n')

        html_parts.append(f'</div>\n\n')

    html_parts.append('</div>\n')

    html_parts.append("""
</body>
</html>
""")

    html = "".join(html_parts)
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"\nHTML written to {OUTPUT_FILE}")
    print(f"File size: {len(html):,} bytes")


if __name__ == "__main__":
    main()
