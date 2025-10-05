import speedtest
from tqdm import tqdm
import time
import csv
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse
import asciichartpy as asciichart
import requests

def display_ip_details():
    """Fetches and displays public IP and geolocation details."""
    try:
        print("Fetching your public IP details...")
        response = requests.get("https://ipinfo.io/json")
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        print("\nYour Public IP Information:")
        print(f"  IP Address: {data.get('ip')}")
        print(f"  ISP: {data.get('org')}")
        print(f"  Location: {data.get('city')}, {data.get('region')}, {data.get('country')}")
        print("-" * 30)

    except requests.exceptions.RequestException as e:
        print(f"\nCould not fetch IP details: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred while fetching IP details: {e}")

def get_optimization_suggestions(download_speed, upload_speed, ping):
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        if not client.api_key:
            return "OpenAI API key is not configured. Please set the OPENAI_API_KEY environment variable."
            
        prompt = f"My internet speed is {download_speed:.2f} Mbps download, {upload_speed:.2f} Mbps upload, and {ping:.2f} ms ping. First, evaluate if the connection is good or not. Second, What are some suggestions to optimize my internet connection? Give me 2 concise suggestions."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides internet optimization tips."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not get AI suggestions. Error: {e}"

def test_internet_speed():
    display_ip_details()
    print("\nTesting your internet speed, please wait...")
    try:
        # Initialize the progress bar
        with tqdm(total=100, desc="Running Tests", bar_format='{l_bar}{bar} [ time left: {remaining} ]') as pbar:
            
            st = speedtest.Speedtest()
            pbar.update(20)  # Update progress after initializing Speedtest

            # Get the best server based on ping
            st.get_best_server()
            pbar.update(30)  # Update progress after getting best server
            
            # Perform download and upload speed tests
            download_speed = st.download() / 1_000_000  # Convert from bits/s to Mbits/s
            pbar.update(25)  # Update progress after download test

            upload_speed = st.upload() / 1_000_000      # Convert from bits/s to Mbits/s
            pbar.update(20)  # Update progress after upload test

            ping = st.results.ping
            pbar.update(5)   # Final progress update

        # Display results
        print(f"\nYour Internet Speed Results:")
        print(f"Download Speed: {download_speed:.2f} Mbps")
        print(f"Upload Speed: {upload_speed:.2f} Mbps")
        print(f"Ping: {ping:.2f} ms")

        # Get and display optimization suggestions
        suggestions = get_optimization_suggestions(download_speed, upload_speed, ping)
        print("\nAI Suggestions:")
        print(suggestions)

        # Log results to CSV file
        log_results(download_speed, upload_speed, ping)
    except speedtest.SpeedtestException as e:
        print(f"\nAn error occurred during the speed test: {e}")
        print("Please check your internet connection and try again.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

def log_results(download_speed, upload_speed, ping):
    filename = "network_log.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.exists(filename)

    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Timestamp", "Download Speed (Mbps)", "Upload Speed (Mbps)", "Ping (ms)"])
        writer.writerow([now, f"{download_speed:.2f}", f"{upload_speed:.2f}", f"{ping:.2f}"])

def show_history():
    """Reads the network log and displays a historical graph of speeds."""
    filename = "network_log.csv"
    if not os.path.exists(filename):
        print("No history log found. Run a speed test first.")
        return

    timestamps = []
    downloads = []
    uploads = []

    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        try:
            header = next(reader) # Skip header
        except StopIteration:
            print("No data in history log yet.")
            return
            
        for row in reader:
            try:
                timestamps.append(row[0])
                downloads.append(float(row[1]))
                uploads.append(float(row[2]))
            except (ValueError, IndexError):
                print(f"Skipping malformed row: {row}")
                continue

    if not downloads:
        print("No data in history log yet.")
        return

    print("Historical Network Speeds (last 30 entries):")
    # Only show the last 30 entries to keep the graph readable
    downloads_recent = downloads[-30:]
    uploads_recent = uploads[-30:]
    
    print("\nDownload Speed (Mbps):")
    print(asciichart.plot(downloads_recent, {'height': 10}))
    print("\nUpload Speed (Mbps):")
    print(asciichart.plot(uploads_recent, {'height': 10}))

if __name__ == "__main__":
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Test internet speed and get AI optimization suggestions.")
    parser.add_argument("--history", action="store_true", help="Show a graph of historical speed data.")
    args = parser.parse_args()

    if args.history:
        show_history()
    else:
        test_internet_speed()