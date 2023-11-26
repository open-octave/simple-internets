import speedtest
import threading
import time
from datetime import datetime
from colorama import Fore, Style
from alive_progress import alive_bar
import argparse
import sys


# Setup argument parser
parser = argparse.ArgumentParser(description="Internet Speedtest Script")
parser.add_argument(
    "-i",
    "--interval",
    type=int,
    default=180,
    help="Interval between tests in seconds (default: 180)",
)
parser.add_argument(
    "-t",
    "--threads",
    type=int,
    default=1,
    help="Number of concurrent threads for the test (default: 1)",
)
args = parser.parse_args()


def run_speed_test():
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download()
    upload_speed = st.upload()
    return download_speed, upload_speed


def test_speed():
    threads = []
    results = []

    def worker():
        download, upload = run_speed_test()
        results.append((download, upload))

    for _ in range(args.threads):
        thread = threading.Thread(target=worker)
        thread.start()
        threads.append(thread)

    with alive_bar(
        len(threads), title="Testing Internet Speed...", bar="bubbles"
    ) as bar:
        for thread in threads:
            thread.join()
            bar()

    total_download = sum(download for download, _ in results)
    total_upload = sum(upload for _, upload in results)
    return total_download, total_upload


def convert_speed_to_mbps(speed):
    return speed / 1_000_000  # Convert from bits per second to Mbps


def log_to_file(log_message):
    with open("./internet_speed_log.txt", "a") as file:
        file.write(log_message + "\n")


def countdown_timer(interval):
    for remaining in range(interval, 0, -1):
        sys.stdout.write(
            f"\r{Fore.CYAN}Next test in: {remaining} second(s)...{Style.RESET_ALL} "
        )
        sys.stdout.flush()
        time.sleep(1)
    print("\n")  # Move to a new line after the countdown is complete


while True:
    total_download, total_upload = test_speed()
    download_mbps = convert_speed_to_mbps(total_download)
    upload_mbps = convert_speed_to_mbps(total_upload)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = (
        f"[{timestamp}] {Fore.GREEN}Total Download: {download_mbps:.2f} Mbps, "
        f"Total Upload: {upload_mbps:.2f} Mbps{Style.RESET_ALL}"
    )
    print(log_message)
    log_to_file(log_message)

    countdown_timer(args.interval)
