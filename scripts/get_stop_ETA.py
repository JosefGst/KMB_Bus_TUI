import os
import curses
import threading
import time
from bus_eta import fetch_bus_data, parse_eta, get_bus_urls
from zoneinfo import ZoneInfo 
from datetime import datetime

def fetch_all_bus_data(urls, now, shared_data, lock, refresh_interval=60):
    """Background thread: fetch bus data and update shared_data."""
    while True:
        new_results = []
        for url in urls:
            try:
                data = fetch_bus_data(url)
                buses = data.get('data', [])
                if not buses:
                    new_results.append(("No bus data available.", False))
                for bus in buses:
                    result = parse_eta(bus, now)
                    is_arriving = "min till arrival" in result
                    new_results.append((result, is_arriving))
            except Exception:
                new_results.append(("Error fetching or parsing data.", False))
        with lock:
            shared_data.clear()
            shared_data.extend(new_results)
        time.sleep(refresh_interval)

def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green text
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Red text

    refresh_rate = 30  # seconds
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, '../config/bus_routes.yaml')
    urls = get_bus_urls(yaml_path)

    shared_data = []
    lock = threading.Lock()

    # Start background thread to fetch data
    thread = threading.Thread(
        target=fetch_all_bus_data,
        args=(urls, datetime.now(ZoneInfo("Asia/Hong_Kong")), shared_data, lock),
        kwargs={'refresh_interval': refresh_rate},
        daemon=True
    )
    thread.start()

    while True:
        stdscr.clear()
        now = datetime.now(ZoneInfo("Asia/Hong_Kong"))
        stdscr.addstr(0, 0, "KMB Bus ETA Viewer", curses.A_BOLD | curses.color_pair(1))
        stdscr.addstr(0, 30, now.strftime("%H:%M:%S"), curses.A_DIM)
        stdscr.addstr(1, 0, f"Press ctrl + c to exit. Data refreshes every {refresh_rate} seconds.", curses.A_DIM)
        stdscr.addstr(2, 0, "=" * 50, curses.color_pair(1))
        display_idx = 4

        with lock:
            if not shared_data:
                stdscr.addstr(display_idx, 2, "Loading data...", curses.A_DIM)
            else:
                for result, is_arriving in shared_data:
                    color = curses.color_pair(1) | curses.A_BOLD if is_arriving else curses.color_pair(2) | curses.A_BOLD
                    stdscr.addstr(display_idx, 2, result, color)
                    display_idx += 1

        stdscr.refresh()
        stdscr.timeout(1000)  # Check for key every second
        key = stdscr.getch()
        # if key != -1:
        #     break

curses.wrapper(main)