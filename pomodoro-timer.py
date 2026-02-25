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
try:
    import pygame
except ImportError:
    pygame = None

console = Console()

class TickingSound:
    def __init__(self, file_path):
        self.sound = None
        if pygame and file_path and os.path.exists(file_path):
            try:
                pygame.mixer.init()
                self.sound = pygame.mixer.Sound(file_path)
            except pygame.error as e:
                console.print(f"[bold red]Could not initialize sound: {e}[/bold red]")

    def play(self):
        if self.sound:
            try:
                self.sound.play()
            except pygame.error as e:
                console.print(f"[bold red]Could not play sound: {e}[/bold red]")

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

def pomodoro_timer(work_duration, break_duration, long_break_duration, cycles, long_break_interval, user_name, quotes_file, achievements_log, session_log, audio_settings):
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
        session_complete = countdown('work', work_duration * 60, cycle, cycles, audio_settings)
        
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
                break_complete = countdown('long_break', long_break_duration * 60, cycle, cycles, audio_settings)
            else:
                break_complete = countdown('break', break_duration * 60, cycle, cycles, audio_settings)
            
            if break_complete:
                console.print("[bold green]Break over![/bold green]")
            else:
                console.print("[bold yellow]Break skipped.[/bold yellow]")

            notification.notify(title='Break Over', message='Time to get back to work!')
            
            if cycle + 1 <= cycles:
                console.input("\n[bold cyan]Press Enter to start the next work session...[/bold cyan]")

    console.print(Panel(Text(f"All {cycles} pomodoro cycles completed! Great job, {user_name}! 🎉", justify="center"), title="[bold green]Finished![/bold green]"))
    notification.notify(title='Pomodoro Complete', message=f'All {cycles} cycles completed! Great job!')

def countdown(session_type, duration, current_cycle, total_cycles, audio_settings):
    title_styles = {
        'work': f"[bold red]Work Session {current_cycle}/{total_cycles}",
        'break': f"[bold green]Short Break {current_cycle}/{total_cycles}",
        'long_break': f"[bold blue]Long Break {current_cycle}/{total_cycles}"
    }
    title = title_styles.get(session_type, "Session")

    ticking_sound = audio_settings.get('ticking_sound')
    tick_speed = audio_settings.get('tick_speed', 1.0)
    tick_interval = 1.0 / tick_speed
    last_tick_time = 0

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(title, total=duration)
        start_time = time.monotonic()

        while not progress.finished:
            elapsed_time = time.monotonic() - start_time
            
            if handle_input() == 'skip':
                return False

            if ticking_sound and elapsed_time - last_tick_time >= tick_interval:
                ticking_sound.play()
                last_tick_time = elapsed_time

            progress.update(task, completed=elapsed_time)
            time.sleep(0.01) # Sleep for a short time to prevent high CPU usage
            
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

        audio_settings = {}
        ticking_sound = None
        if pygame:
            try:
                audio_config = config['Audio']
                if audio_config.getboolean('enable_ticking_sound', False):
                    sound_file = audio_config.get('tick_sound_file')
                    if sound_file:
                        ticking_sound = TickingSound(sound_file)
                        if not ticking_sound.sound:
                             console.print(f"[bold yellow]Could not load ticking sound file from '{sound_file}'. Please check the file path in config.ini.[/bold yellow]")
                    else:
                        console.print("[bold yellow]Ticking sound is enabled, but no sound file is specified in config.ini.[/bold yellow]")

                    audio_settings['ticking_sound'] = ticking_sound
                    audio_settings['tick_speed'] = audio_config.getfloat('tick_speed', 1.0)
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                pass # Audio section is optional
        
        pomodoro_timer(work_minutes, break_minutes, long_break_minutes, total_cycles, long_break_interval, user_name, quotes_file, achievements_log, session_log, audio_settings)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Timer cancelled. Goodbye![/bold yellow]")
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        console.print(f"[bold red]Configuration Error: {e}. Please check your config.ini file.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
        if pygame and 'pygame' in str(e).lower():
            console.print("[bold red]An error occurred with the audio system (pygame). Please ensure your audio drivers are working.[/bold red]")
