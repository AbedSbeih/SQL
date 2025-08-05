from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3


# -------- Database Setup --------
DB_NAME = "mydb.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Enables dict-like access
    return conn


# -------- Pydantic Models --------
class User(BaseModel):
    name: str
    email: str

class UserUpdate(BaseModel):
    name: str = None
    email: str = None


# -------- FastAPI App --------
app = FastAPI(title="FastAPI CRUD Example")


class UserAPI:

    @staticmethod
    @app.post("/users")
    def insert_user(user: User):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                           (user.name, user.email))
            conn.commit()
            return {"message": "User added successfully"}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Email already exists")
        finally:
            conn.close()

    @staticmethod
    @app.get("/users")
    def get_users():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    @app.put("/users/{user_id}")
    def update_user(user_id: int, user: UserUpdate):
        conn = get_connection()
        cursor = conn.cursor()

        # Build dynamic update query
        fields = []
        values = []
        if user.name:
            fields.append("name = ?")
            values.append(user.name)
        if user.email:
            fields.append("email = ?")
            values.append(user.email)

        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")

        values.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        conn.close()
        return {"message": "User updated successfully"}

    @staticmethod
    @app.delete("/users/{user_id}")
    def delete_user(user_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        conn.close()
        return {"message": "User deleted successfully"}


# -------- Database Table Creation --------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()
