#!/usr/bin/env python3
"""
This script reads the links from links.json and produces an html document to display them nicely.
Minimal CSS, warm-themed.
"""

import json
import sys
from datetime import datetime
from collections import defaultdict


def load_links(json_file='links.json'):
    """Load links from JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_file} not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error reading {json_file}: {e}")
        sys.exit(1)


def get_all_tags(links):
    """Extract all unique tags from links."""
    tags = set()
    for link in links:
        tags.update(link.get('tags', []))
    return sorted(tags)


def escape_html(text):
    """Escape HTML special characters."""
    if not text:
        return ""
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def generate_html(links):
    """Generate HTML document from links."""
    all_tags = get_all_tags(links)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bookmarks</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #faf7f2;
            color: #3e2723;
            line-height: 1.6;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #d7c9b8;
        }}

        h1 {{
            color: #6d4c41;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #8d6e63;
            font-size: 1.1em;
        }}

        .search-box {{
            margin: 30px 0;
            position: sticky;
            top: 20px;
            background: #faf7f2;
            padding: 10px 0;
            z-index: 100;
        }}

        #search {{
            width: 100%;
            padding: 12px 20px;
            font-size: 16px;
            border: 2px solid #d7c9b8;
            border-radius: 8px;
            background: #fff;
            color: #3e2723;
            transition: border-color 0.3s;
        }}

        #search:focus {{
            outline: none;
            border-color: #a1887f;
        }}

        .tag-filters {{
            margin: 20px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .tag-filter {{
            padding: 6px 14px;
            background: #efebe9;
            color: #5d4037;
            border: 1px solid #d7ccc8;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s;
        }}

        .tag-filter:hover {{
            background: #d7ccc8;
        }}

        .tag-filter.active {{
            background: #a1887f;
            color: #fff;
            border-color: #8d6e63;
        }}

        .tag-section {{
            margin-bottom: 50px;
        }}

        .tag-header {{
            color: #6d4c41;
            font-size: 1.5em;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 1px solid #d7c9b8;
        }}

        .links-list {{
            list-style: none;
        }}

        .link-item {{
            padding: 12px 0;
            border-bottom: 1px solid #e8dfd0;
        }}

        .link-item:hover {{
            background: #f5f1ec;
            padding-left: 8px;
            margin-left: -8px;
            padding-right: 8px;
            margin-right: -8px;
        }}

        .link-title {{
            font-size: 1.05em;
            margin-bottom: 4px;
        }}

        .link-title a {{
            color: #bf5f3a;
            text-decoration: none;
        }}

        .link-title a:hover {{
            text-decoration: underline;
        }}

        .link-url {{
            font-size: 0.85em;
            color: #8d6e63;
            word-break: break-all;
            margin-bottom: 6px;
        }}

        .link-description {{
            color: #5d4037;
            font-size: 0.9em;
            margin-bottom: 6px;
            line-height: 1.5;
        }}

        .link-tags {{
            display: inline;
        }}

        .tag {{
            display: inline-block;
            padding: 3px 10px;
            background: #fff3e0;
            color: #e65100;
            border-radius: 12px;
            font-size: 0.8em;
            border: 1px solid #ffe0b2;
        }}

        .stats {{
            margin: 30px 0;
            padding: 20px;
            background: #efebe9;
            border-radius: 8px;
            text-align: center;
        }}

        .stats-number {{
            font-size: 2em;
            color: #6d4c41;
            font-weight: bold;
        }}

        .stats-label {{
            color: #8d6e63;
            font-size: 0.9em;
        }}

        footer {{
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #d7c9b8;
            text-align: center;
            color: #8d6e63;
            font-size: 0.9em;
        }}

        .hidden {{
            display: none;
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Bookmarks</h1>
            <p class="subtitle">Personal collection of interesting links</p>
        </header>

        <div class="stats">
            <div class="stats-number">{len(links)}</div>
            <div class="stats-label">Total Links</div>
        </div>

        <div class="search-box">
            <input type="text" id="search" placeholder="Search links by title, description, or URL...">
        </div>
"""

    # Add tag filters if there are tags
    if all_tags:
        html += '        <div class="tag-filters">\n'
        html += '            <button class="tag-filter active" data-tag="all">All</button>\n'
        for tag in all_tags:
            html += f'            <button class="tag-filter" data-tag="{escape_html(tag)}">{escape_html(tag)}</button>\n'
        html += '        </div>\n\n'

    # Add tagged sections
    for tag in all_tags:
        tag_links = tag_groups[tag]
        html += f'        <div class="tag-section" data-section-tag="{escape_html(tag)}">\n'
        html += f'            <h2 class="tag-header">{escape_html(tag)} ({len(tag_links)})</h2>\n'
        html += '            <ul class="links-list">\n'

        for link in tag_links:
            html += generate_link_item(link)

        html += '            </ul>\n'
        html += '        </div>\n\n'

    # Add untagged section
    if untagged:
        html += '        <div class="tag-section" data-section-tag="untagged">\n'
        html += f'            <h2 class="tag-header">Untagged ({len(untagged)})</h2>\n'
        html += '            <ul class="links-list">\n'

        for link in untagged:
            html += generate_link_item(link)

        html += '            </ul>\n'
        html += '        </div>\n\n'

    # Add footer and JavaScript
    html += f"""        <footer>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </footer>
    </div>

    <script>
        // Search functionality
        const searchInput = document.getElementById('search');
        const linkItems = document.querySelectorAll('.link-item');

        searchInput.addEventListener('input', function() {{
            const searchTerm = this.value.toLowerCase();

            linkItems.forEach(item => {{
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {{
                    item.classList.remove('hidden');
                }} else {{
                    item.classList.add('hidden');
                }}
            }});

            // Hide empty sections
            document.querySelectorAll('.tag-section').forEach(section => {{
                const visibleItems = section.querySelectorAll('.link-item:not(.hidden)');
                if (visibleItems.length === 0) {{
                    section.classList.add('hidden');
                }} else {{
                    section.classList.remove('hidden');
                }}
            }});
        }});

        // Tag filter functionality
        const tagFilters = document.querySelectorAll('.tag-filter');

        tagFilters.forEach(filter => {{
            filter.addEventListener('click', function() {{
                // Update active state
                tagFilters.forEach(f => f.classList.remove('active'));
                this.classList.add('active');

                const selectedTag = this.dataset.tag;

                // Show/hide sections based on selected tag
                document.querySelectorAll('.tag-section').forEach(section => {{
                    const sectionTag = section.dataset.sectionTag;

                    if (selectedTag === 'all') {{
                        section.classList.remove('hidden');
                    }} else if (sectionTag === selectedTag) {{
                        section.classList.remove('hidden');
                    }} else {{
                        section.classList.add('hidden');
                    }}
                }});

                // Clear search when filtering by tag
                searchInput.value = '';
                linkItems.forEach(item => item.classList.remove('hidden'));
            }});
        }});
    </script>
</body>
</html>"""

    return html


def generate_link_item(link):
    """Generate HTML for a single link item."""
    url = escape_html(link.get('url', ''))
    label = escape_html(link.get('label', url))
    description = escape_html(link.get('description', ''))
    tags = link.get('tags', [])

    item = '                <li class="link-item">\n'
    item += f'                    <div class="link-title"><a href="{url}" target="_blank" rel="noopener">{label}</a></div>\n'
    item += f'                    <div class="link-url">{url}</div>\n'

    if description:
        item += f'                    <div class="link-description">{description}</div>\n'

    if tags:
        item += '                    <div class="link-tags">\n'
        for tag in tags:
            item += f'                        <span class="tag">{escape_html(tag)}</span>\n'
        item += '                    </div>\n'

    item += '                </li>\n'

    return item


def main():
    output_file = 'bookmarks.html'

    print("Loading links from links.json...")
    links = load_links()

    print(f"Found {len(links)} links")
    print("Generating HTML...")

    html = generate_html(links)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Successfully created {output_file}")
    print(f"Open it in your browser: file://{sys.path[0]}/{output_file}")


if __name__ == '__main__':
    main()
