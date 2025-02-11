import speedtest
from tqdm import tqdm
import time

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

    print(f"\nYour Internet Speed Results:")
    print(f"Download Speed: {download_speed:.2f} Mbps")
    print(f"Upload Speed: {upload_speed:.2f} Mbps")
    print(f"Ping: {ping:.2f} ms")

if __name__ == "__main__":
    test_internet_speed()