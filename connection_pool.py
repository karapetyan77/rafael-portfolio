from queue import Queue
import sqlite3


class ConnectionPool:
    def __init__(self, db_name, size=2):
        self.db_name = db_name
        self.size = size
        self.pool = Queue(size)
        for _ in range(size):
            conn = sqlite3.connect(db_name)
            self.pool.put(conn)
    
    def acquire_conn(self):
        return self.pool.get()

    def release_conn(self, conn):
        self.pool.put(conn)
    
    def __del__(self):
        for _ in range(self.pool.qsize()):
            self.pool.get().close()


def main():
    pool = ConnectionPool('books.db', 3)
    conn = pool.acquire_conn()
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS books_table (
                   id INTEGER PRIMARY KEY,
                   title TEXT
                   )""")
    
    try:
        cursor.execute("""INSERT INTO books_table (title) VALUES ('book1')""")
        conn.commit()
        pool.release_conn(conn)
    except Exception as e:
        print(f"Error: {e}")
        conn.close()

    pool.acquire_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books_table")
    res = cursor.fetchall()
    for name in res:
        print(name)

    pool.release_conn(conn)


if __name__ == "__main__":
    main()
