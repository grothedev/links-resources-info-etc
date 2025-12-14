#!/usr/bin/env python3
"""
Script to import links from links.json into a PostgreSQL or SQLite database.
"""

import json
import sys
import os
import argparse


def load_json_file(filename):
    """Load and parse the JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} links from {filename}")
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}")
        sys.exit(1)


class PostgreSQLHandler:
    """Handler for PostgreSQL database operations."""

    def __init__(self, config):
        import psycopg2
        from psycopg2.extras import execute_values
        self.psycopg2 = psycopg2
        self.execute_values = execute_values
        self.config = config
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to PostgreSQL database."""
        print(f"Connecting to PostgreSQL database '{self.config['dbname']}' at {self.config['host']}:{self.config['port']}...")
        self.conn = self.psycopg2.connect(**self.config)
        self.cursor = self.conn.cursor()

    def create_table(self):
        """Create the links table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                label TEXT NOT NULL,
                tags TEXT[],
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(url)
            );
        """)
        print("Table 'links' created or already exists.")

    def insert_links(self, links):
        """Insert links into the database."""
        data = [
            (link.get('url', ''),
             link.get('label', ''),
             link.get('tags', []),
             link.get('description', ''))
            for link in links
        ]

        query = """
            INSERT INTO links (url, label, tags, description)
            VALUES %s
            ON CONFLICT (url) DO UPDATE SET
                label = EXCLUDED.label,
                tags = EXCLUDED.tags,
                description = EXCLUDED.description;
        """

        self.execute_values(self.cursor, query, data)
        print(f"Successfully inserted/updated {len(links)} links.")

    def get_count(self):
        """Get total count of links."""
        self.cursor.execute("SELECT COUNT(*) FROM links;")
        return self.cursor.fetchone()[0]

    def commit(self):
        """Commit changes."""
        self.conn.commit()

    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


class SQLiteHandler:
    """Handler for SQLite database operations."""

    def __init__(self, db_path):
        import sqlite3
        self.sqlite3 = sqlite3
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to SQLite database."""
        print(f"Connecting to SQLite database '{self.db_path}'...")
        self.conn = self.sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def create_table(self):
        """Create the links table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL UNIQUE,
                label TEXT NOT NULL,
                tags TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Table 'links' created or already exists.")

    def insert_links(self, links):
        """Insert links into the database."""
        for link in links:
            url = link.get('url', '')
            label = link.get('label', '')
            tags = json.dumps(link.get('tags', []))  # Store tags as JSON string
            description = link.get('description', '')

            self.cursor.execute("""
                INSERT INTO links (url, label, tags, description)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    label = excluded.label,
                    tags = excluded.tags,
                    description = excluded.description;
            """, (url, label, tags, description))

        print(f"Successfully inserted/updated {len(links)} links.")

    def get_count(self):
        """Get total count of links."""
        self.cursor.execute("SELECT COUNT(*) FROM links;")
        return self.cursor.fetchone()[0]

    def commit(self):
        """Commit changes."""
        self.conn.commit()

    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Import links from links.json into a database (PostgreSQL or SQLite)'
    )
    parser.add_argument(
        '--db-type',
        choices=['postgres', 'sqlite'],
        default=os.getenv('DB_TYPE', 'sqlite'),
        help='Database type to use (default: sqlite, can also set DB_TYPE env var)'
    )
    parser.add_argument(
        '--sqlite-path',
        default=os.getenv('SQLITE_PATH', 'links.db'),
        help='Path to SQLite database file (default: links.db, can also set SQLITE_PATH env var)'
    )
    parser.add_argument(
        '--json-file',
        default='links.json',
        help='Path to JSON file containing links (default: links.json)'
    )

    args = parser.parse_args()

    try:
        # Load JSON data
        links = load_json_file(args.json_file)

        # Initialize database handler based on type
        if args.db_type == 'postgres':
            # PostgreSQL configuration
            db_config = {
                'dbname': os.getenv('DB_NAME', 'links_db'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'postgres'),
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432')
            }
            handler = PostgreSQLHandler(db_config)
        else:
            # SQLite configuration
            handler = SQLiteHandler(args.sqlite_path)

        # Connect to database
        handler.connect()

        # Create table
        handler.create_table()

        # Insert links
        handler.insert_links(links)

        # Commit changes
        handler.commit()

        # Verify insertion
        count = handler.get_count()
        print(f"\nTotal links in database: {count}")

        print("\nImport completed successfully!")

    except ImportError as e:
        if 'psycopg2' in str(e):
            print("Error: psycopg2 not installed. Install it with: pip install psycopg2-binary")
        else:
            print(f"Import error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'handler' in locals():
            handler.close()


if __name__ == '__main__':
    main()
