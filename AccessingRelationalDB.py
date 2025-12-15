"""
Author: Your Name
Date: 2025-12-14
Assignment: EN_ReviewData CRUD Application
Purpose: This program demonstrates full CRUD operations on an SQLite database named EN_ReviewData.db.
         It creates the required tables (Reviewers, Categories, Products, Reviews), enables foreign keys,
         loads data from a JSON file, and provides a text-based menu for:
         * Displaying categories with at least a user-specified number of products
         * Executing ad-hoc SQL SELECT statements
         * Inserting a row into any table
         * Deleting all reviews for a user-specified product_category
         * Deleting all tables in the database
"""

import sqlite3
import json
import os
from typing import Optional, Tuple, List, Dict

DB_NAME = "EN_ReviewData.db"

# ---------------------------------------------
# Utility functions for database connections
# ---------------------------------------------

def get_connection() -> sqlite3.Connection:
    """
    Create a database connection and ensure foreign keys are enforced.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ---------------------------------------------------
# * Create database and required tables per assignment
# ---------------------------------------------------

def create_db_and_tables():
    """
    Create all required tables with appropriate primary/foreign keys.
    Tables:
      - Reviewers(reviewer_id PRIMARY KEY, name OPTIONAL)
      - Categories(product_category PRIMARY KEY)
      - Products(product_id PRIMARY KEY, product_name OPTIONAL, product_category FOREIGN KEY -> Categories)
      - Reviews(review_id PRIMARY KEY, product_id FOREIGN KEY -> Products, reviewer_id FOREIGN KEY -> Reviewers,
                stars, review_body, review_title)
    """
    conn = get_connection()
    cur = conn.cursor()

    # * Create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Reviewers (
            reviewer_id TEXT PRIMARY KEY,
            name TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Categories (
            product_category TEXT PRIMARY KEY
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            product_category TEXT NOT NULL,
            FOREIGN KEY(product_category) REFERENCES Categories(product_category) ON DELETE CASCADE ON UPDATE CASCADE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Reviews (
            review_id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            reviewer_id TEXT NOT NULL,
            stars INTEGER,
            review_body TEXT,
            review_title TEXT,
            FOREIGN KEY(product_id) REFERENCES Products(product_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(reviewer_id) REFERENCES Reviewers(reviewer_id) ON DELETE CASCADE ON UPDATE CASCADE
        );
    """)

    conn.commit()
    conn.close()
    print("Database and tables created (or already exist).")


# ----------------------------------------------------
# * Insert data from a JSON file into the tables
# ----------------------------------------------------

