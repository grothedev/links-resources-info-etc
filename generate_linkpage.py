#!/usr/bin/env python3
"""Render a list of bookmarks into a simple single-file web page.

Reads a JSON, YAML, or TOML file containing an array of link records:

    [
      {
        "url": "https://example.com",
        "label": "Example Site",       // optional, falls back to the url
        "tags": ["dev", "tools"],      // optional
        "description": "what it is"    // optional
      }
    ]

and writes a minimal, terminal-flavored HTML page listing them.

Works well paired with bin/linkgrab.py output saved as JSON.

Examples:
    linkpage.py tmp/links.json tmp/links.html
    linkpage.py links.json --tags dev,ml --sort label
    linkpage.py links.json --stdout > page.html

Configuration (cmnpy framework):
    page_title  : page <h1>/<title>, also LINKPAGE_TITLE env
    trim_desc   : max description characters (0 keeps full text), also
                  LINKPAGE_TRIM env. Standard flags apply too: --config,
                  --config-dir, --config-file, --set, --show-config.

Styling is intentionally reminiscent of OpenCode: monospace typography on a
near-black background, muted grays, and a single warm accent color.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

try:
    import cmnpy
except ImportError:
    # this script lives in bin/, next to the cmnpy checkout
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'cmnpy'))
    import cmnpy

import yaml

try:
    import tomllib
except ImportError:
    tomllib = None

from cmnpy import cli, config, util

READ_SUFFIXES = ('.json', '.yaml', '.yml', '.toml')


# --- cmnpy configuration -----------------------------------------------------

schema = config.Schema({
    'page_title': config.Field(
        default='links', env='LINKPAGE_TITLE',
        validator=lambda value: bool(str(value).strip())),
    'trim_desc': config.Field(
        default=240, env='LINKPAGE_TRIM', parse=int,
        validator=lambda value: value >= 0),
})


def buildParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Render a bookmark list (json/yaml/toml) as a web page.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        'input', nargs='?', metavar='LINKS_FILE',
        help='links file (.json, .yaml, or .toml)')
    parser.add_argument(
        'output', nargs='?', metavar='HTML_FILE',
        help='html file to write (default: links.html)')
    parser.add_argument(
        '--tags', metavar='TAG1,TAG2',
        help='only include links having any of these tags')
    parser.add_argument(
        '--sort', choices=('none', 'label', 'tag'), default='none',
        help='sort links by label or tag (default: file order)')
    parser.add_argument(
        '--stdout', action='store_true',
        help='write the page to stdout instead of a file')
    return parser


# --- input parsing -----------------------------------------------------------

def loadLinks(path: Path) -> list:
    if not path.is_file():
        raise ValueError(f'links file does not exist: {path}')
    suffix = path.suffix.lower()
    if suffix not in READ_SUFFIXES:
        raise ValueError(
            f'unsupported links file format {suffix!r}; '
            'expected one of: ' + ', '.join(READ_SUFFIXES))
    try:
        if suffix == '.json':
            with path.open('r', encoding='utf-8') as f:
                data = json.load(f)
        elif suffix == '.toml':
            if tomllib is None:
                raise ValueError('toml support needs python 3.11+')
            with path.open('rb') as f:
                data = tomllib.load(f)
        else:
            with path.open('r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, ValueError) as exc:
        raise ValueError(f'could not parse links file {path}: {exc}') from exc

    if isinstance(data, dict):  # tolerate {"links": [...]}
        data = data.get('links')
    if not isinstance(data, list):
        raise ValueError(f'links file {path} must contain a list of link records')

    links = []
    for index, record in enumerate(data):
        if not isinstance(record, dict):
            raise ValueError(f'links file {path}: record {index} is not a mapping')
        url = record.get('url')
        if not isinstance(url, str) or not url.strip():
            raise ValueError(f'links file {path}: record {index} has no "url"')
        links.append(record)
    return links


def normalizeLinks(links: list) -> list:
    '''Fill defaults: label falls back to url, tags list always present.'''
    normalized = []
    for record in links:
        url = record['url'].strip()
        label = str(record.get('label') or url).strip() or url
        tags = record.get('tags')
        normalized.append({
            'url': url,
            'label': label,
            'tags': [str(t) for t in tags] if isinstance(tags, list) else [],
            'description': str(record.get('description') or '').strip(),
        })
    return normalized


# --- html rendering ----------------------------------------------------------

_CSS = '''
:root { --bg:#0e0e10; --panel:#151518; --border:#26262b; --line:#32323a;
        --text:#e2e2e6; --muted:#8b8b95; --accent:#ff9f5b; }
* { box-sizing: border-box; margin: 0; }
body { max-width: 48rem; margin: 0 auto; padding: 2.5rem 1rem 4rem;
       background: var(--bg); color: var(--text);
       font: 14px/1.55 ui-monospace, "SF Mono", "Cascadia Code", "Fira Code",
             Menlo, Consolas, monospace; }
header { padding-bottom: 1rem; margin-bottom: 1.5rem;
         border-bottom: 1px solid var(--border); }
header h1 { font-size: 15px; font-weight: 600; letter-spacing: .04em;
            text-transform: lowercase; }
header h1::before { content: "$ "; color: var(--muted); }
.meta { margin-top: .3rem; color: var(--muted); font-size: 12px; }
.meta span { color: var(--accent); }
ol { list-style: none; padding: 0; }
li { padding: .8rem 1rem; margin-bottom: .55rem;
     background: var(--panel); border: 1px solid var(--border);
     border-radius: 6px; }
li a { color: var(--accent); text-decoration: none; }
li a:hover { text-decoration: underline; }
.tags { margin-top: .35rem; }
.tag { display: inline-block; margin-right: .4rem; padding: 0 .45rem;
       font-size: 11px; color: var(--muted);
       border: 1px solid var(--border); border-radius: 4px; }
.tag::before { content: "#"; opacity: .6; }
.desc { margin-top: .35rem; color: var(--muted); font-size: 12.5px; }
'''


def _trim(text: str, limit: int) -> str:
    if limit and len(text) > limit:
        return text[:limit].rstrip() + ' …'
    return text


def renderPage(title: str, links: list, trim: int) -> str:
    esc = html.escape
    items = []
    for link in links:
        parts = [f'<a href="{esc(link["url"], quote=True)}">{esc(link["label"])}</a>']
        if link['tags']:
            parts.append('<div class="tags">' + ''.join(
                f'<span class="tag">{esc(tag)}</span>' for tag in link['tags']) + '</div>')
        if link['description']:
            parts.append(f'<p class="desc">{esc(_trim(link["description"], trim))}</p>')
        items.append('      <li>' + ''.join(parts) + '</li>')

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>{_CSS}</style>
</head>
<body>
<header>
  <h1>{esc(title)}</h1>
  <p class="meta"><span>{len(links)}</span> links</p>
</header>
    <ol>
{chr(10).join(items)}
    </ol>
</body>
</html>
'''


# --- main --------------------------------------------------------------------

def main(settings, args) -> None:
    if not args.input:
        print('error: missing LINKS_FILE argument', file=sys.stderr)
        sys.exit(2)

    links = normalizeLinks(loadLinks(Path(args.input)))

    if args.tags:
        wanted = {tag.strip() for tag in args.tags.split(',') if tag.strip()}
        links = [link for link in links if set(link['tags']) & wanted]
    if not links:
        print('error: no links to render (input empty or filter too narrow)',
              file=sys.stderr)
        sys.exit(1)
    if args.sort == 'label':
        links.sort(key=lambda link: link['label'].lower())
    elif args.sort == 'tag':
        links.sort(key=lambda link: (' '.join(sorted(link['tags'])), link['label'].lower()))

    page = renderPage(str(settings.page_title), links, int(settings.trim_desc))

    if args.stdout:
        sys.stdout.write(page)
    else:
        out = Path(args.output or 'links.html')
        out.write_text(page, encoding='utf-8')
        util.log(f'linkpage: rendered {len(links)} link(s) -> {out}')
        print(f'{len(links)} link(s) -> {out}')


if __name__ == '__main__':
    cli.run(schema, main=main, parser=buildParser(), app_name='linkpage',
            description='render a bookmark list as a web page')

# *************************************************************************************************
