import speedtest
from tqdm import tqdm
import time
import csv
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI

def get_optimization_suggestions(download_speed, upload_speed, ping):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    prompt = f"My internet speed is {download_speed:.2f} Mbps download, {upload_speed:.2f} Mbps upload, and {ping:.2f} ms ping. First, evaluate if the connection is good or not. Second, What are some suggestions to optimize my internet connection? Give me 2 concise suggestions."

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides internet optimization tips."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def test_internet_speed():
    print("Testing your internet speed, please wait...")
    
    # Initialize the progress bar
    with tqdm(total=100, desc="Running Tests", bar_format='{l_bar}{bar} [ time left: {remaining} ]') as pbar:
        
        st = speedtest.Speedtest()
        pbar.update(20)  # Update progress after initializing Speedtest
        time.sleep(0.5)

        # Get the best server based on ping
        st.get_best_server()
        pbar.update(30)  # Update progress after getting best server
        time.sleep(0.5)
        
        # Perform download and upload speed tests
        download_speed = st.download() / 1_000_000  # Convert from bits/s to Mbits/s
        pbar.update(25)  # Update progress after download test
        time.sleep(0.5)

        upload_speed = st.upload() / 1_000_000      # Convert from bits/s to Mbits/s
        pbar.update(20)  # Update progress after upload test
        time.sleep(0.5)

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

def log_results(download_speed, upload_speed, ping):
    filename = "network_log.csv"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if file exists and write header if not
    try:
        with open(filename, 'x', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Timestamp", "Download Speed (Mbps)", "Upload Speed (Mbps)", "Ping (ms)"])
    except FileExistsError:
        pass  # File already exists

    # Append the results
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([now, f"{download_speed:.2f}", f"{upload_speed:.2f}", f"{ping:.2f}"])

if __name__ == "__main__":
    load_dotenv()
    test_internet_speed()