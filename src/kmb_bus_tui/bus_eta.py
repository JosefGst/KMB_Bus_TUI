import os
import importlib.resources
from pathlib import Path

import requests
from datetime import datetime
from zoneinfo import ZoneInfo

def fetch_bus_data(url, timeout=30):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError):
        return None

def parse_eta(bus, now=None):
    route = bus.get('route', 'Unknown')
    eta = bus.get('eta')
    if not now:
        now = datetime.now(ZoneInfo("Asia/Hong_Kong"))
    if eta:
        eta_dt = datetime.fromisoformat(eta.replace('Z', '+00:00'))
        minutes = int((eta_dt - now).total_seconds() // 60)
        return route, minutes
    else:
        return route, False

def get_config_path() -> Path:
    """Return the writable path where bus_routes.yaml lives.

    Config must live in a location the user can edit and that survives
    reinstalls. $SNAP is read-only when running as a strictly-confined
    snap, so we never read/write there: SNAP_USER_COMMON (writable,
    persists across snap revisions) is used when set, otherwise we fall
    back to the usual XDG config directory. The file is seeded from the
    package's bundled default the first time it's needed.
    """
    if snap_common := os.environ.get("SNAP_USER_COMMON"):
        config_dir = Path(snap_common)
    else:
        config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "kmb-bus-tui"

    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "bus_routes.yaml"

    if not config_path.exists():
        default = importlib.resources.files("kmb_bus_tui").joinpath("default_bus_routes.yaml")
        config_path.write_text(default.read_text())

    return config_path


def get_bus_urls(yaml_path):
    import yaml
    with open(yaml_path, 'r') as f:
        bus_routes = yaml.safe_load(f)
    return [f"https://data.etabus.gov.hk/v1/transport/kmb/eta/{value}" for value in bus_routes.values()]
