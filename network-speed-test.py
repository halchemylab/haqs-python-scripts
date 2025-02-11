import speedtest

def test_internet_speed():
    print("Testing your internet speed, please wait...")
    st = speedtest.Speedtest()
    
    # Get the best server based on ping
    st.get_best_server()
    
    # Perform download and upload speed tests
    download_speed = st.download() / 1_000_000  # Convert from bits/s to Mbits/s
    upload_speed = st.upload() / 1_000_000      # Convert from bits/s to Mbits/s
    ping = st.results.ping

    print(f"\nYour Internet Speed Results:")
    print(f"Download Speed: {download_speed:.2f} Mbps")
    print(f"Upload Speed: {upload_speed:.2f} Mbps")
    print(f"Ping: {ping:.2f} ms")

if __name__ == "__main__":
    test_internet_speed()
