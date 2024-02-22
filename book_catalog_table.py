import sqlite3


try:
    conn = sqlite3.connect('the_book_catalog.db')
    cursor = conn.cursor()
    cursor.execute("""
                    CREATE TABLE books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    year_published INTEGER,
                    genre TEXT,
                    rating INTEGER
                    )
                    """)
except sqlite3.Error as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
