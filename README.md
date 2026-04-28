# links-resources-info-etc
a collection of useful links, resources, and notes, with tools to manage them.

## repository structure

```
data/           - link data files (links.txt, links.json)
notes/          - reference notes (ML resources, server security notes)
docs/           - project documentation and specs (DataCluster spec)
web/            - web UI prototypes and assets
bookmarktool/   - main bookmark management tool (Python)
scripts:
  parse_links_txt.py    - parse links.txt and merge into links.json
  import_links_to_db.py - import links.json into SQLite or PostgreSQL
  enrich_links.py       - fetch and fill missing labels/descriptions from URLs
  yt-to-rss.py          - convert YouTube playlist/channel URLs to RSS feeds
```

## usage

**parse links from text file into json:**
```
python parse_links_txt.py
```

**import links into a database:**
```
python import_links_to_db.py --db-type sqlite
python import_links_to_db.py --db-type postgres
```

**enrich link metadata by fetching pages:**
```
python enrich_links.py
```

**convert youtube url to rss:**
```
python yt-to-rss.py "https://www.youtube.com/@username"
```
