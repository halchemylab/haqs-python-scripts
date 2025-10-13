import time
import sys
import csv
import random
from datetime import datetime
import os
from plyer import notification
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
import configparser

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

def pomodoro_timer(work_duration, break_duration, long_break_duration, cycles, long_break_interval, user_name, quotes_file, achievements_log, session_log):
    total_sessions = get_user_session_count(user_name, achievements_log)
    console.print(Panel(Text(f"Welcome back, {user_name}! You have completed {total_sessions} sessions so far.", justify="center"), title="[bold green]Pomodoro Timer[/bold green]"))

    # Display a random motivational quote
    try:
        with open(quotes_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader) # Skip header
            quotes = list(reader)
            if quotes:
                random_quote = random.choice(quotes)
                quote_text = random_quote[0]
                author_text = random_quote[1]
                quote_display = f'"{quote_text}"\n- {author_text}'
                console.print(Panel(Text(quote_display, justify="center"), title="[bold yellow]Quote of the Session[/bold yellow]"))
    except FileNotFoundError:
        # If quotes_file is not found, do nothing and just continue.
        console.print(f"[bold red]Warning: Could not find quotes file at {quotes_file}[/bold red]")
        pass
    console.print("[bold cyan]Press 's' at any time to skip the current session.[/bold cyan]")

    for cycle in range(1, cycles + 1):
        # --- Work Session ---
        console.print(f"\n--- Cycle {cycle} of {cycles} ---")
        start_time = datetime.now()
        session_complete = countdown('work', work_duration * 60, cycle, cycles)
        
        if session_complete:
            end_time = datetime.now()
            log_session(user_name, 'work', start_time, end_time, work_duration, session_log)
            total_sessions += 1
            track_achievements(user_name, total_sessions, achievements_log)
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

def get_user_session_count(user_name, file_path):
    if not os.path.exists(file_path): return 0
    with open(file_path, 'r', newline='') as file:
        try:
            reader = csv.reader(file)
            next(reader, None) # Skip header
            return sum(1 for row in reader if row and row[0] == user_name)
        except (IOError, StopIteration):
            return 0

def track_achievements(user_name, total_sessions, file_path):
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

def log_session(user_name, session_type, start_time, end_time, duration_minutes, file_path):
    file_exists = os.path.exists(file_path)
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists or file.tell() == 0:
            writer.writerow(['user_name', 'session_type', 'start_time', 'end_time', 'duration_minutes'])
        writer.writerow([user_name, session_type, start_time.isoformat(), end_time.isoformat(), duration_minutes])

if __name__ == "__main__":
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')

        # Get paths
        paths = config['Paths']
        quotes_file = paths.get('quotes_file', 'data/quotes.csv')
        session_log = paths.get('session_log', 'session_log.csv')
        achievements_log = paths.get('achievements_log', 'pomodoro_achievements.csv')

        # Get Pomodoro settings
        pomodoro_settings = config['Pomodoro']
        user_name = pomodoro_settings.get('user_name', 'User')
        work_minutes = pomodoro_settings.getint('work_minutes', 25)
        break_minutes = pomodoro_settings.getint('break_minutes', 5)
        long_break_minutes = pomodoro_settings.getint('long_break_minutes', 15)
        total_cycles = pomodoro_settings.getint('cycles', 4)
        long_break_interval = pomodoro_settings.getint('long_break_interval', 2)
        
        pomodoro_timer(work_minutes, break_minutes, long_break_minutes, total_cycles, long_break_interval, user_name, quotes_file, achievements_log, session_log)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Timer cancelled. Goodbye![/bold yellow]")
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        console.print(f"[bold red]Configuration Error: {e}. Please check your config.ini file.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
