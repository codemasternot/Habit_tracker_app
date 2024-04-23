from habit import Habit
import click
import sqlite3
from datetime import datetime, timedelta
import database

#For when we use the CLI, as a back up CLI. Basically does the same as what is in the main function.
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
# In the main everything does pretty much it it says or what it's name is
def main():
    database.create_db()
    print('If you did not know, a habit takes on average 66 days to establish. However to break a habit research suggests takes between 18 and 254 days.')
    action = input('What do you want to do with habits? Add, Remove, list, streaks, mark as complete or exit. ')
    #if add:
    if action == 'Add' or action == 'add':
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
