import sqlite3

connection = sqlite3.connect("database.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    eco_points INTEGER DEFAULT 0,
    last_login TEXT
)
""")

# Add last_login to existing databases if it is not already present
columns = cursor.execute("PRAGMA table_info(students)").fetchall()

column_names = [column[1] for column in columns]

if "last_login" not in column_names:
    cursor.execute("ALTER TABLE students ADD COLUMN last_login TEXT")

connection.commit()
connection.close()

print("Student table created/updated successfully.")