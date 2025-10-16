import csv
import os
from rich.console import Console

console = Console()

def read_csv(file_path, as_dict=False):
    """
    Reads a CSV file and returns its content as a list of lists or a list of dictionaries.
    Handles file not found errors.
    """
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            if as_dict:
                reader = csv.DictReader(file)
            else:
                reader = csv.reader(file)
            return list(reader)
    except FileNotFoundError:
        console.print(f"[bold red]Error: The file at {file_path} was not found.[/bold red]")
        return []
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred while reading {file_path}: {e}[/bold red]")
        return []

def write_csv(file_path, data, header=None):
    """
    Writes data to a CSV file. Data should be a list of lists.
    Handles potential I/O errors.
    """
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if header:
                writer.writerow(header)
            writer.writerows(data)
    except IOError as e:
        console.print(f"[bold red]Error writing to {file_path}: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred while writing to {file_path}: {e}[/bold red]")

def append_csv(file_path, data, header=None):
    """
    Appends data to a CSV file. Data should be a list of lists.
    Handles potential I/O errors.
    """
    file_exists = os.path.exists(file_path)
    try:
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists and header:
                writer.writerow(header)
            writer.writerows(data)
    except IOError as e:
        console.print(f"[bold red]Error appending to {file_path}: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred while appending to {file_path}: {e}[/bold red]")
