import sqlite3


try:
   conn = sqlite3.connect('task_manager.db')
   cursor = conn.cursor()
   cursor.execute('''CREATE TABLE tasks (
                     id INTEGER PRIMARY KEY,
                     description TEXT,
                     due_date TEXT,
                     completed BOOLEAN
                  )''')
except sqlite3.Error as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
