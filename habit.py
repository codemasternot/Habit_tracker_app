#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sqlite3
from datetime import datetime, timedelta 

class Habit:
    def __init__(self, id, name, period, created_at):
        self.id = id
        self.name = name
        self.period = period
        self.created_at = created_at

    def complete_task(self):
        self.completed_at = datetime.now()

    def task_incomplete(self):
        if self.completed_at:
            self.completed_at.pop()

    def is_streak_continuing(self):
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

    def check_streaks(habits):
        for habit_tuple in habits:
            name = habit_tuple[1]
            period = habit_tuple[2]
            habit = Habit.get_habit_by_name(name)
            streak_count = habit.is_streak_continuing()
            print(f"{habit.name}: Streak count: {streak_count}")

    def get_habit_by_name(name):
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM habits WHERE name = ?", (name,))
        habit = cur.fetchone()
        cur.close()
        conn.close()
        if habit:
            return Habit(habit[0], habit[1], habit[2], habit[3])
        return None

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

    def fetch_all_habits():
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM habits")
        habits = cur.fetchall()
        cur.close()
        conn.close()
        return habits
    
    def mark_streaks(habit_name):
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()

        habit_id = get_habit_id_by_name(habit_name)

        if habit_id is None:
            print(f"Habit '{habit_name}' not found.")
            return

        cur.execute("SELECT period FROM habits WHERE id = ?", (habit_id,))
        period = cur.fetchone()[0]

        if period == 'daily':
            last_completion_date = cur.execute("SELECT MAX(date) FROM streaks WHERE habit_id = ?", (habit_id,)).fetchone()[0]
            if last_completion_date and last_completion_date == datetime.now().strftime('%Y-%m-%d'):
                streak_count = cur.execute("SELECT completed FROM streaks WHERE habit_id = ? ORDER BY date DESC LIMIT 1", (habit_id,)).fetchone()[0]
                cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                            (habit_id, datetime.now(), streak_count + 1, period))
                print(f"Streak marked for habit '{habit_name}'")
            else:
                cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                            (habit_id, datetime.now(), 1, period))
                print(f"Streak broken for habit '{habit_name}'")
        elif period == 'weekly':
            last_completion_date = cur.execute("SELECT MAX(date) FROM streaks WHERE habit_id = ?", (habit_id,)).fetchone()[0]
            if last_completion_date:
                last_completion_date = last_completion_date.split()[0]
                if datetime.strptime(last_completion_date, "%Y-%m-%d").isocalendar()[1] == datetime.now().isocalendar()[1]:
                    streak_count = cur.execute("SELECT completed FROM streaks WHERE habit_id = ? ORDER BY date DESC LIMIT 1", (habit_id,)).fetchone()[0]
                    cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                                (habit_id, datetime.now(), streak_count + 1, period))
                    print(f"Streak marked for habit '{habit_name}'")
                else:
                    cur.execute("INSERT INTO streaks (habit_id, date, completed, period) VALUES (?, ?, ?, ?)",
                                (habit_id, datetime.now(), 1, period))
                    print(f"Streak broken for habit '{habit_name}'")
            else:
                print(f"No last completion date found for habit '{habit_name}'")

        conn.commit()
        conn.close()

    def add_habit(n, per):
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM habits")
        num_entries = cur.fetchone()[0] + 1

        new_habit = (num_entries, n, per, datetime.now())
        cur.execute("SELECT * FROM habits WHERE name = ?", (n,))
        existing_habit = cur.fetchone()

        if existing_habit:
            print(f"Habit '{n}' already exists, skipping insertion.")
        else:
            cur.execute("INSERT INTO habits (id, name, period, created_at) VALUES (?, ?, ?, ?)", new_habit)
            print(f"Habit '{n}' added successfully.")
        conn.commit()
        cur.close()
        conn.close()

    def remove_habit(name):
        conn = sqlite3.connect("mydb.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM habits WHERE name = ?", (name,))
        existing_habit = cur.fetchone()

        if existing_habit:
            cur.execute("DELETE FROM habits WHERE name = ?", (name,))
            print(f"Habit '{name}' removed successfully.")
            cur.execute("UPDATE habits SET id = id - 1 WHERE id > ?", (existing_habit[0],))
        else:
            print(f"Habit '{name}' does not exist in the database.")

        conn.commit()
        cur.close()
        conn.close()


# In[ ]:




