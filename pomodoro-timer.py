import time
import sys
from tqdm import tqdm

def pomodoro_timer(work_duration=25, break_duration=5, cycles=2, user_name="User"):
    total_sessions = 0
    for cycle in range(1, cycles + 1):
        print(f"\nCycle {cycle} of {cycles}")
        
        # Work Session
        print(f"Work time! Stay focused, {user_name}! 🍅 (Press 's' to skip)")
        if not countdown(work_duration * 60):
            if cycle < cycles:
                print(f"Break time! Relax a bit, {user_name}. ☕ (Press 's' to skip)")
                if not countdown(break_duration * 60):
                    continue
            continue

        if cycle < cycles:
            # Break Session
            print(f"Break time! Relax a bit, {user_name}. ☕ (Press 's' to skip)")
            if not countdown(break_duration * 60):
                continue
        else:
            print(f"\nAll Pomodoro cycles completed! Great job, {user_name}! 🎉")
        total_sessions += 1
        track_achievements(total_sessions)


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

def track_achievements(total_sessions):
    achievements = {
        5: "🥉 Bronze Tomato: Complete 5 sessions",
        10: "🥈 Silver Tomato: Complete 10 sessions",
        20: "🥇 Gold Tomato: Complete 20 sessions",
        50: "👑 Pomodoro Master: Complete 50 sessions"
    }
    
    for sessions, message in achievements.items():
        if total_sessions == sessions:
            print(f"\n🎉 Achievement Unlocked! {message}")

if __name__ == "__main__":
    print("Welcome to the Pomodoro Timer!")
    user_name = input("Enter your name: ") or "User"
    work_minutes = int(input("Enter work duration in minutes (default 25): ") or 25)
    break_minutes = int(input("Enter break duration in minutes (default 5): ") or 5)
    total_cycles = int(input("Enter number of cycles (default 2): ") or 2)

    pomodoro_timer(work_minutes, break_minutes, total_cycles, user_name)