from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, date
from pydantic import BaseModel
import asyncpg
import os


class Task(BaseModel):
    title: str
    description: str
    deadline: date


app = FastAPI()

three_days_ahead = (datetime.now() + timedelta(days=3)).date()
date_column = 'deadline'

table_name = 'tasks'

db_config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT'),
    'database': os.environ.get('DB_NAME')
    }


async def get_connection():
    try:
        conn = await asyncpg.connect(**db_config)
        return conn
    except Exception as e:
        print(f"Error: {e}")
    return None


@app.post('/tasks/')
async def create_task(task_body: Task):
    title = task_body.title
    description = task_body.description
    deadline = task_body.deadline

    try:
        conn = await get_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Unable to connect to database")

        query = f"""
        INSERT INTO {table_name}
        (title, description, deadline)
        VALUES($1, $2, $3)
        """

        await conn.execute(query, title, description, deadline)

        return JSONResponse(status_code=200, content={"message": "Task created successfully"})
    
    except asyncpg.ConnectionFailureError as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=f"{e}")
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail=f"Error: {e}") 
    
    finally:
        if conn:
            await conn.close()



@app.get('/tasks/{id}')
async def get_task(id: int):
    try:
        conn = await get_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Unable to connect to database")
        
        query = f"SELECT * FROM {table_name} WHERE id = {id}"
        row = await conn.fetchrow(query)
        if row is None:
            return JSONResponse(status_code=404, content={"message": "Task not found"})
        
        return row
    except asyncpg.ConnectionFailureError as e:
        print("Errorrr:", e)
        raise HTTPException(status_code=500, detail="Database connection error")
    except Exception as e:
        print("Error:", e)
    finally:
        if conn:
            await conn.close()


@app.get('/tasks/')
async def get_all_task():
    try:
        conn = await get_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Unable to connect to database")
        
        query = f"SELECT * FROM {table_name}"
        rows = await conn.fetch(query)

        if rows is None:
            return JSONResponse(status_code=404, content={"message": "Task not found"})

        return rows
    except asyncpg.ConnectionFailureError as e:
        print("Errorrr:", e)
        raise HTTPException(status_code=500, detail="Database connection error")
    except Exception as e:
        print("Error:", e)
    finally:
        if conn:
            await conn.close()


@app.get('/tasks/3daysahead/')
async def get_3days_ahead_task():
    try:
        conn = await get_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Unable to connect to database")

        query = f"""
        SELECT * FROM {table_name}
        WHERE {date_column} BETWEEN CURRENT_DATE AND $1
        """
        
        rows = await conn.fetch(query, three_days_ahead)
        if not rows:
            return {"message": "No tasks found in the next three days"}

        return rows
    except Exception as e:
        print("Error:", e)
    finally:
        if conn:
            await conn.close()


@app.put('/tasks/{id}')
async def update_task(id: int, task_body: Request):
    data = await task_body.json()
    required_fields = {'title', 'description', 'deadline'}
    if set(data.keys()) != required_fields:
        raise HTTPException(status_code=400, detail="Invalid input: Use the keys 'title', 'description', 'deadline'.")

    title = data['title']
    description = data['description']
    deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')

    try:
        conn = await get_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Unable to connect to database")

        query = f"""UPDATE {table_name} SET
        title = $1,
        description = $2,
        deadline = $3
        WHERE id = $4
        """
        await conn.execute(query, title, description, deadline, id)
        return JSONResponse(status_code=200, content={"message": "Task updated successfully"})
    
    except Exception as e:
        print("Error:", e)

    finally:
        if conn:
            await conn.close()


@app.delete('/tasks/{id}')
async def delete_task(id: int):
    try:
        conn = await get_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Unable to connect to database")
        
        query_check = f"SELECT 1 FROM {table_name} WHERE id = $1"
        exists = await conn.fetchval(query_check, id)
        if not exists:
            raise HTTPException(status_code=404, detail=f"Task with id {id} not found")
        
        query = f"DELETE FROM {table_name} WHERE id = $1"
        await conn.execute(query, id)
       
        return JSONResponse(status_code=200, content={"message": "Task deleted successfully"})
    except HTTPException as e:
        raise e
    
    except Exception as e:
        print("Error", e)
        
    finally:
        if conn:
            await conn.close()


if __name__ == '__main__':
    from uvicorn import run
    run(app, host="127.0.0.1", port=8000)
