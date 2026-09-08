import curses
from kmb_bus_tui.bus_eta import fetch_bus_data, parse_eta, get_bus_urls, get_config_path
from zoneinfo import ZoneInfo
from datetime import datetime


def _run(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green text
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Red text

    yaml_path = get_config_path()
    stdscr.timeout(1000)  # getch() below blocks up to 1s, pacing the refresh loop

    while True:
        stdscr.clear()
        now = datetime.now(ZoneInfo("Asia/Hong_Kong"))
        stdscr.addstr(0, 0, "KMB Bus ETA Viewer", curses.A_BOLD)
        stdscr.addstr(0, 20, now.strftime("%H:%M:%S"), curses.A_DIM)
        stdscr.addstr(0, 30, "(q to quit)", curses.A_DIM)
        stdscr.addstr(1, 0, f"Routes: {yaml_path}", curses.A_DIM)
        stdscr.addstr(2, 0, "=" * 30)
        display_idx = 3

        urls = get_bus_urls(yaml_path)
        for url in urls:
            data = fetch_bus_data(url)
            if data is None:
                stdscr.addstr(display_idx, 0, "Connection error. Could not fetch bus data.", curses.color_pair(2) | curses.A_BOLD)
                display_idx += 1
                continue
            buses = data.get('data', [])
            if not buses:
                stdscr.addstr(display_idx, 0, "No bus data available.", curses.A_DIM)
                display_idx += 1
            for bus in buses:
                result = parse_eta(bus, now)
                if result[1]: 
                    stdscr.addstr(display_idx, 0, f"{result[0]}: ", curses.A_BOLD)
                    stdscr.addstr(str(result[1]), curses.color_pair(1) | curses.A_BOLD)
                    stdscr.addstr(" min till arrival")
                else:
                    stdscr.addstr(display_idx, 0, f"{result[0]}: Not available", curses.color_pair(2))
                display_idx += 1

        stdscr.refresh()
        key = stdscr.getch()  # blocks up to 1s (see stdscr.timeout above), then loops
        if key in (ord('q'), ord('Q')):
            break


def main() -> None:
    curses.wrapper(_run)