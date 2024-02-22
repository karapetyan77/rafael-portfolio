from fastapi import FastAPI, HTTPException, Request
from datetime import datetime
import aiohttp
import pymysql
import json
import os


class MySQLDatabase:
    def __init__(self, host, user, password, database):
        self.conn = pymysql.connect(host=host, user=user, password=password, database=database)
        self.cursor = self.conn.cursor()

    def insert(self, table_name, values):
        try:
            query = f"INSERT IGNORE INTO {table_name} VALUES({values})"
            self.cursor.execute(query)
            self.conn.commit()
            return True
        except Exception:
            return False

    def update(self, table_name, set_statements, where_condition):
        query = f"UPDATE {table_name} SET {set_statements} WHERE {where_condition}"
        self.cursor.execute(query)
        self.conn.commit()

    def remove(self, table_name, where_condition):
        query = f"DELETE FROM {table_name} WHERE {where_condition}"
        self.cursor.execute(query)
        self.conn.commit()

    def query(self, query_string):
        self.cursor.execute(query_string)
        rows = self.cursor.fetchall()

        formatted_rows = []
        for row in rows:
            date_obj = row[1]
            new_row = row[:1] + (str(date_obj),) + row[2:]
            formatted_rows.append(new_row)

        keys = ['id', 'date', 'temp', 'mood']
        result = [dict(zip(keys, tuple_row)) for tuple_row in formatted_rows]
        return json.dumps(result)

    def __del__(self):
        self.cursor.close()
        self.conn.close()


db = MySQLDatabase(host="localhost", user="root",
                   password="987654321", database="weather_journal")

app = FastAPI()

API_URL = 'https://api.openweathermap.org/data/2.5/weather'
API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY')


async def fetch_weather(city_name: str):
    async with aiohttp.ClientSession() as session:
        params = {
            'q': city_name,
            'appid': API_KEY,
        }
        async with session.get(API_URL, params=params) as response:
            if response.status == 200:
                weather_data = await response.json()
                temp_kelvin = weather_data["main"]["temp"]
                temp_celsius = int(temp_kelvin - 273.15)
                return temp_celsius
            else:
                raise HTTPException(status_code=404, detail="Weather data not found")


@app.post("/log/")
async def log_journal_entry(request: Request):
    data = await request.json()
    mood_data = data.get('mood')
    city_name = data.get('city')

    if not city_name or not mood_data:
        raise HTTPException(
            status_code=400,
            detail="City name and mood are required in the request body")

    # mood_data = data.get('mood')
    city_weather = await fetch_weather(city_name)
    current_date = datetime.today().date()
    values = f"NULL, '{current_date}', {city_weather}, '{mood_data}'"

    if db.insert("mood_journal", values):
        return {"status": "success"}, 200
    else:
        raise HTTPException(status_code=404, detail="Insert failed")


@app.get("/entries")
async def get_journal_entries():
    entries = db.query("SELECT * FROM mood_journal")
    if not entries:
        raise HTTPException(status_code=404, detail="No entries found")

    return entries, {"status": "success"}, 200


@app.get("/entry/{entry_id}")
async def get_journal_entry(entry_id: int):
    entry = db.query(f"SELECT * FROM mood_journal WHERE id = {entry_id}")
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return entry, {"status": "success"}, 200


if __name__ == "__main__":
    from uvicorn import run
    run(app, host="127.0.0.1", port=8000)
