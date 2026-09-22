import sqlite3
import os

DATABASE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "database.db"
)

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    eco_points INTEGER DEFAULT 0,
    last_login TEXT,
    account_status TEXT DEFAULT 'Active',
    failed_attempts INTEGER DEFAULT 0,
    locked_until TEXT
)
""")

columns = cursor.execute(
    "PRAGMA table_info(students)"
).fetchall()

column_names = [column[1] for column in columns]

if "last_login" not in column_names:
    cursor.execute(
        "ALTER TABLE students ADD COLUMN last_login TEXT"
    )

if "account_status" not in column_names:
    cursor.execute(
        "ALTER TABLE students ADD COLUMN account_status TEXT DEFAULT 'Active'"
    )

if "failed_attempts" not in column_names:
    cursor.execute(
        "ALTER TABLE students ADD COLUMN failed_attempts INTEGER DEFAULT 0"
    )

if "locked_until" not in column_names:
    cursor.execute(
        "ALTER TABLE students ADD COLUMN locked_until TEXT"
    )

if "eco_goal" not in column_names:
    cursor.execute(
        "ALTER TABLE students ADD COLUMN eco_goal INTEGER DEFAULT 100"
    )

cursor.execute("""
    UPDATE students
    SET account_status = 'Active'
    WHERE account_status IS NULL
""")

cursor.execute("""
    UPDATE students
    SET failed_attempts = 0
    WHERE failed_attempts IS NULL
""")

# ==========================================
# MEMBER 3: CHALLENGES & BADGES TABLES
# ==========================================
connection.execute('''
CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    points INTEGER NOT NULL
)
''')

connection.execute('''
CREATE TABLE IF NOT EXISTS challenge_participations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    challenge_id INTEGER NOT NULL
)
''')

connection.execute('''
CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    badge_name TEXT NOT NULL
)
''')
connection.commit()
connection.close()

print("Student database updated successfully.")