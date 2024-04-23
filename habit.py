#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sqlite3
from datetime import datetime, timedelta 

class Habit: # Define habit class
    def __init__(self, id, name, period, created_at): # Initializing the habit object
        self.id = id # Assign habit ID
        self.name = name # Assign habit name
        self.period = period
        self.created_at = created_at

    def complete_task(self): # Marks task as complete at current time
        self.completed_at = datetime.now()

    def task_incomplete(self): # Marks as incomplete
        if self.completed_at:
            self.completed_at.pop() # pop removes

    def is_streak_continuing(self): # Is streak for Habit continuing
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        if self.period == 'daily':
            streak_check_query = "SELECT COUNT(*) FROM streaks WHERE habit_id = ? AND date >= ?" # Counts number of streaks for the period
            period_days = 1
        elif self.period == 'weekly':
            streak_check_query = "SELECT COUNT(*) FROM streaks WHERE habit_id = ? AND date >= ?" # Counts number of streaks for the period
            period_days = 7

        habit_id = self.id
        streak_check_result = cur.execute(streak_check_query, (habit_id, datetime.now() - timedelta(days=period_days))).fetchone() # Checks query with habit id and date
        streak_count = streak_check_result[0] if streak_check_result else 0 # Streak result of query
        conn.close()
        return streak_count

    def check_streaks(habits): # Check streaks for habits
        for habit_tuple in habits:
            name = habit_tuple[1] # Habit name from tuple
            period = habit_tuple[2] # Habit period from tuple
            habit = Habit.get_habit_by_name(name)
            streak_count = habit.is_streak_continuing()
            print(f"{habit.name}: Streak count: {streak_count}") # Prints habit name and streak count

    def get_habit_by_name(name): # Get's Habit entry by name
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM habits WHERE name = ?", (name,))
        habit = cur.fetchone()
        cur.close()
        conn.close()
        if habit:
            return Habit(habit[0], habit[1], habit[2], habit[3]) # Include id and created_at when creating Habit object
        return None

    def get_streak_count(self): # Get's streak count for specific habit
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        if self.period == 'daily':
            streak_check_query = "SELECT COUNT(*) FROM streaks WHERE habit_id = ? AND date >= ?" # Counts streaks for the habits
            period_days = 1
        elif self.period == 'weekly':
            streak_check_query = "SELECT COUNT(*) FROM streaks WHERE habit_id = ? AND date >= ?"
            period_days = 7
            
        habit_id = self.id
        streak_check_result = cur.execute(streak_check_query, (habit_id, datetime.now() - timedelta(days=period_days))).fetchone() # Query to count the habit streaks
        streak_count = streak_check_result[0] if streak_check_result else 0 # Streak count for query result
        conn.close()
        return streak_count

    def get_longest_streak(habit_name): # Get's longest streak of all habits
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

    def fetch_all_habits(): # Fetches all the habits
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM habits")
        habits = cur.fetchall()
        cur.close()
        conn.close()
        return habits
    
    def mark_streaks(habit_name): # Get habit id buy name
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()

        habit_id = get_habit_id_by_name(habit_name) # Get the habit ID by name

        if habit_id is None:
            print(f"Habit '{habit_name}' not found.")
            return

        cur.execute("SELECT period FROM habits WHERE id = ?", (habit_id,)) # Get the period of the habit from the habits table
        period = cur.fetchone()[0] # Fetches period of habits and fetches results from query
        # Check if the habit was completed within the required period
        # Update streaks table with the streak count for testing
        #cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)", 
                    #(habit_id, datetime.now(), 1, period))
        #print(f"Streak marked for habit '{habit_name}'")
        if period == 'daily':
            last_completion_date = cur.execute("SELECT MAX(date) FROM streaks WHERE habit_id = ?", (habit_id,)).fetchone()[0]
            if last_completion_date and last_completion_date == datetime.now().strftime('%Y-%m-%d'):
                streak_count = cur.execute("SELECT completed FROM streaks WHERE habit_id = ? ORDER BY date DESC LIMIT 1", (habit_id,)).fetchone()[0]
                # Habit was completed today, update streak count
                cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                            (habit_id, datetime.now(), streak_count + 1, period))
                print(f"Streak marked for habit '{habit_name}'")
            else: # Habit was not completed today, streak broken
                cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                            (habit_id, datetime.now(), 1, period)) # Include the period here
                print(f"Streak broken for habit '{habit_name}'")
        elif period == 'weekly':
            last_completion_date = cur.execute("SELECT MAX(date) FROM streaks WHERE habit_id = ?", (habit_id,)).fetchone()[0]
            if last_completion_date:
                last_completion_date = last_completion_date.split()[0]  # Extract date part from the datetime string
                if datetime.strptime(last_completion_date, "%Y-%m-%d").isocalendar()[1] == datetime.now().isocalendar()[1]:  # Habit was completed this week, update streak count
                    streak_count = cur.execute("SELECT completed FROM streaks WHERE habit_id = ? ORDER BY date DESC LIMIT 1", (habit_id,)).fetchone()[0]
                    cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                                (habit_id, datetime.now(), streak_count + 1, period))
                    print(f"Streak marked for habit '{habit_name}'")
                else: # Habit was not completed this week, streak broken
                    cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                                (habit_id, datetime.now(), 1, period)) # Include the period here
                    print(f"Streak broken for habit '{habit_name}'")
            else:
                print(f"No last completion date found for habit '{habit_name}'")

        conn.commit()
        conn.close()

    def add_habit(n, per):  # Adds Habit
        # n would be name and per period
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        # Fetching the number of entries to determine the new habit ID
        cur.execute("SELECT COUNT(*) FROM habits")
        num_entries = cur.fetchone()[0] + 1
        # Allows us to add a new id
        # Creating a tuple for the new habit
        new_habit = (num_entries, n, per, datetime.now())
        cur.execute("SELECT * FROM habits WHERE name = ?", (n,)) # Selct if the habit exists
        existing_habit = cur.fetchone()

        if existing_habit: # Inserting the new habit into the database
            print(f"Habit '{n}' already exists, skipping insertion.")
        else: 
            cur.execute("INSERT INTO habits (id, name, period, created_at) VALUES (?, ?, ?, ?)", new_habit) 
            print(f"Habit '{n}' added successfully.")
        conn.commit()
        cur.close()
        conn.close()

    def remove_habit(name):  # Removes Habit
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
# Selct if the habit exists
        cur.execute("SELECT * FROM habits WHERE name = ?", (name,))
        existing_habit = cur.fetchone()

        if existing_habit: # If the habit exists, remove it from the database
            cur.execute("DELETE FROM habits WHERE name = ?", (name,))
            print(f"Habit '{name}' removed successfully.")
            cur.execute("UPDATE habits SET id = id - 1 WHERE id > ?", (existing_habit[0],)) # Fixes Id after deletion so it does not skip a number
        else:
            print(f"Habit '{name}' does not exist in the database.")

        conn.commit()
        cur.close()
        conn.close()
def get_habit_id_by_name(name):
    # Gets the habit id based on name
    conn = sqlite3.connect("mydb.db")
    cur = conn.cursor()
    cur.execute("SELECT id FROM habits WHERE name = ?", (name,))
    habit_id = cur.fetchone()
    cur.close()
    conn.close()
    return habit_id[0] if habit_id else None
# In[ ]:




