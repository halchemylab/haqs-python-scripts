import time
import sys
import csv
from datetime import datetime
import os
from plyer import notification
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

# --- Global Console ---
console = Console()

def handle_input():
    if sys.platform.startswith('win'):
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 's':
                return 'skip'
    else:  # For macOS and Linux
        import select
        import termios
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1).lower()
            if key == 's':
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                return 'skip'
    return None

def pomodoro_timer(work_duration=25, break_duration=5, long_break_duration=15, cycles=4, long_break_interval=4, user_name="User"):
    total_sessions = get_user_session_count(user_name)
    console.print(Panel(Text(f"Welcome back, {user_name}! You have completed {total_sessions} sessions so far.", justify="center"), title="[bold green]Pomodoro Timer[/bold green]"))

    # Display cycle sequence
    cycle_sequence = []
    for i in range(1, cycles + 1):
        cycle_sequence.append(f"Work ({work_duration} min)")
        if i < cycles:
            if i % long_break_interval == 0:
                cycle_sequence.append(f"Long Break ({long_break_duration} min)")
            else:
                cycle_sequence.append(f"Break ({break_duration} min)")
    
    console.print(Panel(Text(" -> ".join(cycle_sequence), justify="center"), title="[bold yellow]Cycle Sequence[/bold yellow]"))
    console.print("[bold cyan]Press 's' at any time to skip the current session.[/bold cyan]")

    for cycle in range(1, cycles + 1):
        # --- Work Session ---
        console.print(f"\n--- Cycle {cycle} of {cycles} ---")
        start_time = datetime.now()
        session_complete = countdown('work', work_duration * 60, cycle, cycles)
        
        if session_complete:
            end_time = datetime.now()
            log_session(user_name, 'work', start_time, end_time, work_duration)
            total_sessions += 1
            track_achievements(user_name, total_sessions)
            console.print(f"[bold green]Work session {cycle} complete![/bold green]")
            break_msg = f"Time for a long {long_break_duration}-minute break." if cycle % long_break_interval == 0 else f"Time for a {break_duration}-minute break."
        else:
            console.print(f"[bold yellow]Work session {cycle} skipped.[/bold yellow]")
            break_msg = "Work session skipped."

        is_long_break = cycle % long_break_interval == 0
        notification.notify(title='Work Session Over', message=break_msg)

        if cycle < cycles:
            console.input(f"\n[bold cyan]Press Enter to start your {'long' if is_long_break else 'short'} break...[/bold cyan]")
            # --- Break Session ---
            if is_long_break:
                break_complete = countdown('long_break', long_break_duration * 60, cycle, cycles)
            else:
                break_complete = countdown('break', break_duration * 60, cycle, cycles)
            
            if break_complete:
                console.print("[bold green]Break over![/bold green]")
            else:
                console.print("[bold yellow]Break skipped.[/bold yellow]")

            notification.notify(title='Break Over', message='Time to get back to work!')
            
            if cycle + 1 <= cycles:
                console.input("\n[bold cyan]Press Enter to start the next work session...[/bold cyan]")

    console.print(Panel(Text(f"All {cycles} pomodoro cycles completed! Great job, {user_name}! 🎉", justify="center"), title="[bold green]Finished![/bold green]"))
    notification.notify(title='Pomodoro Complete', message=f'All {cycles} cycles completed! Great job!')


def countdown(session_type, duration, current_cycle, total_cycles):
    title_styles = {
        'work': f"[bold red]Work Session {current_cycle}/{total_cycles}",
        'break': f"[bold green]Short Break {current_cycle}/{total_cycles}",
        'long_break': f"[bold blue]Long Break {current_cycle}/{total_cycles}"
    }
    title = title_styles.get(session_type, "Session")

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(title, total=duration)
        for _ in range(duration):
            if handle_input() == 'skip':
                return False # Skipped
            progress.update(task, advance=1)
            time.sleep(1)
    return True # Completed

def get_user_session_count(user_name, file_path='pomodoro_achievements.csv'):
    if not os.path.exists(file_path): return 0
    with open(file_path, 'r', newline='') as file:
        try:
            reader = csv.reader(file)
            next(reader, None) # Skip header
            return sum(1 for row in reader if row and row[0] == user_name)
        except (IOError, StopIteration):
            return 0

def track_achievements(user_name, total_sessions, file_path='pomodoro_achievements.csv'):
    achievements = {
        5: "🥉 Bronze Tomato: Complete 5 sessions",
        10: "🥈 Silver Tomato: Complete 10 sessions",
        20: "🥇 Gold Tomato: Complete 20 sessions",
        50: "👑 Pomodoro Master: Complete 50 sessions"
    }
    if total_sessions in achievements:
        message = achievements[total_sessions]
        console.print(Panel(f"🎉 [bold yellow]Achievement Unlocked![/bold yellow] 🎉\n{message}", title="Congratulations!"))
        notification.notify(title='Achievement Unlocked!', message=f'{user_name}, you unlocked: {message}')
        
        file_exists = os.path.exists(file_path)
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

if __name__ == "__main__":
    try:
        user_name = "henry"
        work_minutes = 25
        break_minutes = 5
        long_break_minutes = 15
        total_cycles = 4
        long_break_interval = 2
        
        pomodoro_timer(work_minutes, break_minutes, long_break_minutes, total_cycles, long_break_interval, user_name)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Timer cancelled. Goodbye![/bold yellow]")