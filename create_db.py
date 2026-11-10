import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    email TEXT,
    security_question TEXT,
    security_answer TEXT
)
""")

cursor.execute("""
INSERT INTO users
(username,password,email,security_question,security_answer)
VALUES
(
'deepak',
'123456',
'deepakgaur9115@gmail.com',
'What is your favourite colour?',
'blue'
)
""")

conn.commit()
conn.close()

print("Database Created")