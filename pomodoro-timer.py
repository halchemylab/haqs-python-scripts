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
from rich.live import Live
from rich.align import Align
from rich.layout import Layout
from rich.padding import Padding

# --- Global Console ---
console = Console()

def pomodoro_timer(work_duration=25, break_duration=5, long_break_duration=15, cycles=4, long_break_interval=4, user_name="User"):
    total_sessions = get_user_session_count(user_name)
    console.print(Panel(Text(f"Welcome back, {user_name}! You have completed {total_sessions} sessions so far.", justify="center"), title="[bold green]Pomodoro Timer[/bold green]"))

    for cycle in range(1, cycles + 1):
        # --- Work Session ---
        start_time = datetime.now()
        session_complete = countdown('work', work_duration * 60, cycle, cycles)
        if session_complete:
            end_time = datetime.now()
            log_session(user_name, 'work', start_time, end_time, work_duration)
            total_sessions += 1
            track_achievements(user_name, total_sessions)
            
            is_long_break = cycle % long_break_interval == 0
            break_msg = f"Time for a long {long_break_duration}-minute break." if is_long_break else f"Time for a {break_duration}-minute break."
            notification.notify(title='Work Session Over', message=break_msg)

            if cycle < cycles:
                # --- Break Session ---
                if is_long_break:
                    countdown('long_break', long_break_duration * 60, cycle, cycles)
                else:
                    countdown('break', break_duration * 60, cycle, cycles)
                notification.notify(title='Break Over', message='Time to get back to work!')
        else: # Session was skipped
            console.print(Text("Session skipped.", style="yellow"), justify="center")
            # If a work session is skipped, we also skip the following break
            if cycle < cycles:
                console.print(Text("Skipping the following break.", style="yellow"), justify="center")
                continue


    console.print(Panel(Text(f"All {cycles} pomodoro cycles completed! Great job, {user_name}! 🎉", justify="center"), title="[bold green]Finished![/bold green]"))
    notification.notify(title='Pomodoro Complete', message=f'All {cycles} cycles completed! Great job!')


def countdown(session_type, duration, current_cycle, total_cycles):
    paused = False
    
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=50),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
    )
    task = progress.add_task("Time Remaining", total=duration)

    title_styles = {
        'work': "[bold red]Work Session",
        'break': "[bold green]Short Break",
        'long_break': "[bold blue]Long Break"
    }
    title = title_styles.get(session_type, "Session")
    
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(ratio=1, name="main")
    )

    def get_display():
        header_text = Text(f"{title} | Cycle {current_cycle} of {total_cycles}", justify="center")
        main_content = Padding(Align.center(progress), (1, 0))
        
        if paused:
            header_text = Text(f"{title} [bold yellow][PAUSED][/bold yellow] | Cycle {current_cycle} of {total_cycles}", justify="center")

        layout["header"].update(header_text)
        layout["main"].update(main_content)
        return layout

    with Live(get_display(), console=console, screen=False, refresh_per_second=10) as live:
        while not progress.finished:
            user_input = handle_input()
            if user_input == 'skip':
                return False
            elif user_input == 'pause':
                paused = not paused
            
            if not paused:
                progress.update(task, advance=1)
                time.sleep(1)
            else:
                time.sleep(0.1) # Sleep briefly when paused to prevent high CPU usage
            
            live.update(get_display())

    return True


def handle_input():
    if sys.platform.startswith('win'):
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 's': return 'skip'
            if key == 'p': return 'pause'
    else: # For macOS and Linux
        import select
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1).lower()
            if key == 's': return 'skip'
            if key == 'p': return 'pause'
    return None

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

def get_integer_input(prompt, default):
    while True:
        user_input = console.input(f"[bold cyan]{prompt}[/bold cyan]")
        if not user_input:
            return default
        try:
            return int(user_input)
        except ValueError:
            console.print("[bold red]Invalid input. Please enter a whole number.[/bold red]")

if __name__ == "__main__":
    try:
        console.clear()
        console.print(Panel(Text("Welcome to the Pomodoro Timer!", justify="center")))
        user_name = console.input("[bold cyan]Enter your name (default: User): [/bold cyan]") or "User"
        work_minutes = get_integer_input("Enter work duration in minutes (default 25): ", 25)
        break_minutes = get_integer_input("Enter short break duration in minutes (default 5): ", 5)
        long_break_minutes = get_integer_input("Enter long break duration in minutes (default 15): ", 15)
        total_cycles = get_integer_input("Enter number of cycles (default 4): ", 4)
        long_break_interval = get_integer_input("Enter long break interval (default 4 cycles): ", 4)
        
        console.clear()
        pomodoro_timer(work_minutes, break_minutes, long_break_minutes, total_cycles, long_break_interval, user_name)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Timer cancelled. Goodbye![/bold yellow]")
