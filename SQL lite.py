import sqlite3

conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Drop the table if it exists to start fresh
cursor.execute("DROP TABLE IF EXISTS users")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
    )
    """)

cursor.execute("INSERT INTO users (name,email) VALUES (?,?)", ("Alice", "Alice@gmail.com"))
cursor.execute("INSERT INTO users (name, email) VALUES (?,?)", ("Bob", "Bob@gmail.com"))
conn.commit()

cursor.execute("""
CREATE TABLE products (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)""")


cursor.execute("INSERT INTO products (name, price, user_id) VALUES (?, ?, ?)", ("Apple", 1.99, 1))
cursor.execute("INSERT INTO products (name, price, user_id) VALUES (?, ?, ?)", ("Banana", 0.99, 2))


cursor.execute("UPDATE users SET name = ? WHERE id = ?", ("Abed", 1))
conn.commit()

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.execute("SELECT * FROM products JOIN users ON products.user_id = users.id")
rows2 = cursor.fetchall()
for row in rows2:
    print(row)  
conn.close()