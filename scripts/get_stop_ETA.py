import os
import requests
import yaml
import curses
import time
from datetime import datetime, timezone

def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green text
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Red text
    # Read bus ETA URLs from YAML file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, '../conf/bus_routs.yaml')
    with open(yaml_path, 'r') as f:
        bus_routes = yaml.safe_load(f)

    urls = []
    for key, value in bus_routes.items():
        urls.append(f"https://data.etabus.gov.hk/v1/transport/kmb/eta/{value}")
    
    while True:
        stdscr.clear()
        display_idx = 1
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                buses = data.get('data', [])
                if not buses:
                    stdscr.addstr(display_idx, 0, "No bus data available.", curses.color_pair(2) | curses.A_BOLD)
                    display_idx += 1
                for bus in buses:
                    route = bus.get('route', 'Unknown')
                    eta = bus.get('eta')
                    if eta:
                        try:
                            eta_dt = datetime.fromisoformat(eta.replace('Z', '+00:00'))
                            now = datetime.now(timezone.utc)
                            minutes = int((eta_dt - now).total_seconds() // 60)
                            if minutes >= 0:
                                stdscr.addstr(display_idx, 0, f"{route}: ", curses.color_pair(1) | curses.A_BOLD)
                                stdscr.addstr(f"{minutes} min till arrival", curses.A_NORMAL)
                            else:
                                stdscr.addstr(display_idx, 0, f"{route}: Arrived ({eta})")
                        except Exception:
                            stdscr.addstr(display_idx, 0, f"{route}: Next arrival at {eta}")
                    else:
                        stdscr.addstr(display_idx, 0, f"{route}: Arrival time not available")
                    display_idx += 1
            except requests.exceptions.ConnectionError as e:
                # stdscr.addstr(display_idx, 0, "Connection error: Connection reset by peer", curses.color_pair(2) | curses.A_BOLD)
                display_idx += 1
            except requests.RequestException as e:
                # stdscr.addstr(display_idx, 0, f"Request error: {str(e)}", curses.color_pair(2) | curses.A_BOLD)
                display_idx += 1
            except Exception as e:
                # stdscr.addstr(display_idx, 0, f"Data error: {str(e)}", curses.color_pair(2) | curses.A_BOLD)
                display_idx += 1
        stdscr.refresh()
        stdscr.timeout(10000)  # 10000 ms = 10 seconds
        key = stdscr.getch()
        if key != -1:
            break
        stdscr.getch()

curses.wrapper(main)