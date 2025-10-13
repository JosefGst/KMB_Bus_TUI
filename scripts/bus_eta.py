import requests
from datetime import datetime
from zoneinfo import ZoneInfo

def fetch_bus_data(url, timeout=30):
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()

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

def get_bus_urls(yaml_path):
    import yaml, os
    with open(yaml_path, 'r') as f:
        bus_routes = yaml.safe_load(f)
    return [f"https://data.etabus.gov.hk/v1/transport/kmb/eta/{value}" for value in bus_routes.values()]
