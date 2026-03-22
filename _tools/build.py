#!/usr/bin/env python3
"""
Static site generator: converts _blog/*.md -> blog/*.html
No external dependencies required.
"""

import re
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
SRC_DIR = os.path.join(ROOT, '_blog')
OUT_DIR = os.path.join(ROOT, 'blog')


def md_to_html(md: str) -> str:
    # Escape HTML entities
    html = md.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # Fenced code blocks (protect from further processing)
    code_blocks = []

    def save_code_block(m):
        lang = m.group(1)
        code = m.group(2).rstrip()
        cls = f' class="language-{lang}"' if lang else ''
        placeholder = f'\x00CODE{len(code_blocks)}\x00'
        code_blocks.append(f'<pre><code{cls}>{code}</code></pre>')
        return placeholder

    html = re.sub(r'```(\w*)\n([\s\S]*?)```', save_code_block, html)

    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # Headings
    for level in range(6, 0, -1):
        pattern = r'^{} (.+)$'.format('#' * level)
        html = re.sub(pattern, r'<h{0}>\1</h{0}>'.format(level), html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', html)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Images before links
    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img alt="\1" src="\2">', html)
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # Horizontal rule
    html = re.sub(r'^---$', '<hr>', html, flags=re.MULTILINE)

    # Blockquotes (already escaped as &gt;)
    html = re.sub(r'^&gt; (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

    # Unordered lists
    def replace_ul(m):
        items = '\n'.join(
            f'  <li>{re.sub(r"^[-*] ", "", line)}</li>'
            for line in m.group(0).strip().splitlines()
        )
        return f'<ul>\n{items}\n</ul>'

    html = re.sub(r'((?:^[-*] .+\n?)+)', replace_ul, html, flags=re.MULTILINE)

    # Ordered lists
    def replace_ol(m):
        items = '\n'.join(
            f'  <li>{re.sub(r"^\d+\. ", "", line)}</li>'
            for line in m.group(0).strip().splitlines()
        )
        return f'<ol>\n{items}\n</ol>'

    html = re.sub(r'((?:^\d+\. .+\n?)+)', replace_ol, html, flags=re.MULTILINE)

    # Paragraphs: wrap non-block, non-empty lines
    BLOCK_TAGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li',
                  'pre', 'blockquote', 'hr', 'img', 'p', '\x00')
    lines = html.splitlines()
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append('')
        elif any(stripped.startswith(f'<{t}') or stripped.startswith(t) for t in BLOCK_TAGS):
            result.append(line)
        else:
            result.append(f'<p>{line}</p>')
    html = '\n'.join(result)

    # Restore code blocks
    for i, block in enumerate(code_blocks):
        html = html.replace(f'\x00CODE{i}\x00', block)

    return html


def extract_title(md: str) -> str:
    m = re.search(r'^# (.+)$', md, re.MULTILINE)
    return m.group(1) if m else 'Blog Post'


def build_page(title: str, body_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{ font-family: sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; }}
    pre {{ background: #f4f4f4; padding: 1rem; border-radius: 4px; overflow-x: auto; }}
    code {{ background: #f4f4f4; padding: 0.1em 0.3em; border-radius: 3px; }}
    pre code {{ background: none; padding: 0; }}
    blockquote {{ border-left: 4px solid #ccc; margin: 0; padding-left: 1rem; color: #555; }}
    img {{ max-width: 100%; }}
  </style>
</head>
<body>
{body_html}
</body>
</html>
"""


def build_index_page(posts: list) -> str:
    """Build root index.html listing all blog posts."""
    items = '\n'.join(
        f'  <li><a href="blog/{name}.html">{title}</a></li>'
        for name, title in posts
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog</title>
  <style>
    body {{ font-family: sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ margin: 0.5rem 0; }}
    a {{ text-decoration: none; color: #0066cc; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>Blog</h1>
  <ul>
{items}
  </ul>
</body>
</html>
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    files = [f for f in os.listdir(SRC_DIR) if f.endswith('.md')]
    if not files:
        print('No .md files found in _blog/')
        sys.exit(0)

    posts = []
    for filename in sorted(files):
        src = os.path.join(SRC_DIR, filename)
        name = os.path.splitext(filename)[0]
        dest = os.path.join(OUT_DIR, f'{name}.html')

        md = open(src, encoding='utf-8').read()
        title = extract_title(md)
        body = md_to_html(md)
        page = build_page(title, body)

        with open(dest, 'w', encoding='utf-8') as f:
            f.write(page)

        posts.append((name, title))
        print(f'  {filename} -> blog/{name}.html')

    index_dest = os.path.join(ROOT, 'index.html')
    with open(index_dest, 'w', encoding='utf-8') as f:
        f.write(build_index_page(posts))
    print('  index.html updated')

    print(f'Done. {len(files)} file(s) processed.')


if __name__ == '__main__':
    main()
