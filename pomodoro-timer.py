import time
import sys
from tqdm import tqdm
import csv
from datetime import datetime
import os
from plyer import notification

def pomodoro_timer(work_duration=25, break_duration=5, long_break_duration=15, cycles=4, long_break_interval=4, user_name="User"):
    total_sessions = get_user_session_count(user_name)
    print(f"Welcome back, {user_name}! You have completed {total_sessions} sessions so far.")

    for cycle in range(1, cycles + 1):
        print(f"\nCycle {cycle} of {cycles}")
        
        # Work Session
        print(f"Work time! Stay focused, {user_name}! 🍅 (Press 's' to skip, 'p' to pause)")
        start_time = datetime.now()
        if countdown(work_duration * 60):
            end_time = datetime.now()
            log_session(user_name, 'work', start_time, end_time, work_duration)
            total_sessions += 1
            track_achievements(user_name, total_sessions)
            
            if cycle % long_break_interval == 0:
                notification.notify(
                    title='Pomodoro Timer',
                    message=f'Work session is over! Time for a long {long_break_duration}-minute break.',
                )
            else:
                notification.notify(
                    title='Pomodoro Timer',
                    message=f'Work session is over! Time for a {break_duration}-minute break.',
                )

        if cycle < cycles:
            # Break Session
            if cycle % long_break_interval == 0:
                print(f"Long break time! Relax and recharge, {user_name}. ☕ (Press 's' to skip, 'p' to pause)")
                if countdown(long_break_duration * 60):
                    notification.notify(
                        title='Pomodoro Timer',
                        message='Long break is over! Time to get back to work.',
                    )
            else:
                print(f"Break time! Relax a bit, {user_name}. ☕ (Press 's' to skip, 'p' to pause)")
                if countdown(break_duration * 60):
                    notification.notify(
                        title='Pomodoro Timer',
                        message='Break is over! Time to get back to work.',
                    )
        else:
            print(f"\nAll Pomodoro cycles completed! Great job, {user_name}! 🎉")
            notification.notify(
                title='Pomodoro Timer',
                message=f'All {cycles} pomodoro cycles completed! Great job!',
            )


def countdown(duration):
    paused = False
    with tqdm(total=duration, desc="Time Remaining", bar_format='{l_bar}{bar} | {remaining}') as pbar:
        for remaining in range(duration, 0, -1):
            while paused:
                time.sleep(0.1)
                user_input = handle_input()
                if user_input == 'pause':
                    paused = False
                    pbar.set_description("Time Remaining")
                    pbar.refresh()
            
            time.sleep(1)
            pbar.update(1)
            
            user_input = handle_input()
            if user_input == 'skip':
                pbar.close()
                print("\nSession skipped!")
                return False
            elif user_input == 'pause':
                paused = True
                pbar.set_description("Time Remaining [PAUSED]")
                pbar.refresh()

    print("\nTime's up!")
    return True


def handle_input():
    if sys.platform.startswith('win'):
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 's':
                return 'skip'
            elif key == 'p':
                return 'pause'
    else:
        import select
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1).lower()
            if key == 's':
                return 'skip'
            elif key == 'p':
                return 'pause'
    return None

def get_user_session_count(user_name, file_path='pomodoro_achievements.csv'):
    if not os.path.exists(file_path):
        return 0
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        # Skip header
        next(reader, None)
        count = sum(1 for row in reader if row and row[0] == user_name)
    return count

def track_achievements(user_name, total_sessions, file_path='pomodoro_achievements.csv'):
    achievements = {
        5: "🥉 Bronze Tomato: Complete 5 sessions",
        10: "🥈 Silver Tomato: Complete 10 sessions",
        20: "🥇 Gold Tomato: Complete 20 sessions",
        50: "👑 Pomodoro Master: Complete 50 sessions"
    }

    file_exists = os.path.exists(file_path)

    for sessions, message in achievements.items():
        if total_sessions == sessions:
            print(f"\n🎉 Achievement Unlocked for {user_name}! {message}")
            notification.notify(
                title='Achievement Unlocked!',
                message=f'{user_name}, you unlocked: {message}',
            )
            with open(file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists or file.tell() == 0:
                    writer.writerow(['user_name', 'achievement', 'timestamp'])
                writer.writerow([user_name, message, datetime.now().isoformat()])

def log_session(user_name, session_type, start_time, end_time, duration_minutes, file_path='session_log.csv'):
    file_exists = os.path.exists(file_path)
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists or file.tell() == 0:
            writer.writerow(['user_name', 'session_type', 'start_time', 'end_time', 'duration_minutes'])
        writer.writerow([user_name, session_type, start_time.isoformat(), end_time.isoformat(), duration_minutes])

def get_integer_input(prompt, default):
    while True:
        user_input = input(prompt)
        if not user_input:
            return default
        try:
            return int(user_input)
        except ValueError:
            print("Invalid input. Please enter a whole number.")

if __name__ == "__main__":
    print("Welcome to the Pomodoro Timer!")
    user_name = input("Enter your name: ") or "User"
    work_minutes = get_integer_input("Enter work duration in minutes (default 25): ", 25)
    break_minutes = get_integer_input("Enter short break duration in minutes (default 5): ", 5)
    long_break_minutes = get_integer_input("Enter long break duration in minutes (default 15): ", 15)
    total_cycles = get_integer_input("Enter number of cycles (default 4): ", 4)
    long_break_interval = get_integer_input("Enter long break interval (default 4 cycles): ", 4)

    pomodoro_timer(work_minutes, break_minutes, long_break_minutes, total_cycles, long_break_interval, user_name)