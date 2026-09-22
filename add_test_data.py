import sqlite3
import os

DATABASE = os.path.join(os.path.dirname(__file__), "database.db")
connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

cursor.execute("INSERT INTO challenges (title, description, category, points) VALUES (?, ?, ?, ?)", 
               ("Plastic Free Week", "Use zero single-use plastics for 7 days.", "Recycling", 50))
cursor.execute("INSERT INTO challenges (title, description, category, points) VALUES (?, ?, ?, ?)", 
               ("Plant a Tree", "Plant a sapling on campus or in your neighborhood.", "Planting", 100))

connection.commit()
connection.close()
print("Test challenges added!")
