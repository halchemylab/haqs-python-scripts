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
from utils.csv_helper import read_csv, append_csv

console = Console()

def handle_input():
    if sys.platform.startswith('win'):
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8').lower()
            if key == 's':
                return 'skip'
    else:
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

    try:
        quotes = read_csv(quotes_file)
        if quotes:
            random_quote = random.choice(quotes[1:])
            quote_text = random_quote[0]
            author_text = random_quote[1]
            quote_display = f'"[italic]{quote_text}[/italic]"\n- [bold]{author_text}[/bold]'
            console.print(Panel(Text(quote_display, justify="center"), title="[bold yellow]Quote of the Session[/bold yellow]"))
    except (FileNotFoundError, IndexError) as e:
        console.print(f"[bold red]Could not display quote: {e}[/bold red]")
        pass

    console.print("[bold cyan]Press 's' at any time to skip the current session.[/bold cyan]")

    for cycle in range(1, cycles + 1):
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
                return False
            progress.update(task, advance=1)
            time.sleep(1)
    return True

def get_user_session_count(user_name, file_path):
    if not os.path.exists(file_path): return 0
    data = read_csv(file_path)
    if not data or len(data) <= 1:
        return 0
    return sum(1 for row in data if row and row[0] == user_name)

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
        
        header = ['user_name', 'achievement', 'timestamp']
        data = [[user_name, message, datetime.now().isoformat()]]
        append_csv(file_path, data, header=header)

def log_session(user_name, session_type, start_time, end_time, duration_minutes, file_path):
    header = ['user_name', 'session_type', 'start_time', 'end_time', 'duration_minutes']
    data = [[user_name, session_type, start_time.isoformat(), end_time.isoformat(), duration_minutes]]
    append_csv(file_path, data, header=header)

if __name__ == "__main__":
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')

        paths = config['Paths']
        quotes_file = paths.get('quotes_file', 'data/quotes.csv')
        session_log = paths.get('session_log', 'session_log.csv')
        achievements_log = paths.get('achievements_log', 'pomodoro_achievements.csv')

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
