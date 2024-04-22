#!/usr/bin/env python
# coding: utf-8

# In[87]:


import json
import pandas as pd
import numpy as np
import database as db
from datetime import datetime, timedelta 
import sqlite3
import time
import click
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
# Create the streaks table if it doesn't exist
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
# Adds a completed column to the streaks table
if 'completed' not in [col[1] for col in cur.fetchall()]:
    cur.execute('''
        ALTER TABLE streaks ADD COLUMN completed INTEGER NOT NULL DEFAULT 0;
    ''')
# Dummy data to insert into habits
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

# Fetch all rows
rows = cur.fetchall()

# Print the rows for testing
#for row in rows:
    #print(row)

# Commit changes and close cursor/connection
conn.commit()
cur.close()
conn.close()
# Define habit class
class Habit:
     def __init__(self, id, name, period, created_at):
        self.id = id
        self.name = name
        self.period = period
        self.created_at = created_at
     # Marks task as complete at current time
     def complete_task(self):
        self.completed_at = datetime.now()
     # Marks as incomplete
     def task_incomplete(self):
        if self.completed_at:
            self.completed_at.pop()
     
     def is_streak_continuing(self):
         # Is streak for Habit continuing
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        if self.period == 'daily':
            streak_check_query = "SELECT COUNT(*) FROM streaks WHERE habit_id = ? AND date >= ?"
            period_days = 1
        elif self.period == 'weekly':
            streak_check_query = "SELECT COUNT(*) FROM streaks WHERE habit_id = ? AND date >= ?"
            period_days = 7

        habit_id = self.id
        streak_check_result = cur.execute(streak_check_query, (habit_id, datetime.now() - timedelta(days=period_days))).fetchone()
        streak_count = streak_check_result[0] if streak_check_result else 0
        conn.close()
        return streak_count
     # Check streaks for habits
     def check_streaks(habits):
        for habit_tuple in habits:
            name = habit_tuple[1]
            period = habit_tuple[2]
            habit = Habit.get_habit_by_name(name)
            streak_count = habit.is_streak_continuing()
            print(f"{habit.name}: Streak count: {streak_count}")
     # Get's Habit entry by name
     def get_habit_by_name(name):
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM habits WHERE name = ?", (name,))
        habit = cur.fetchone()
        cur.close()
        conn.close()
        if habit:
            return Habit(habit[0], habit[1], habit[2], habit[3])  # Include id and created_at when creating Habit object
        return None
     # Get's streak count for specific habit
     def get_streak_count(self):
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        if self.period == 'daily':
            streak_check_query = "SELECT COUNT(*) FROM streaks WHERE habit_id = ? AND date >= ?"
            period_days = 1
        elif self.period == 'weekly':
            streak_check_query = "SELECT COUNT(*) FROM streaks WHERE habit_id = ? AND date >= ?"
            period_days = 7
            
        habit_id = self.id
        streak_check_result = cur.execute(streak_check_query, (habit_id, datetime.now() - timedelta(days=period_days))).fetchone()
        streak_count = streak_check_result[0] if streak_check_result else 0
        conn.close()
        return streak_count

     # Get's longest streak of all habits
     def get_longest_streak(habit_name):
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        cur.execute("SELECT period, id FROM habits WHERE name = ?", (habit_name,))
        result = cur.fetchone()
        if result:
            period, habit_id = result
            if period == 'daily':
                streak_check_query = "SELECT COUNT(*) FROM streaks WHERE habit_id = ? AND date >= ?"
                period_days = 1
            elif period == 'weekly':
                streak_check_query = "SELECT COUNT(*) FROM streaks WHERE habit_id = ? AND date >= ?"
                period_days = 7

            streak_check_result = cur.execute(streak_check_query, (habit_id, datetime.now() - timedelta(days=period_days))).fetchone()
            streak_count = streak_check_result[0] if streak_check_result else 0

            conn.close()
            return streak_count
        else:
            return None
     # Fetches all the habits
     def fetch_all_habits():
         conn = sqlite3.connect("mydb.db")
         cur = conn.cursor()
         cur.execute("SELECT * FROM habits")
         habits = cur.fetchall()
         cur.close()
         conn.close()
         return habits
        
     def mark_streaks(habit_name):
         # Get's habit id buy name
         conn = sqlite3.connect("mydb.db")
         cur = conn.cursor()

    # Get the habit ID by name
         habit_id = get_habit_id_by_name(habit_name)

         if habit_id is None:
             print(f"Habit '{habit_name}' not found.")
             return

    # Get the period of the habit from the habits table
         cur.execute("SELECT period FROM habits WHERE id = ?", (habit_id,))
         period = cur.fetchone()[0]

    # Check if the habit was completed within the required period
    # Update streaks table with the streak count for testing
    #cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)", 
                #(habit_id, datetime.now(), 1, period))
    #print(f"Streak marked for habit '{habit_name}'")
         if period == 'daily':
             last_completion_date = cur.execute("SELECT MAX(date) FROM streaks WHERE habit_id = ?", (habit_id,)).fetchone()[0]
             if last_completion_date and last_completion_date == datetime.now().strftime('%Y-%m-%d'):
            # Habit was completed today, update streak count
                 streak_count = cur.execute("SELECT completed FROM streaks WHERE habit_id = ? ORDER BY date DESC LIMIT 1", (habit_id,)).fetchone()[0]
                 cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                             (habit_id, datetime.now(), streak_count + 1, period))
                 print(f"Streak marked for habit '{habit_name}'")
             else:
            # Habit was not completed today, streak broken
                 cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                             (habit_id, datetime.now(), 1, period))  # Include the period here
                 print(f"Streak broken for habit '{habit_name}'")
         elif period == 'weekly':
             last_completion_date = cur.execute("SELECT MAX(date) FROM streaks WHERE habit_id = ?", (habit_id,)).fetchone()[0]
             if last_completion_date:
        # Extract date part from the datetime string
                 last_completion_date = last_completion_date.split()[0]
                 if datetime.strptime(last_completion_date, "%Y-%m-%d").isocalendar()[1] == datetime.now().isocalendar()[1]:
            # Habit was completed this week, update streak count
                     streak_count = cur.execute("SELECT completed FROM streaks WHERE habit_id = ? ORDER BY date DESC LIMIT 1", (habit_id,)).fetchone()[0]
                     cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                             (habit_id, datetime.now(), streak_count + 1, period))
                     print(f"Streak marked for habit '{habit_name}'")
                 else:
            # Habit was not completed this week, streak broken
                     cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                             (habit_id, datetime.now(), 1, period))  # Include the period here
                     print(f"Streak broken for habit '{habit_name}'")
                
             else:
                 print(f"No last completion date found for habit '{habit_name}'")
                
         conn.commit()
         conn.close()
            
     def add_habit(n, per):
         conn = sqlite3.connect("mydb.db")
         cur = conn.cursor()
    
    # Fetching the number of entries to determine the new habit ID
         cur.execute("SELECT COUNT(*) FROM habits")
         num_entries = cur.fetchone()[0] + 1

    # Creating a tuple for the new habit
         new_habit = (num_entries, n, per, datetime.now())
         cur.execute("SELECT * FROM habits WHERE name = ?", (n,))
         existing_habit = cur.fetchone()

         if existing_habit:
             print(f"Habit '{n}' already exists, skipping insertion.")
         else:
            # Inserting the new habit into the database
             cur.execute("INSERT INTO habits (id, name, period, created_at) VALUES (?, ?, ?, ?)", new_habit)
             print(f"Habit '{n}' added successfully.")
         conn.commit()
         cur.close()
         conn.close()

    
     def remove_habit(name):
         conn = sqlite3.connect("mydb.db")
         cur = conn.cursor()
    
    # Check if the habit exists
         cur.execute("SELECT * FROM habits WHERE name = ?", (name,))
         existing_habit = cur.fetchone()
    
         if existing_habit:
        # If the habit exists, remove it from the database
             cur.execute("DELETE FROM habits WHERE name = ?", (name,))
             print(f"Habit '{name}' removed successfully.")
        
        # Update IDs after deletion
             cur.execute("UPDATE habits SET id = id - 1 WHERE id > ?", (existing_habit[0],))
         else:
             print(f"Habit '{name}' does not exist in the database.")
    
    # Commit changes
         conn.commit()
    
    # Close cursor and connection
         cur.close()
         conn.close()
