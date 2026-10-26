import sqlite3
from contextlib import closing
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "sophia.db"


def initialize_database():
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sys_command (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                path VARCHAR(1000)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS web_command (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                url VARCHAR(1000)
            )
            """
        )
        connection.execute(
            """
            INSERT INTO web_command (name, url)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM web_command WHERE LOWER(name) = LOWER(?)
            )
            """,
            ("GitHub", "https://github.com", "GitHub"),
        )
