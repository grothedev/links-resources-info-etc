#!/usr/bin/env python3
"""
Script to enrich links.json by fetching missing labels and descriptions from URLs.
"""

import json
import sys
import time
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install requests beautifulsoup4")
    sys.exit(1)


def load_links(json_file):
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


def save_links(json_file, links):
    """Save links to JSON file."""
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(links, f, indent=2, ensure_ascii=False)
    print(f"\nSaved {len(links)} links to {json_file}")


def fetch_html(url, timeout=10):
    """Fetch HTML content from URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        print(f"  ⚠ Timeout fetching {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  ⚠ Error fetching {url}: {e}")
        return None


def extract_label(soup, url):
    """
    Extract label from HTML.
    Priority: <title>, og:title meta tag, twitter:title, h1, domain name
    """
    # Try <title> tag
    title_tag = soup.find('title')
    if title_tag and title_tag.string:
        label = title_tag.string.strip()
        if label:
            return label

    # Try Open Graph title
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        label = og_title['content'].strip()
        if label:
            return label

    # Try Twitter title
    twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
    if twitter_title and twitter_title.get('content'):
        label = twitter_title['content'].strip()
        if label:
            return label

    # Try first h1
    h1 = soup.find('h1')
    if h1:
        label = h1.get_text().strip()
        if label:
            return label

    # Fallback to domain name
    parsed = urlparse(url)
    return parsed.netloc


def extract_description(soup):
    """
    Extract description from HTML.
    Priority: meta description, og:description, twitter:description, first p tag
    """
    # Try meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        desc = meta_desc['content'].strip()
        if desc:
            return desc

    # Try Open Graph description
    og_desc = soup.find('meta', property='og:description')
    if og_desc and og_desc.get('content'):
        desc = og_desc['content'].strip()
        if desc:
            return desc

    # Try Twitter description
    twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
    if twitter_desc and twitter_desc.get('content'):
        desc = twitter_desc['content'].strip()
        if desc:
            return desc

    # Try first paragraph in main/article/content div
    for container in ['main', 'article', 'content', 'post-content', 'entry-content']:
        content_div = soup.find(['div', 'main', 'article'], class_=lambda c: c and container in c.lower())
        if content_div:
            p = content_div.find('p')
            if p:
                desc = p.get_text().strip()
                if desc:
                    return desc[:500]  # Limit to 500 chars

    # Try first p tag anywhere
    p = soup.find('p')
    if p:
        desc = p.get_text().strip()
        if desc:
            return desc[:500]  # Limit to 500 chars

    return ""


def needs_enrichment(link):
    """Check if link needs label or description enrichment."""
    url = link.get('url', '')
    label = link.get('label', '')
    description = link.get('description', '')

    # Needs enrichment if label is empty/same as URL, or description is empty
    label_needs_work = not label or label == url
    desc_needs_work = not description

    return label_needs_work or desc_needs_work


def enrich_link(link, delay=1.0):
    """Enrich a single link with label and description."""
    url = link.get('url', '')
    label = link.get('label', '')
    description = link.get('description', '')

    label_needs_work = not label or label == url
    desc_needs_work = not description

    if not label_needs_work and not desc_needs_work:
        return link, False

    print(f"\nFetching: {url}")
    print(f"  Label: {'[MISSING]' if label_needs_work else '[OK]'}")
    print(f"  Description: {'[MISSING]' if desc_needs_work else '[OK]'}")

    # Fetch HTML
    html = fetch_html(url)
    if not html:
        return link, False

    # Parse HTML
    soup = BeautifulSoup(html, 'html.parser')

    updated = False

    # Extract label if needed
    if label_needs_work:
        new_label = extract_label(soup, url)
        if new_label and new_label != url:
            link['label'] = new_label
            print(f"  ✓ Label: {new_label[:80]}")
            updated = True
        else:
            print(f"  ✗ Could not extract label")

    # Extract description if needed
    if desc_needs_work:
        new_desc = extract_description(soup)
        if new_desc:
            link['description'] = new_desc
            print(f"  ✓ Description: {new_desc[:80]}...")
            updated = True
        else:
            print(f"  ✗ Could not extract description")

    # Be nice to servers
    if delay > 0:
        time.sleep(delay)

    return link, updated


def main():
    json_file = 'links.json'

    print("Loading links...")
    links = load_links(json_file)
    print(f"Loaded {len(links)} links")

    # Find links that need enrichment
    needs_work = [link for link in links if needs_enrichment(link)]
    print(f"\nFound {len(needs_work)} links needing enrichment")

    if not needs_work:
        print("All links already have labels and descriptions!")
        return

    # Ask for confirmation
    response = input(f"\nEnrich {len(needs_work)} links? This may take a while. (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return

    # Process each link
    updated_count = 0
    for i, link in enumerate(links, 1):
        if needs_enrichment(link):
            print(f"\n[{i}/{len(links)}]", end=' ')
            enriched_link, was_updated = enrich_link(link, delay=1.0)
            links[i-1] = enriched_link
            if was_updated:
                updated_count += 1

            # Save periodically (every 10 links)
            if updated_count > 0 and updated_count % 10 == 0:
                save_links(json_file, links)
                print(f"\n  💾 Progress saved ({updated_count} updated so far)")

    # Final save
    save_links(json_file, links)

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total links: {len(links)}")
    print(f"  Links processed: {len(needs_work)}")
    print(f"  Links updated: {updated_count}")
    print(f"{'='*60}")
    print("\nDone!")


if __name__ == '__main__':
    main()