def get_habit_id_by_name(name):
    conn = sqlite3.connect("mydb.db")
    cur = conn.cursor()
    cur.execute("SELECT id FROM habits WHERE name = ?", (name,))
    habit_id = cur.fetchone()
    cur.close()
    conn.close()
    return habit_id[0] if habit_id else None
    

#For when we use the CLI, but as we want to see the input we will use normal input for now.
#@click.command()
#@click.option('--add', is_flag=True, help='Add a new habit')
#@click.option('--remove', is_flag=True, help='Remove an existing habit')
#@click.option('--list', is_flag=True, help='List all habits')
#@click.option('--streaks', is_flag=True, help='Check streaks for a specific habit')
#@click.option('--complete', is_flag=True, help='Mark a habit as complete')
#@click.option('--longeststreak', is_flag=True, help='Find the habit with the longest streak')
#@click.option('--exit', is_flag=True, help='Exit the program')
#def main(add, remove, list, streaks, complete, longeststreak):
#We will put all code related to cli as comments for now as so far this is just for testing and no clickable buttons have been added.
def main():
    print('If you did not know, a habit takes on average 66 days to establish. However to break a habit research suggests takes between 18 and 254 days.')
    action = input('What do you want to do with habits? Add, Remove, list, streaks, mark as complete or exit. ')
    #if add:
    if action == 'Add' or action =='add':
        name = input('What is the habit you want to add? ')
        period = input('Is it daily or weekly? ')
        gb = input('Would you consider it a good or bad habit ')
        habits = Habit.add_habit(name, period)
    #elif remove:
    elif action == 'Remove' or action == 'remove':
        name = input('What is the habit you want to Remove? ')
        habits = Habit.remove_habit(name)
    #elif list:
    elif action == 'list':
        habits = Habit.fetch_all_habits()
        for habit in habits:
                print(habit)
    #elif streaks:
    elif action == 'streaks':
        name = input("What is the name of the habit streak you want to check? ")
        habit = Habit.get_habit_by_name(name)
        if habit:
            streak_count = habit.get_streak_count()
            print(f"{habit.name}: Streak count: {streak_count}")
        else:
            print(f"Habit '{name}' not found.")
    #elif complete:
    elif action == 'mark as complete':
        name = input("What is the name of the habit you want to mark as complete? ")
        Habit.mark_streaks(name)
        print(f"{name} marked as complete.")
    #elif longeststreak:
    elif action == 'longest streak':
        habits = Habit.fetch_all_habits()
        longest_streak = 0
        habit_with_longest_streak = None
        for habit in habits:
            if habit:
                habit_name = habit[1]
                streak = Habit.get_longest_streak(habit_name)
                if streak is not None and streak > longest_streak:
                    longest_streak = streak
                    habit_with_longest_streak = habit_name
        if longest_streak > 0:
            print(f"The longest streak is: {longest_streak}, for habit named {habit_with_longest_streak}")
        else:
            print("No streak recorded for any habit.")
    #elif exit
    elif action == 'exit':
        print('You have chosen to exit. ')
    
if __name__ == "__main__":
    main()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




