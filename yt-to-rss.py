#!/usr/bin/env python3
"""
YouTube Playlist and Channel to RSS Feed Converter
Converts YouTube playlist URLs and channel URLs to RSS feed URLs that can be used in RSS readers.
"""

import re
import sys
import argparse
import requests
from urllib.parse import urlparse, parse_qs

def extract_playlist_id(url):
    """
    Extract playlist ID from various YouTube URL formats.
    
    Supports:
    - https://www.youtube.com/playlist?list=PLxxxxxx
    - https://www.youtube.com/watch?v=xxxxx&list=PLxxxxxx
    - PLxxxxxx (direct playlist ID)
    """
    # Direct playlist ID
    if re.match(r'^[A-Za-z0-9_-]{34}$', url):
        return url
    
    # Parse URL
    parsed = urlparse(url)
    
    # Extract from query parameters
    if parsed.query:
        query_params = parse_qs(parsed.query)
        if 'list' in query_params:
            return query_params['list'][0]
    
    return None

def extract_channel_id(url):
    """
    Extract channel ID from various YouTube channel URL formats.
    
    Supports:
    - https://www.youtube.com/channel/UCxxxxxx
    - https://www.youtube.com/c/channelname
    - https://www.youtube.com/@username
    - https://www.youtube.com/user/username
    - UCxxxxxx (direct channel ID)
    """
    # Direct channel ID (starts with UC and is 24 characters)
    if re.match(r'^UC[A-Za-z0-9_-]{22}$', url):
        return url
    
    # Parse URL
    parsed = urlparse(url)
    
    if parsed.netloc in ['www.youtube.com', 'youtube.com', 'm.youtube.com']:
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            if path_parts[0] == 'channel':
                # https://www.youtube.com/channel/UCxxxxxx
                return path_parts[1]
            elif path_parts[0] in ['c', 'user']:
                # https://www.youtube.com/c/channelname or /user/username
                # These need to be resolved to channel ID via API or web scraping
                return resolve_channel_handle(url)
        elif len(path_parts) >= 1 and path_parts[0].startswith('@'):
            # https://www.youtube.com/@username
            return resolve_channel_handle(url)
    
    return None

def resolve_channel_handle(url):
    """
    Resolve channel handle/username to channel ID by scraping the page.
    This is a fallback method when we can't extract the ID directly.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Look for channel ID in the page source
            content = response.text
            # Try to find channel ID in various places in the HTML
            patterns = [
                r'"channelId":"(UC[A-Za-z0-9_-]{22})"',
                r'channel_id=([UC][A-Za-z0-9_-]{22})',
                r'/channel/(UC[A-Za-z0-9_-]{22})',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
    except requests.RequestException:
        pass
    
    return None

def get_playlist_rss_url(playlist_id):
    """Generate RSS feed URL for a YouTube playlist."""
    return f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"

def get_channel_rss_url(channel_id):
    """Generate RSS feed URL for a YouTube channel."""
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

def verify_rss_exists(rss_url):
    """Verify that the RSS feed exists and is accessible."""
    try:
        response = requests.head(rss_url, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_rss_info(rss_url):
    """Get basic information from the RSS feed."""
    try:
        response = requests.get(rss_url, timeout=10)
        if response.status_code == 200:
            # Basic XML parsing to extract title
            content = response.text
            title_match = re.search(r'<title>(.+?)</title>', content)
            if title_match:
                return title_match.group(1)
    except requests.RequestException:
        pass
    
    return None

def main():
    parser = argparse.ArgumentParser(
        description="Convert YouTube playlist and channel URLs to RSS feed URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Playlists
  %(prog)s "https://www.youtube.com/playlist?list=PLxxxxxx"
  %(prog)s "https://www.youtube.com/watch?v=xxxxx&list=PLxxxxxx"
  %(prog)s PLxxxxxx
  
  # Channels
  %(prog)s "https://www.youtube.com/channel/UCxxxxxx"
  %(prog)s "https://www.youtube.com/c/channelname"
  %(prog)s "https://www.youtube.com/@username"
  %(prog)s "https://www.youtube.com/user/username"
  %(prog)s UCxxxxxx
  
  # With options
  %(prog)s --verify "https://www.youtube.com/channel/UCxxxxxx"
  %(prog)s --info "https://www.youtube.com/@username"
        """
    )
    
    parser.add_argument(
        'url', 
        help='YouTube playlist URL, channel URL, or ID'
    )
    
    parser.add_argument(
        '--verify', 
        action='store_true',
        help='Verify that the RSS feed exists and is accessible'
    )
    
    parser.add_argument(
        '--info',
        action='store_true', 
        help='Show feed information (title, etc.)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Only output the RSS URL'
    )
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Try to extract playlist ID first
    playlist_id = extract_playlist_id(args.url)
    channel_id = None
    feed_type = None
    rss_url = None
    
    if playlist_id:
        feed_type = "playlist"
        rss_url = get_playlist_rss_url(playlist_id)
    else:
        # Try to extract channel ID
        channel_id = extract_channel_id(args.url)
        if channel_id:
            feed_type = "channel"
            rss_url = get_channel_rss_url(channel_id)
    
    if not rss_url:
        print("Error: Could not extract playlist or channel ID from URL", file=sys.stderr)
        print("Supported formats:", file=sys.stderr)
        print("  Playlists:", file=sys.stderr)
        print("    - https://www.youtube.com/playlist?list=PLxxxxxx", file=sys.stderr)
        print("    - https://www.youtube.com/watch?v=xxxxx&list=PLxxxxxx", file=sys.stderr)
        print("    - PLxxxxxx (direct playlist ID)", file=sys.stderr)
        print("  Channels:", file=sys.stderr)
        print("    - https://www.youtube.com/channel/UCxxxxxx", file=sys.stderr)
        print("    - https://www.youtube.com/c/channelname", file=sys.stderr)
        print("    - https://www.youtube.com/@username", file=sys.stderr)
        print("    - https://www.youtube.com/user/username", file=sys.stderr)
        print("    - UCxxxxxx (direct channel ID)", file=sys.stderr)
        sys.exit(1)
    
    if args.quiet:
        print(rss_url)
        return
    
    if feed_type == "playlist":
        print(f"Playlist ID: {playlist_id}")
    else:
        print(f"Channel ID: {channel_id}")
    
    print(f"Feed Type: {feed_type.title()}")
    print(f"RSS Feed URL: {rss_url}")
    
    # Verify RSS feed exists if requested
    if args.verify:
        print(f"\nVerifying {feed_type}...")
        if verify_rss_exists(rss_url):
            print("✓ RSS feed exists and is accessible")
        else:
            print("✗ RSS feed not found or not accessible")
            sys.exit(1)
    
    # Get RSS feed info if requested
    if args.info:
        print(f"\nFetching {feed_type} information...")
        title = get_rss_info(rss_url)
        if title:
            print(f"Title: {title}")
        else:
            print("Could not fetch feed information")

if __name__ == "__main__":
    main()