def insert_from_json(json_path: str):
    """
    Insert data from a JSON file into the database.

    Expected JSON structure (keys are optional if not used):
    {
      "categories": [
        {"product_category": "Electronics"},
        {"product_category": "Books"}
      ],
      "reviewers": [
        {"reviewer_id": "r1", "name": "Alice"},
        {"reviewer_id": "r2", "name": "Bob"}
      ],
      "products": [
        {"product_id": "p1", "product_name": "Headphones", "product_category": "Electronics"},
        {"product_id": "p2", "product_name": "Novel", "product_category": "Books"}
      ],
      "reviews": [
        {"review_id": "rv1", "product_id": "p1", "reviewer_id": "r1", "stars": 5,
         "review_title": "Great!", "review_body": "Loved the sound quality"},
        {"review_id": "rv2", "product_id": "p2", "reviewer_id": "r2", "stars": 4,
         "review_title": "Enjoyable", "review_body": "Good read"}
      ]
    }

    Notes:
    - Missing optional fields will be inserted as NULL.
    - Existing rows (same primary key) will be ignored via INSERT OR IGNORE.
    """
    if not os.path.isfile(json_path):
        print(f"File not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = get_connection()
    cur = conn.cursor()

    # * Use transactions for integrity and performance
    try:
        conn.execute("BEGIN;")

        # * Insert categories
        for cat in data.get("categories", []):
            product_category = cat.get("product_category")
            if product_category:
                cur.execute("""
                    INSERT OR IGNORE INTO Categories (product_category)
                    VALUES (?);
                """, (product_category,))

        # * Insert reviewers
        for rev in data.get("reviewers", []):
            reviewer_id = rev.get("reviewer_id")
            name = rev.get("name")
            if reviewer_id:
                cur.execute("""
                    INSERT OR IGNORE INTO Reviewers (reviewer_id, name)
                    VALUES (?, ?);
                """, (reviewer_id, name))

        # * Insert products
        for prod in data.get("products", []):
            product_id = prod.get("product_id")
            product_name = prod.get("product_name")
            product_category = prod.get("product_category")
            if product_id and product_category:
                cur.execute("""
                    INSERT OR IGNORE INTO Products (product_id, product_name, product_category)
                    VALUES (?, ?, ?);
                """, (product_id, product_name, product_category))

        # * Insert reviews
        for rv in data.get("reviews", []):
            review_id = rv.get("review_id")
            product_id = rv.get("product_id")
            reviewer_id = rv.get("reviewer_id")
            stars = rv.get("stars")
            review_body = rv.get("review_body")
            review_title = rv.get("review_title")
            if review_id and product_id and reviewer_id:
                cur.execute("""
                    INSERT OR IGNORE INTO Reviews (review_id, product_id, reviewer_id, stars, review_body, review_title)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (review_id, product_id, reviewer_id, stars, review_body, review_title))

        conn.commit()
        print("Data inserted successfully from JSON.")

    except sqlite3.IntegrityError as e:
        conn.rollback()
        print(f"Integrity error while inserting data: {e}")
    except Exception as e:
        conn.rollback()
        print(f"Error while inserting data: {e}")
    finally:
        conn.close()


# ----------------------------------------------------------------------
# * Display categories that have at least a user-entered number of products
# ----------------------------------------------------------------------

def display_categories_by_min_products(min_count: int):
    """
    Show categories with product counts >= min_count.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.product_category, COUNT(p.product_id) AS product_count
        FROM Categories c
        LEFT JOIN Products p ON p.product_category = c.product_category
        GROUP BY c.product_category
        HAVING COUNT(p.product_id) >= ?
        ORDER BY product_count DESC, c.product_category ASC;
    """, (min_count,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print(f"No categories found with at least {min_count} products.")
        return

    print(f"Categories with at least {min_count} products:")
    for category, count in rows:
        print(f"- {category}: {count}")


# -----------------------------------------------------------
# * Allow the user to type in and execute SQL SELECT statements
# -----------------------------------------------------------

def execute_user_select(sql: str):
    """
    Execute a user-provided SQL SELECT statement safely:
    - Restrict to SELECT-only to prevent harmful operations.
    """
    sql_stripped = sql.strip().lower()
    if not sql_stripped.startswith("select"):
        print("Only SELECT statements are allowed in this mode.")
        return

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        cols = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()

        # * Display results in a simple table-like format
        if cols:
            print(" | ".join(cols))
            print("-" * (len(" | ".join(cols)) + 3))
        for row in rows:
            print(" | ".join(str(x) if x is not None else "" for x in row))
        if not rows:
            print("No rows returned.")
    except sqlite3.Error as e:
        print(f"SQL error: {e}")
    finally:
        conn.close()


# ---------------------------------------------------------
# * Allow the user to insert a row into any table by prompt
# ---------------------------------------------------------

def list_tables() -> List[str]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cur.fetchall()]
    conn.close()
    return tables


def get_table_columns(table: str) -> List[Tuple[str, str, bool]]:
    """
    Return [(name, type, is_pk)] for the given table.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    cols = [(row[1], row[2], bool(row[5])) for row in cur.fetchall()]  # (name, type, pk flag)
    conn.close()
    return cols


def prompt_insert_row_any_table():
    """
    Prompt user to choose a table and input column values.
    Uses parameterized INSERT to avoid SQL injection.
    """
    tables = list_tables()
    if not tables:
        print("No tables found. Create tables first.")
        return

    print("Available tables:")
    for i, t in enumerate(tables, start=1):
        print(f"{i}. {t}")
    try:
        choice = int(input("Select a table number to insert into: ").strip())
        table = tables[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    columns = get_table_columns(table)
    print(f"Columns for {table}:")
    for name, coltype, is_pk in columns:
        pk_mark = " (PK)" if is_pk else ""
        print(f"- {name} [{coltype}]{pk_mark}")

    values = []
    col_names = []
    for name, coltype, _ in columns:
        # * Ask the user for value per column (blank means NULL)
        raw = input(f"Enter value for '{name}' (leave blank for NULL): ").strip()
        val = None if raw == "" else raw
        # Cast stars to int when relevant
        if table == "Reviews" and name == "stars" and val is not None:
            try:
                val = int(val)
            except ValueError:
                print("Invalid stars value; must be an integer. Aborting insert.")
                return
        values.append(val)
        col_names.append(name)

    placeholders = ", ".join(["?"] * len(values))
    col_clause = ", ".join(col_names)
    sql = f"INSERT INTO {table} ({col_clause}) VALUES ({placeholders});"

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql, values)
        conn.commit()
        print(f"Row inserted into {table}.")
    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
    except sqlite3.Error as e:
        print(f"Insert error: {e}")
    finally:
        conn.close()


# --------------------------------------------------------------------
# * Delete all records in Reviews for a user-entered product_category
