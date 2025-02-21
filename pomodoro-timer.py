import time
import sys
from tqdm import tqdm
import csv
import uuid
from datetime import datetime

def save_session_to_csv(session_id, session_type, cycle_number, start_time, end_time):
    """Saves session data to pomo-tracker.csv."""
    file_exists = False
    try:
        with open('pomo-tracker.csv', 'r', newline='') as csvfile:
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    with open('pomo-tracker.csv', 'a', newline='') as csvfile:
        fieldnames = ['session_id', 'session_type', 'cycle_number', 'start_time', 'end_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            'session_id': session_id,
            'session_type': session_type,
            'cycle_number': cycle_number,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        })

def pomodoro_timer(work_duration=25, break_duration=5, cycles=2):
    for cycle in range(1, cycles + 1):
        print(f"\nCycle {cycle} of {cycles}")
        
        # Work Session
        session_id = str(uuid.uuid4())
        start_time = datetime.now()
        print("Work time! Stay focused! 🍅 (Press 's' to skip)")
        if not countdown(work_duration * 60):
            end_time = datetime.now()
            save_session_to_csv(session_id, 'work', cycle, start_time, end_time)
            if cycle < cycles:
                print("Break time! Relax a bit. ☕ (Press 's' to skip)")
                if not countdown(break_duration * 60):
                    continue
            continue
        end_time = datetime.now()
        save_session_to_csv(session_id, 'work', cycle, start_time, end_time)

        if cycle < cycles:
            # Break Session
            session_id = str(uuid.uuid4())
            start_time = datetime.now()
            print("Break time! Relax a bit. ☕ (Press 's' to skip)")
            if not countdown(break_duration * 60):
                end_time = datetime.now()
                save_session_to_csv(session_id, 'break', cycle, start_time, end_time)
                continue
            end_time = datetime.now()
            save_session_to_csv(session_id, 'break', cycle, start_time, end_time)
        else:
            print("\nAll Pomodoro cycles completed! Great job! 🎉")
            session_id = str(uuid.uuid4())
            start_time = datetime.now()
            end_time = datetime.now()
            save_session_to_csv(session_id, 'completion', cycle, start_time, end_time)

def countdown(duration):
    with tqdm(total=duration, desc="Time Remaining", bar_format='{l_bar}{bar} | {remaining}') as pbar:
        for remaining in range(duration, 0, -1):
            time.sleep(1)
            pbar.update(1)
            if skip_check():
                pbar.close()
                print("\nSession skipped!")
                return False
    print("\nTime's up!")
    return True

def skip_check():
    if sys.platform.startswith('win'):
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 's':
                return True
    else:
        import select
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1).lower()
            if key == 's':
                return True
    return False

if __name__ == "__main__":
    print("Welcome to the Pomodoro Timer!")
    work_minutes = int(input("Enter work duration in minutes (default 25): ") or 25)
    break_minutes = int(input("Enter break duration in minutes (default 5): ") or 5)
    total_cycles = int(input("Enter number of cycles (default 2): ") or 2)

    pomodoro_timer(work_minutes, break_minutes, total_cycles)