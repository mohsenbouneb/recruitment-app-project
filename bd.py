import sqlite3

# Connect to the database
conn = sqlite3.connect("recrutement.db")
cursor = conn.cursor()

# Create or update the `candidats` table with an auto-incrementing primary key `id`
cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        experience INTEGER,
        diplome INTEGER,
        competences_techniques INTEGER,
        qualites_humaines INTEGER,
        mobilite INTEGER,
        score INTEGER,
        categorie TEXT
    )
''')

# Create or update the `users` table with an auto-incrementing primary key `id`
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

# Commit changes and close the connection
conn.commit()
conn.close()
