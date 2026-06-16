#!/usr/bin/env python3
"""
AI Builders Digest Static Site Generator
Converts markdown digest files to a clean HTML website
"""

import os
import re
import glob
from datetime import datetime
from pathlib import Path

# Site configuration
SITE_TITLE = "AI Builders Digest"
SITE_DESCRIPTION = "Daily AI builder insights from X/Twitter, podcasts, and blogs"
OUTPUT_DIR = "site"
INPUT_DIR = "/root/.openclaw/workspace/obsidian-sync-local"

# HTML template for individual digest pages
DIGEST_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — {site_title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1><a href="index.html">{site_title}</a></h1>
            <p class="subtitle">{site_description}</p>
        </div>
    </header>
    
    <nav class="breadcrumb">
        <div class="container">
            <a href="index.html">← All Digests</a>
        </div>
    </nav>

    <main class="container">
        <div class="digest-header">
            <h2>{date_display}</h2>
            {status_badge}
        </div>
        
        <div class="digest-content">
            {content}
        </div>
    </main>

    <footer>
        <div class="container">
            <p>Generated from Follow Builders skill</p>
            <p><a href="https://github.com/zarazhangrui/follow-builders" target="_blank">View Source</a></p>
        </div>
    </footer>
</body>
</html>"""

# HTML template for index page
INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>{site_title}</h1>
            <p class="subtitle">{site_description}</p>
        </div>
    </header>

    <main class="container">
        <section class="latest">
            <h2>Latest Digest</h2>
            {latest_card}
        </section>

        <section class="archive">
            <h2>Archive</h2>
            <div class="digest-grid">
                {archive_cards}
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>Generated from Follow Builders skill</p>
            <p><a href="https://github.com/zarazhangrui/follow-builders" target="_blank">View Source</a></p>
        </div>
    </footer>
</body>
</html>"""

# CSS stylesheet
CSS = """:root {
    --bg: #0f0f12;
    --surface: #1a1a1f;
    --surface-hover: #222228;
    --text: #e8e8ec;
    --text-muted: #8a8a93;
    --accent: #6366f1;
    --accent-hover: #818cf8;
    --border: #2a2a30;
    --radius: 12px;
    --warning: #f59e0b;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}

.container {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 24px;
}

header {
    padding: 48px 0 32px;
    border-bottom: 1px solid var(--border);
}

header h1 a {
    color: var(--text);
    text-decoration: none;
}

header h1 a:hover {
    color: var(--accent-hover);
}

.subtitle {
    color: var(--text-muted);
    margin-top: 8px;
    font-size: 1.1rem;
}

.breadcrumb {
    padding: 16px 0;
    border-bottom: 1px solid var(--border);
}

.breadcrumb a {
    color: var(--accent);
    text-decoration: none;
}

.breadcrumb a:hover {
    color: var(--accent-hover);
}

.digest-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 32px 0 24px;
    flex-wrap: wrap;
}

.digest-header h2 {
    font-size: 1.8rem;
}

.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    background: var(--warning);
    color: #000;
}

.status-ok {
    background: #22c55e;
    color: #fff;
}

.entry-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 20px;
    transition: border-color 0.2s;
}

.entry-card:hover {
    border-color: var(--accent);
}

.entry-card h3 {
    font-size: 1.25rem;
    margin-bottom: 4px;
    color: var(--accent-hover);
}

.entry-card .meta {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-bottom: 16px;
}

.entry-card .summary {
    margin-bottom: 12px;
}

.entry-card .cn-summary {
    color: var(--text-muted);
    border-left: 3px solid var(--accent);
    padding-left: 16px;
    margin-bottom: 16px;
}

.entry-card .links {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

.entry-card .links a {
    color: var(--accent);
    text-decoration: none;
    font-size: 0.9rem;
    word-break: break-all;
}

.entry-card .links a:hover {
    text-decoration: underline;
}

.section-header {
    font-size: 1.5rem;
    margin: 40px 0 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--accent);
    display: inline-block;
}

.latest {
    margin: 32px 0;
}

.digest-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
    margin-top: 20px;
}

.digest-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    text-decoration: none;
    color: var(--text);
    display: block;
    transition: all 0.2s;
}

.digest-card:hover {
    background: var(--surface-hover);
    border-color: var(--accent);
    transform: translateY(-2px);
}

.digest-card .date {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 8px;
}

.digest-card .preview {
    color: var(--text-muted);
    font-size: 0.9rem;
    line-height: 1.5;
}

.latest-card {
    background: var(--surface);
    border: 2px solid var(--accent);
    border-radius: var(--radius);
    padding: 24px;
    display: block;
    text-decoration: none;
    color: var(--text);
    transition: all 0.2s;
}

.latest-card:hover {
    background: var(--surface-hover);
    transform: translateY(-2px);
}

.latest-card .date {
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 12px;
}

.latest-card .preview {
    color: var(--text-muted);
    line-height: 1.6;
}

footer {
    margin-top: 60px;
    padding: 32px 0;
    border-top: 1px solid var(--border);
    text-align: center;
    color: var(--text-muted);
    font-size: 0.9rem;
}

footer a {
    color: var(--accent);
    text-decoration: none;
}

footer a:hover {
    text-decoration: underline;
}

@media (max-width: 600px) {
    .container { padding: 0 16px; }
    header { padding: 32px 0 24px; }
    .digest-grid { grid-template-columns: 1fr; }
    .entry-card { padding: 16px; }
}

.podcast-card .takeaway {
    background: var(--bg);
    border-radius: 8px;
    padding: 16px;
    margin: 12px 0;
    font-style: italic;
}

.podcast-card .cn-takeaway {
    color: var(--text-muted);
    border-left: 3px solid var(--accent);
    padding-left: 16px;
    margin-top: 8px;
}"""


def has_chinese(text):
    """Check if text contains Chinese characters (CJK range)"""
    for c in text:
        if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf' or '\u3000' <= c <= '\u303f':
            return True
    return False


def parse_markdown_digest(content, filename=""):
    """Parse markdown digest into structured entries"""
    entries = []
    
    # Extract date from title or filename
    date_match = re.search(r'# AI Builders Digest[\s—]+(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        date_str = date_match.group(1)
    else:
        date_match = re.search(r'digest-(\d{4}-\d{2}-\d{2})', filename)
        date_str = date_match.group(1) if date_match else ""
    
    has_stale_warning = '⚠️' in content or 'stale' in content.lower() or '较旧' in content
    
    sections = re.split(r'\n##\s+', content)
    
    for section in sections[1:]:
        lines = section.strip().split('\n')
        section_title = lines[0].strip()
        section_content = '\n'.join(lines[1:])
        entry_blocks = re.split(r'\n###\s+', section_content)
        
        for entry in entry_blocks[1:] if entry_blocks[0].strip() == '' else entry_blocks:
            if not entry.strip():
                continue
                
            entry_lines = entry.strip().split('\n')
            entry_title = entry_lines[0].strip()
            
            entry_content = '\n'.join(entry_lines[1:])
            entry_content = re.sub(r'^---+\n?', '', entry_content.strip())
            
            links = re.findall(r'- (https?://\S+)', entry_content)
            
            paragraphs = [p.strip() for p in entry_content.split('\n\n') if p.strip()]
            
            en_summary = ""
            cn_summary = ""
            
            for p in paragraphs:
                if p.startswith('- http') or p.startswith('---') or p.startswith('Generated at:'):
                    continue
                if has_chinese(p):
                    cn_summary = p
                else:
                    en_summary = p
            
            en_summary = re.sub(r'\n+', ' ', en_summary).strip()
            cn_summary = re.sub(r'\n+', ' ', cn_summary).strip()
            
            entries.append({
                'section': section_title,
                'title': entry_title,
                'en_summary': en_summary,
                'cn_summary': cn_summary,
                'links': links
            })
    
    return {
        'date': date_str,
        'has_stale_warning': has_stale_warning,
        'entries': entries
    }


def generate_digest_html(parsed):
    """Generate HTML for a single digest page"""
    date = parsed['date']
    date_display = datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y') if date else "Unknown Date"
    
    status_badge = '<span class="status-badge">⚠️ Stale Data</span>' if parsed['has_stale_warning'] else '<span class="status-badge status-ok">✓ Fresh</span>'
    
    sections = {}
    for entry in parsed['entries']:
        sec = entry['section']
        if sec not in sections:
            sections[sec] = []
        sections[sec].append(entry)
    
    content_html = ""
    for section_name, entries in sections.items():
        section_id = section_name.lower().replace('/', '-').replace(' ', '-')
        content_html += f'<h2 class="section-header" id="{section_id}">{section_name}</h2>\n'
        
        for entry in entries:
            is_podcast = 'podcast' in section_name.lower()
            card_class = 'entry-card podcast-card' if is_podcast else 'entry-card'
            
            content_html += f'<div class="{card_class}">\n'
            content_html += f'<h3>{entry["title"]}</h3>\n'
            
            if entry['en_summary']:
                if is_podcast and ('Takeaway' in entry['en_summary'] or '核心要点' in entry['cn_summary']):
                    content_html += f'<div class="takeaway">{entry["en_summary"]}</div>\n'
                else:
                    content_html += f'<div class="summary">{entry["en_summary"]}</div>\n'
            
            if entry['cn_summary']:
                if is_podcast and '核心要点' in entry['cn_summary']:
                    content_html += f'<div class="cn-takeaway">{entry["cn_summary"]}</div>\n'
                else:
                    content_html += f'<div class="cn-summary">{entry["cn_summary"]}</div>\n'
            
            if entry['links']:
                content_html += '<div class="links">\n'
                for link in entry['links']:
                    content_html += f'<a href="{link}" target="_blank">{link}</a>\n'
                content_html += '</div>\n'
            
            content_html += '</div>\n'
    
    return DIGEST_TEMPLATE.format(
        title=f"Digest {date}",
        site_title=SITE_TITLE,
        site_description=SITE_DESCRIPTION,
        date_display=date_display,
        status_badge=status_badge,
        content=content_html
    )


def generate_index_page(digests):
    """Generate the index page"""
    latest = digests[-1] if digests else None
    
    if latest:
        latest_date = latest['date']
        latest_display = datetime.strptime(latest_date, '%Y-%m-%d').strftime('%B %d, %Y')
        preview_entries = [e['title'] for e in latest['entries'][:4]]
        preview = ' • '.join(preview_entries) if preview_entries else "Latest AI builder insights"
        
        latest_card = f'''<a href="digest-{latest_date}.html" class="latest-card">
            <div class="date">{latest_display}</div>
            <div class="preview">{preview}</div>
        </a>'''
    else:
        latest_card = '<p>No digests available</p>'
    
    archive_cards = ""
    for digest in reversed(digests[:-1] if latest else digests):
        date = digest['date']
        display = datetime.strptime(date, '%Y-%m-%d').strftime('%b %d, %Y')
        preview_entries = [e['title'] for e in digest['entries'][:3]]
        preview = ' • '.join(preview_entries) if preview_entries else "AI builder insights"
        
        archive_cards += f'''<a href="digest-{date}.html" class="digest-card">
            <div class="date">{display}</div>
            <div class="preview">{preview}</div>
        </a>'''
    
    return INDEX_TEMPLATE.format(
        site_title=SITE_TITLE,
        site_description=SITE_DESCRIPTION,
        latest_card=latest_card,
        archive_cards=archive_cards
    )


def main():
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    
    digest_files = sorted(glob.glob(os.path.join(INPUT_DIR, "digest-2026-*.md")))
    print(f"Found {len(digest_files)} digest files")
    
    digests = []
    for filepath in digest_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parsed = parse_markdown_digest(content, os.path.basename(filepath))
        if parsed['date']:
            digests.append(parsed)
            html = generate_digest_html(parsed)
            output_file = output_path / f"digest-{parsed['date']}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"Generated: {output_file}")
    
    index_html = generate_index_page(digests)
    with open(output_path / "index.html", 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"Generated: {output_path}/index.html")
    
    with open(output_path / "style.css", 'w', encoding='utf-8') as f:
        f.write(CSS)
    print(f"Generated: {output_path}/style.css")
    
    print(f"\nSite generated successfully in {OUTPUT_DIR}/")
    print(f"Total pages: {len(digests) + 1}")


if __name__ == '__main__':
    main()
