#!/usr/bin/env python
# coding: utf-8

# In[2]:


import sqlite3
from datetime import datetime
def create_db():
    #Create database and insert our five habits
    # Connect to the database
    conn = sqlite3.connect("mydb.db")
    cur = conn.cursor()
    #Wipe database if we need to
    #cur.execute("DROP TABLE IF EXISTS habits")
    # Create the habits table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            period TEXT NOT NULL,
            created_at DATETIME NOT NULL
        )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS streaks (
        id INTEGER PRIMARY KEY,
        habit_id INTEGER NOT NULL,
        date DATE NOT NULL,
        completed INTEGER NOT NULL,
        FOREIGN KEY (habit_id) REFERENCES habits(id)
    )
    ''')
    cur.execute(''' 
        PRAGMA table_info(streaks);
    ''')
    if 'completed' not in [col[1] for col in cur.fetchall()]:
        cur.execute('''
            ALTER TABLE streaks ADD COLUMN completed INTEGER NOT NULL DEFAULT 0;
        ''')
    # Define the habits to insert
    habits = [
        (1, 'Go to gym', 'daily', datetime.now()),
        (2, 'Brush teeth', 'daily', datetime.now()),
        (3, 'Drink two litres of water', 'daily', datetime.now()),
        (4, 'Call parents', 'weekly', datetime.now()),
        (5, 'Sleep 8 hours', 'daily', datetime.now()),
    ]

    # Insert the habits into the table if they don't already exist
    for habit in habits:
        name = habit[1]
        cur.execute("SELECT * FROM habits WHERE name = ?", (name,))
        existing_habit = cur.fetchone()
        if not existing_habit:
            cur.execute("INSERT INTO habits (id, name, period, created_at) VALUES (?, ?, ?, ?)", habit)

    # Query the habits table
    cur.execute("SELECT * FROM habits")

    # Fetch all rows from the result set
    rows = cur.fetchall()

    # Print the rows for testing
    #for row in rows:
        #print(row)

    # Commit changes and close cursor/connection
    conn.commit()
    cur.close()
    conn.close()


# In[ ]:




