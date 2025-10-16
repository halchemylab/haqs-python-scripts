import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except TypeError:
        import os
        os.system("chcp 65001 > nul")

import speedtest
import csv
from datetime import datetime
import os
import argparse
import asciichartpy as asciichart
import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.live import Live
from rich.table import Table
from rich.markdown import Markdown
import configparser
from utils.openai_client import get_openai_client
from utils.ai_helper import get_ai_response
from utils.csv_helper import append_csv, read_csv

console = Console()

def display_ip_details():
    """Fetches and displays public IP and geolocation details using Rich."""
    try:
        console.print("Fetching your public IP details...", style="cyan")
        response = requests.get("https://ipinfo.io/json")
        response.raise_for_status()
        data = response.json()

        table = Table(title="Your Public IP Information", show_header=False, border_style="magenta")
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="white")
        
        table.add_row("IP Address", data.get('ip', 'N/A'))
        table.add_row("ISP", data.get('org', 'N/A'))
        table.add_row("Location", f"{data.get('city', 'N/A')}, {data.get('region', 'N/A')}, {data.get('country', 'N/A')}")
        
        console.print(table)

    except requests.exceptions.RequestException as e:
        console.print(Panel(f"Could not fetch IP details: {e}", title="[bold red]Error[/bold red]"), style="red")
    except Exception as e:
        console.print(Panel(f"An unexpected error occurred: {e}", title="[bold red]Error[/bold red]"), style="red")

def test_internet_speed(filename):
    display_ip_details()
    console.print("\nTesting your internet speed, please wait...", style="cyan")

    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=50),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
    )

    try:
        with Live(progress, console=console, screen=False, refresh_per_second=10) as live:
            task = progress.add_task("Running Tests", total=100)
            
            st = speedtest.Speedtest()
            progress.update(task, advance=20, description="Finding best server")
            st.get_best_server()
            progress.update(task, advance=30, description="Testing download speed")
            download_speed = st.download() / 1_000_000
            progress.update(task, advance=25, description="Testing upload speed")
            upload_speed = st.upload() / 1_000_000
            progress.update(task, advance=20, description="Measuring ping")
            ping = st.results.ping
            progress.update(task, advance=5, description="Done!")

        results_text = Text.from_markup(f"Download: [bold green]{download_speed:.2f} Mbps[/bold green] | "
                                     f"Upload: [bold blue]{upload_speed:.2f} Mbps[/bold blue] | "
                                     f"Ping: [bold magenta]{ping:.2f} ms[/bold magenta]", justify="center")
        
        console.print(Panel(results_text, title="[bold]Speed Test Results[/bold]"))

        with console.status("[bold cyan]Getting AI optimization suggestions...[/bold cyan]", spinner="dots"):
            suggestions = get_ai_response(
                system_message="You are a helpful assistant that provides internet optimization tips.",
                user_prompt=f"My internet speed is {download_speed:.2f} Mbps download, {upload_speed:.2f} Mbps upload, and {ping:.2f} ms ping. First, evaluate if the connection is good or not. Second, What are some suggestions to optimize my internet connection? Give me 2 concise suggestions."
            )
        
        if suggestions:
            console.print(Panel(Markdown(suggestions), title="[bold]AI Suggestions[/bold]"))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = ["Timestamp", "Download Speed (Mbps)", "Upload Speed (Mbps)", "Ping (ms)"]
        data = [[now, f"{download_speed:.2f}", f"{upload_speed:.2f}", f"{ping:.2f}"]]
        append_csv(filename, data, header=header)

    except speedtest.SpeedtestException as e:
        console.print(Panel(f"An error occurred during the speed test: {e}\nPlease check your internet connection and try again.", title="[bold red]Speed Test Error[/bold red]"))
    except Exception as e:
        console.print(Panel(f"An unexpected error occurred: {e}", title="[bold red]Error[/bold red]"))

def show_history(filename):
    """Reads the network log and displays a historical graph of speeds using Rich."""
    try:
        data = read_csv(filename)
        if not data or len(data) <= 1:
            console.print(Panel("No data in history log yet.", title="[bold yellow]Warning[/bold yellow]"))
            return

        header = data[0]
        rows = data[1:]

        timestamps = []
        downloads = []
        uploads = []

        for row in rows:
            try:
                timestamps.append(row[0])
                downloads.append(float(row[1]))
                uploads.append(float(row[2]))
            except (ValueError, IndexError):
                console.print(f"Skipping malformed row: {row}", style="yellow")
                continue

        if not downloads:
            console.print(Panel("No data in history log yet.", title="[bold yellow]Warning[/bold yellow]"))
            return

        downloads_recent = downloads[-30:]
        uploads_recent = uploads[-30:]

        download_chart = asciichart.plot(downloads_recent, {'height': 10})
        upload_chart = asciichart.plot(uploads_recent, {'height': 10})

        history_text = Text("\nDownload Speed (Mbps):\n", style="bold green")
        history_text.append(download_chart)
        history_text.append("\n\nUpload Speed (Mbps):\n", style="bold blue")
        history_text.append(upload_chart)

        console.print(Panel(history_text, title="[bold]Historical Network Speeds (last 30 entries)[/bold]"))
    except FileNotFoundError:
        console.print(Panel("No history log found. Run a speed test first.", title="[bold yellow]Warning[/bold yellow]"))
    except Exception as e:
        console.print(Panel(f"An error occurred while displaying history: {e}", title="[bold red]Error[/bold red]"))

if __name__ == "__main__":
    try:
        
        config = configparser.ConfigParser()
        config.read('config.ini')
        paths = config['Paths']
        network_log = paths.get('network_log', 'network_log.csv')

        parser = argparse.ArgumentParser(description="Test internet speed and get AI optimization suggestions.")
        parser.add_argument("--history", action="store_true", help="Show a graph of historical speed data.")
        args = parser.parse_args()

        if args.history:
            show_history(network_log)
        else:
            test_internet_speed(network_log)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Process interrupted by user. Exiting...[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
