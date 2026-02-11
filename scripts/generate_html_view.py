#!/usr/bin/env python3
"""
Generate an HTML viewer for annotated prompt files with filtering capabilities.
"""

import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
import html

@dataclass
class AnnotatedSentence:
    text: str
    is_fighting: bool
    signals: List[str]
    source_file: str
    paragraph_index: int
    notes: str = ""

def parse_annotated_markdown(filepath: Path) -> List[AnnotatedSentence]:
    """Parse an annotated markdown file and extract sentences with annotations."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    source_file = filepath.stem.replace('_annotated', '')
    sentences = []

    # Split by the --- separator
    blocks = re.split(r'\n---\n', content)

    paragraph_index = 0
    for block in blocks:
        block = block.strip()
        if not block or block.startswith('# Annotated:') or block.startswith('## Summary'):
            continue

        # Check if this block has an annotation
        is_fighting = False
        signals = []
        notes = ""
        text_content = block

        # Parse annotation header
        fighting_match = re.match(r'\*\*\[FIGHTING: ([^\]]+)\]\*\*', block)
        not_fighting_match = re.match(r'\*\*\[NOT FIGHTING\]\*\*', block)

        if fighting_match:
            is_fighting = True
            signals = [s.strip() for s in fighting_match.group(1).split(',')]
            # Get notes (italic text after the header)
            notes_match = re.search(r'\*\*\]\*\*\n\*([^*]+)\*', block)
            if notes_match:
                notes = notes_match.group(1).strip()
            # Get the actual text content (after the annotation)
            text_start = block.find('\n\n')
            if text_start != -1:
                text_content = block[text_start:].strip()
            else:
                # Try finding after the notes
                parts = re.split(r'\n\*[^*]+\*\n', block, maxsplit=1)
                if len(parts) > 1:
                    text_content = parts[1].strip()
                else:
                    text_content = re.sub(r'\*\*\[FIGHTING:[^\]]+\]\*\*\n?', '', block).strip()
        elif not_fighting_match:
            is_fighting = False
            signals = []
            # Get notes if any
            notes_match = re.search(r'\*\*\]\*\*\n\*([^*]+)\*', block)
            if notes_match:
                notes = notes_match.group(1).strip()
            # Get the actual text content
            text_start = block.find('\n\n')
            if text_start != -1:
                text_content = block[text_start:].strip()
            else:
                parts = re.split(r'\n\*[^*]+\*\n', block, maxsplit=1)
                if len(parts) > 1:
                    text_content = parts[1].strip()
                else:
                    text_content = re.sub(r'\*\*\[NOT FIGHTING\]\*\*\n?', '', block).strip()
        else:
            # No annotation found, skip
            continue

        # Clean up the text content
        text_content = re.sub(r'^\*\*\[[^\]]+\]\*\*\s*', '', text_content)
        text_content = re.sub(r'^\*[^*]+\*\s*', '', text_content)

        if not text_content.strip():
            continue

        # Split into sentences
        # Handle code blocks specially - don't split them
        if '```' in text_content or text_content.startswith('//') or text_content.startswith('type '):
            # This is code or a code block - keep as single unit
            sentences.append(AnnotatedSentence(
                text=text_content,
                is_fighting=is_fighting,
                signals=signals,
                source_file=source_file,
                paragraph_index=paragraph_index,
                notes=notes
            ))
        else:
            # Split into sentences, being careful with abbreviations
            # First, protect common abbreviations
            protected = text_content
            protected = re.sub(r'(e\.g\.)', 'E_G_PROTECTED', protected)
            protected = re.sub(r'(i\.e\.)', 'I_E_PROTECTED', protected)
            protected = re.sub(r'(etc\.)', 'ETC_PROTECTED', protected)
            protected = re.sub(r'(vs\.)', 'VS_PROTECTED', protected)

            # Split on sentence boundaries
            sentence_texts = re.split(r'(?<=[.!?])\s+(?=[A-Z*\-])', protected)

            for sent_text in sentence_texts:
                # Restore protected abbreviations
                sent_text = sent_text.replace('E_G_PROTECTED', 'e.g.')
                sent_text = sent_text.replace('I_E_PROTECTED', 'i.e.')
                sent_text = sent_text.replace('ETC_PROTECTED', 'etc.')
                sent_text = sent_text.replace('VS_PROTECTED', 'vs.')
                sent_text = sent_text.strip()

                if sent_text:
                    sentences.append(AnnotatedSentence(
                        text=sent_text,
                        is_fighting=is_fighting,
                        signals=signals,
                        source_file=source_file,
                        paragraph_index=paragraph_index,
                        notes=notes
                    ))

        paragraph_index += 1

    return sentences

def generate_html(all_sentences: List[AnnotatedSentence], output_path: Path):
    """Generate the HTML viewer."""

    # Collect all unique signals and sources
    all_signals = set()
    all_sources = set()
    for s in all_sentences:
        all_signals.update(s.signals)
        all_sources.add(s.source_file)

    all_signals = sorted(all_signals)
    all_sources = sorted(all_sources)

    # Signal descriptions
    signal_names = {
        'A_reminders': 'Reminders/Nagging',
        'B_repetition': 'Repetition/Reiteration',
        'C_prohibitions': 'Negative Prohibitions',
        'D_forceful': 'Forceful/Imperative',
        'E_shouting': 'Shouting/Emphasis',
        'F_threats_pleading': 'Threats/Pleading',
        'G_overconstrained': 'Over-constraining Output'
    }

    # Source display names
    source_names = {
        'anthropic-claude-code_na_2025-11-01': 'Anthropic Claude Code',
        'cursor-agent-cli_na_2025-08-07': 'Cursor Agent CLI',
        'google-gemini-cli-official_latest_current': 'Google Gemini CLI',
        'moonshot-kimi-cli-official_latest_current': 'Moonshot Kimi CLI',
        'openai-codex-cli_na_2025-09-24': 'OpenAI Codex CLI',
        'openhands-official_latest_current': 'OpenHands'
    }

    # Color scheme for signals
    signal_colors = {
        'A_reminders': '#f39c12',
        'B_repetition': '#9b59b6',
        'C_prohibitions': '#e74c3c',
        'D_forceful': '#e67e22',
        'E_shouting': '#c0392b',
        'F_threats_pleading': '#8e44ad',
        'G_overconstrained': '#d35400'
    }

    # Build sentences JSON
    sentences_json = []
    for s in all_sentences:
        sentences_json.append({
            'text': s.text,
            'is_fighting': s.is_fighting,
            'signals': s.signals,
            'source': s.source_file,
            'paragraph': s.paragraph_index,
            'notes': s.notes
        })

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weight-Fighting Signal Viewer</title>
    <style>
        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}

        h1 {{
            margin: 0 0 20px 0;
            font-size: 24px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .filters {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .filter-section {{
            margin-bottom: 15px;
        }}

        .filter-section:last-child {{
            margin-bottom: 0;
        }}

        .filter-section h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .filter-buttons {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .filter-btn {{
            padding: 6px 12px;
            border: 2px solid #ddd;
            border-radius: 20px;
            background: white;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }}

        .filter-btn:hover {{
            border-color: #999;
        }}

        .filter-btn.active {{
            background: #333;
            color: white;
            border-color: #333;
        }}

        .filter-btn.signal {{
            border-left-width: 4px;
        }}

        .stats {{
            background: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            font-size: 14px;
            color: #666;
        }}

        .stats strong {{
            color: #333;
        }}

        .sentences {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .sentence {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid #ddd;
        }}

        .sentence.fighting {{
            border-left-color: #e74c3c;
        }}

        .sentence.not-fighting {{
            border-left-color: #27ae60;
        }}

        .sentence-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 8px;
            gap: 10px;
        }}

        .sentence-source {{
            font-size: 12px;
            color: #888;
            flex-shrink: 0;
        }}

        .sentence-signals {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }}

        .signal-tag {{
            font-size: 10px;
            padding: 2px 8px;
            border-radius: 10px;
            background: #fee;
            color: #c00;
            font-weight: 500;
        }}

        .sentence-text {{
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-break: break-word;
        }}

        .sentence-text code {{
            background: #f0f0f0;
            padding: 1px 4px;
            border-radius: 3px;
            font-size: 13px;
        }}

        .sentence-notes {{
            margin-top: 8px;
            font-size: 12px;
            color: #666;
            font-style: italic;
        }}

        .hidden {{
            display: none !important;
        }}

        .toggle-group {{
            display: flex;
            gap: 0;
            border-radius: 20px;
            overflow: hidden;
            border: 2px solid #ddd;
        }}

        .toggle-btn {{
            padding: 6px 16px;
            border: none;
            background: white;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }}

        .toggle-btn:not(:last-child) {{
            border-right: 1px solid #ddd;
        }}

        .toggle-btn.active {{
            background: #333;
            color: white;
        }}

        .toggle-btn:hover:not(.active) {{
            background: #f0f0f0;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}

            .sentence-header {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Weight-Fighting Signal Analysis</h1>

        <div class="filters">
            <div class="filter-section">
                <h3>Show</h3>
                <div class="toggle-group">
                    <button class="toggle-btn active" data-filter="all">All</button>
                    <button class="toggle-btn" data-filter="fighting">Fighting Only</button>
                    <button class="toggle-btn" data-filter="not-fighting">Not Fighting Only</button>
                </div>
            </div>

            <div class="filter-section">
                <h3>Sources</h3>
                <div class="filter-buttons" id="source-filters">
                    <button class="filter-btn active" data-source="all">All Sources</button>
                    {''.join(f'<button class="filter-btn" data-source="{src}">{source_names.get(src, src)}</button>' for src in all_sources)}
                </div>
            </div>

            <div class="filter-section">
                <h3>Signal Types</h3>
                <div class="filter-buttons" id="signal-filters">
                    <button class="filter-btn active" data-signal="all">All Signals</button>
                    {''.join(f'<button class="filter-btn signal" data-signal="{sig}" style="border-left-color: {signal_colors.get(sig, "#999")}">{signal_names.get(sig, sig)}</button>' for sig in all_signals)}
                </div>
            </div>
        </div>

        <div class="stats" id="stats">
            Loading...
        </div>

        <div class="sentences" id="sentences">
        </div>
    </div>

    <script>
        const sentences = {json.dumps(sentences_json, ensure_ascii=False)};

        const signalNames = {json.dumps(signal_names, ensure_ascii=False)};
        const sourceNames = {json.dumps(source_names, ensure_ascii=False)};
        const signalColors = {json.dumps(signal_colors, ensure_ascii=False)};

        let filters = {{
            fighting: 'all',
            source: 'all',
            signal: 'all'
        }};

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        function highlightSignals(text, signals) {{
            if (!signals.length) return escapeHtml(text);

            let result = escapeHtml(text);

            // Highlight patterns associated with signals
            const patterns = {{
                'E_shouting': /\\b[A-Z]{{2,}}\\b/g,
                'C_prohibitions': /\\b(do not|don't|never|avoid|stop|refrain)\\b/gi,
                'D_forceful': /\\b(must|always|required|critical|important|strictly|essential)\\b/gi,
                'A_reminders': /\\b(remember|don't forget|note that|keep in mind|reminder)\\b/gi,
            }};

            signals.forEach(sig => {{
                if (patterns[sig]) {{
                    const color = signalColors[sig] || '#e74c3c';
                    result = result.replace(patterns[sig], match =>
                        `<mark style="background: ${{color}}22; color: ${{color}}; padding: 0 2px; border-radius: 2px;">${{match}}</mark>`
                    );
                }}
            }});

            return result;
        }}

        function renderSentences() {{
            const container = document.getElementById('sentences');
            const filtered = sentences.filter(s => {{
                if (filters.fighting === 'fighting' && !s.is_fighting) return false;
                if (filters.fighting === 'not-fighting' && s.is_fighting) return false;
                if (filters.source !== 'all' && s.source !== filters.source) return false;
                if (filters.signal !== 'all' && !s.signals.includes(filters.signal)) return false;
                return true;
            }});

            // Update stats
            const fightingCount = filtered.filter(s => s.is_fighting).length;
            const totalCount = filtered.length;
            document.getElementById('stats').innerHTML = `
                Showing <strong>${{totalCount}}</strong> sentences
                (<strong>${{fightingCount}}</strong> fighting,
                <strong>${{totalCount - fightingCount}}</strong> not fighting)
            `;

            container.innerHTML = filtered.map(s => `
                <div class="sentence ${{s.is_fighting ? 'fighting' : 'not-fighting'}}">
                    <div class="sentence-header">
                        <div class="sentence-signals">
                            ${{s.signals.map(sig => `
                                <span class="signal-tag" style="background: ${{signalColors[sig] || '#fee'}}22; color: ${{signalColors[sig] || '#c00'}}">
                                    ${{signalNames[sig] || sig}}
                                </span>
                            `).join('')}}
                            ${{!s.is_fighting ? '<span class="signal-tag" style="background: #e8f5e9; color: #27ae60;">Not Fighting</span>' : ''}}
                        </div>
                        <div class="sentence-source">${{sourceNames[s.source] || s.source}}</div>
                    </div>
                    <div class="sentence-text">${{highlightSignals(s.text, s.signals)}}</div>
                    ${{s.notes ? `<div class="sentence-notes">${{escapeHtml(s.notes)}}</div>` : ''}}
                </div>
            `).join('');
        }}

        // Set up filter buttons
        document.querySelectorAll('.toggle-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                filters.fighting = btn.dataset.filter;
                renderSentences();
            }});
        }});

        document.querySelectorAll('#source-filters .filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('#source-filters .filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                filters.source = btn.dataset.source;
                renderSentences();
            }});
        }});

        document.querySelectorAll('#signal-filters .filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('#signal-filters .filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                filters.signal = btn.dataset.signal;
                renderSentences();
            }});
        }});

        // Initial render
        renderSentences();
    </script>
</body>
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    annotated_dir = Path("/Users/srihari/work/nilenso/long-prompts-analysis/data/prompts/annotated")
    output_path = Path("/Users/srihari/work/nilenso/long-prompts-analysis/data/prompts/viewer.html")

    all_sentences = []

    # Process each annotated markdown file
    for md_file in annotated_dir.glob("*_annotated.md"):
        print(f"Processing: {md_file.name}")
        sentences = parse_annotated_markdown(md_file)
        all_sentences.extend(sentences)
        print(f"  - Extracted {len(sentences)} sentences")

    print(f"\nTotal sentences: {len(all_sentences)}")
    print(f"Fighting: {sum(1 for s in all_sentences if s.is_fighting)}")
    print(f"Not fighting: {sum(1 for s in all_sentences if not s.is_fighting)}")

    generate_html(all_sentences, output_path)
    print(f"\nHTML viewer generated: {output_path}")


if __name__ == "__main__":
    main()
