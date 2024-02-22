import pymysql


not_exists = True
db_name = 'weather_journal'
table_name = 'mood_journal'
table_schema = """
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    temp INTEGER,
    mood VARCHAR(255)
    """
try:
    connection = pymysql.connect(host='localhost', user='root', password='987654321')
    cursor = connection.cursor()
    if not_exists:
        cursor.execute(f"CREATE DATABASE {db_name}")
        cursor.execute(f"USE {db_name}")
        cursor.execute(f"CREATE TABLE {table_name} ({table_schema})")
    else:
        cursor.execute(f"DROP DATABASE {db_name}")
except pymysql.Error as e:
    print(f"Error: {e}")
finally:
    if connection:
        connection.close()
