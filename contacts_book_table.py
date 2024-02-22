import sqlite3


try:
    data_base = sqlite3.connect("Contacts.db")
    cursor = data_base.cursor()
    cursor.execute('''CREATE TABLE contacts (
                        name TEXT,
                        surname TEXT,
                        address TEXT,
                        phone_number TEXT
                        )''')
except sqlite3.Error as e:
    print(f"Error: {e}")
finally:
    if data_base:
        data_base.close()
