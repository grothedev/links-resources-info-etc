#!/usr/bin/env python3
"""
Script to parse links.txt and add new links to links.json.
Only adds links that don't already exist in the JSON file.
"""

import json
import re
from urllib.parse import urlparse


def is_valid_url(text):
    """Check if text is a valid URL."""
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_url_from_line(line):
    """Extract URL from a line of text."""
    # Try to find URLs in the line
    url_pattern = r'https?://[^\s]+'
    matches = re.findall(url_pattern, line)
    return matches[0] if matches else None


def parse_line(line):
    """
    Parse a line and extract URL, label, and tags.

    Formats supported:
    - https://example.com
    - https://example.com :tag1, :tag2
    - label text: https://example.com
    - label text: https://example.com :tag1, :tag2
    - label text https://example.com
    """
    line = line.strip()

    # Skip empty lines and section headers
    if not line or not 'http' in line:
        return None

    # Extract URL
    url = extract_url_from_line(line)
    if not url:
        return None

    # Remove URL from line to work with remaining text
    remaining = line.replace(url, '').strip()

    # Extract tags (anything after the URL that starts with :)
    tags = []
    tag_pattern = r':(\w+)'
    tag_matches = re.findall(tag_pattern, remaining)
    if tag_matches:
        tags = tag_matches
        # Remove tags from remaining text
        remaining = re.sub(r':[\w,\s]+$', '', remaining).strip()

    # What's left is the label (remove trailing colons)
    label = remaining.rstrip(':').strip()

    # If no label, use the URL as label
    if not label:
        label = url

    return {
        'url': url,
        'label': label,
        'tags': tags,
        'description': ''
    }


def load_existing_links(json_file):
    """Load existing links from JSON file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {json_file} not found. Will create new file.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error reading {json_file}: {e}")
        return []


def parse_links_txt(txt_file):
    """Parse links.txt and extract all links."""
    links = []

    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                parsed = parse_line(line)
                if parsed:
                    links.append(parsed)
                    print(f"Line {line_num}: Found {parsed['url']} (tags: {parsed['tags']})")
    except FileNotFoundError:
        print(f"Error: {txt_file} not found.")
        return []

    return links


def merge_links(existing_links, new_links):
    """Merge new links into existing links, avoiding duplicates."""
    # Create a set of existing URLs for quick lookup
    existing_urls = {link['url'] for link in existing_links}

    added_count = 0
    for link in new_links:
        if link['url'] not in existing_urls:
            existing_links.append(link)
            existing_urls.add(link['url'])
            added_count += 1
            print(f"Added: {link['url']}")
        else:
            print(f"Skipped (already exists): {link['url']}")

    return existing_links, added_count


def save_links(json_file, links):
    """Save links to JSON file."""
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(links, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(links)} total links to {json_file}")


def main():
    txt_file = 'links.txt'
    json_file = 'links.json'

    print(f"Parsing {txt_file}...")
    new_links = parse_links_txt(txt_file)
    print(f"\nFound {len(new_links)} links in {txt_file}\n")

    print(f"Loading existing links from {json_file}...")
    existing_links = load_existing_links(json_file)
    print(f"Found {len(existing_links)} existing links\n")

    print("Merging links...")
    merged_links, added_count = merge_links(existing_links, new_links)

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Links in {txt_file}: {len(new_links)}")
    print(f"  Links already in {json_file}: {len(existing_links)}")
    print(f"  New links added: {added_count}")
    print(f"  Total links now: {len(merged_links)}")
    print(f"{'='*60}\n")

    save_links(json_file, merged_links)
    print("Done!")


if __name__ == '__main__':
    main()
