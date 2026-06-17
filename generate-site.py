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
            <span style="color: var(--text-muted); margin: 0 8px;">/</span>
            <span style="color: var(--text-muted);">{date_display}</span>
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
    
    <a href="#" class="back-to-top" id="backToTop" title="Back to top">↑</a>
    <script>
        const backToTop = document.getElementById('backToTop');
        window.addEventListener('scroll', () => {{
            if (window.scrollY > 400) {{
                backToTop.classList.add('visible');
            }} else {{
                backToTop.classList.remove('visible');
            }}
        }});
        backToTop.addEventListener('click', (e) => {{
            e.preventDefault();
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});
    </script>
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
    --bg: #0a0a0e;
    --surface: #14141a;
    --surface-hover: #1e1e26;
    --text: #e6e6ed;
    --text-secondary: #a0a0b0;
    --text-muted: #6e6e80;
    --accent: #7c6cf1;
    --accent-hover: #a599f7;
    --accent-bg: rgba(124, 108, 241, 0.1);
    --border: #2a2a35;
    --border-light: #3a3a48;
    --radius: 12px;
    --radius-sm: 8px;
    --warning: #f59e0b;
    --success: #22c55e;
    --shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
    --shadow-hover: 0 8px 32px rgba(0, 0, 0, 0.5);
    --font-body: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    --font-mono: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--font-body);
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    font-size: 15px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 24px;
}

/* Header */
header {
    padding: 40px 0 28px;
    border-bottom: 1px solid var(--border);
    background: linear-gradient(180deg, var(--surface) 0%, var(--bg) 100%);
}

header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.5px;
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
    margin-top: 6px;
    font-size: 0.95rem;
}

/* Breadcrumb */
.breadcrumb {
    padding: 14px 0;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    position: sticky;
    top: 0;
    z-index: 100;
}

.breadcrumb a {
    color: var(--accent);
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.breadcrumb a:hover {
    color: var(--accent-hover);
}

/* Digest Header */
.digest-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 32px 0 24px;
    flex-wrap: wrap;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
}

.digest-header h2 {
    font-size: 1.7rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    background: var(--warning);
    color: #000;
}

.status-ok {
    background: var(--success);
    color: #fff;
}

/* Section Headers */
.section-header {
    font-size: 1.2rem;
    font-weight: 700;
    margin: 40px 0 20px;
    padding: 8px 0;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 2px solid var(--accent);
    display: inline-block;
}

/* Entry Cards */
.entry-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 16px;
    transition: all 0.3s ease;
    box-shadow: var(--shadow);
}

.entry-card:hover {
    border-color: var(--border-light);
    box-shadow: var(--shadow-hover);
    transform: translateY(-1px);
}

.entry-card h3 {
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--text);
    line-height: 1.4;
}

/* Builder Tag */
.builder-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: var(--accent-bg);
    color: var(--accent);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 12px;
}

/* Summary (English) */
.entry-card .summary {
    color: var(--text-secondary);
    margin-bottom: 14px;
    line-height: 1.7;
    font-size: 0.95rem;
}

/* Chinese Summary */
.entry-card .cn-summary {
    color: var(--text-secondary);
    border-left: 3px solid var(--accent);
    padding-left: 16px;
    margin-bottom: 16px;
    line-height: 1.8;
    font-size: 0.95rem;
}

/* Links */
.entry-card .links {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
}

.entry-card .links a {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--accent);
    text-decoration: none;
    font-size: 0.85rem;
    font-family: var(--font-mono);
    background: var(--accent-bg);
    padding: 6px 12px;
    border-radius: var(--radius-sm);
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: all 0.2s ease;
}

.entry-card .links a::before {
    content: "↗";
    font-size: 0.8rem;
    opacity: 0.7;
    flex-shrink: 0;
}

.entry-card .links a:hover {
    background: var(--accent);
    color: var(--bg);
    white-space: normal;
    word-break: break-all;
}

/* Podcast Cards */
.podcast-card .takeaway {
    background: var(--bg);
    border-radius: var(--radius-sm);
    padding: 16px;
    margin: 12px 0;
    font-style: italic;
    color: var(--text-secondary);
    border-left: 3px solid var(--accent);
}

.podcast-card .cn-takeaway {
    color: var(--text-muted);
    border-left: 3px solid var(--accent);
    padding-left: 16px;
    margin-top: 8px;
}

/* Index Page */
.latest {
    margin: 32px 0 48px;
}

.latest h2 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
}

.digest-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
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
    transition: all 0.3s ease;
    box-shadow: var(--shadow);
}

.digest-card:hover {
    background: var(--surface-hover);
    border-color: var(--accent);
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}

.digest-card .date {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 8px;
    color: var(--accent-hover);
}

.digest-card .preview {
    color: var(--text-muted);
    font-size: 0.85rem;
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.latest-card {
    background: var(--surface);
    border: 2px solid var(--accent);
    border-radius: var(--radius);
    padding: 28px;
    display: block;
    text-decoration: none;
    color: var(--text);
    transition: all 0.3s ease;
    box-shadow: var(--shadow);
}

.latest-card:hover {
    background: var(--surface-hover);
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}

.latest-card .date {
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 12px;
    color: var(--accent-hover);
}

.latest-card .preview {
    color: var(--text-secondary);
    line-height: 1.6;
    font-size: 0.95rem;
}

/* Footer */
footer {
    margin-top: 60px;
    padding: 32px 0;
    border-top: 1px solid var(--border);
    text-align: center;
    color: var(--text-muted);
    font-size: 0.85rem;
}

footer a {
    color: var(--accent);
    text-decoration: none;
}

footer a:hover {
    text-decoration: underline;
}

/* Back to Top Button */
.back-to-top {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 44px;
    height: 44px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    box-shadow: var(--shadow);
    z-index: 999;
    color: var(--accent);
    font-size: 1.2rem;
    text-decoration: none;
}

.back-to-top.visible {
    opacity: 1;
    visibility: visible;
}

.back-to-top:hover {
    background: var(--accent);
    color: var(--bg);
    border-color: var(--accent);
    transform: translateY(-2px);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg);
}

::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--border-light);
}

/* Responsive */
@media (max-width: 640px) {
    .container { padding: 0 16px; }
    header { padding: 28px 0 20px; }
    header h1 { font-size: 1.4rem; }
    .digest-grid { grid-template-columns: 1fr; gap: 12px; }
    .entry-card { padding: 18px; margin-bottom: 12px; }
    .entry-card h3 { font-size: 1.05rem; }
    .digest-header h2 { font-size: 1.4rem; }
    .latest-card { padding: 20px; }
    .latest-card .date { font-size: 1.1rem; }
    .section-header { font-size: 1.05rem; }
}

/* Selection */
::selection {
    background: var(--accent);
    color: var(--bg);
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
            
            links = re.findall(r'https?://\S+', entry_content)
            
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
