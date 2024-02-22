from fastapi import FastAPI
from mru_cache import MRUCache
import aiohttp
import sqlite3
import os


database_name = "52_weeks_high.db"
table_name = "highs_52_weeks"

app = FastAPI()
cache = MRUCache()

API_URL = "https://www.alphavantage.co/query/"
API_KEY = os.environ.get('ALPHAVANTAGE_API_KEY')


def set_up_database():
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (symbol TEXT PRIMARY KEY, price REAL)")
    connection.commit()
    connection.close()


def save_info_to_db(symbol, high52):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute(f"INSERT OR REPLACE INTO {table_name} (symbol, price) VALUES (?, ?)", (symbol, high52))
    connection.commit()
    connection.close()


def save_info_to_cache(symbol, high52):
    cache.put(symbol, high52)


def get_from_db(symbol):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute(f"SELECT price FROM {table_name} WHERE symbol=?", (symbol,))
    result = cursor.fetchone()
    connection.close()
    return result


def get_from_cache(symbol):
    return cache.get(symbol)


@app.get("/stock/high52/{symbol}")
async def get_stock(symbol):
    high52 = get_from_cache(symbol)

    if not high52:
        high52 = get_from_db(symbol)
        if high52:
            high52 = high52[0]
            save_info_to_cache(symbol, high52)
        else:
            high52 = await get_highest_price(symbol)
            if high52:
                save_info_to_db(symbol, high52)
                save_info_to_cache(symbol, high52)

    if high52:
        return {"symbol": high52}, 200
    else:
        return {"error": "Failed to fetch stock price"}, 400


async def parse_weekly_data(data):
    weekly_data = data.get("Weekly Time Series", {})
    weekly_data = dict(list(weekly_data.items())[:52])
    highs = [float(week_data["2. high"]) for _, week_data in weekly_data.items()]
    high52 = max(highs) if highs else 0.0

    return high52


async def get_highest_price(symbol):
    async with aiohttp.ClientSession() as session:
        params = {
            "function": "TIME_SERIES_WEEKLY",
            "symbol": symbol,
            "apikey": API_KEY
        }
        async with session.get(API_URL, params=params) as response:
            data = await response.json()
            high52 = await parse_weekly_data(data)
            return high52


def run_api():
    from uvicorn import run
    run(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    set_up_database()
    run_api()
