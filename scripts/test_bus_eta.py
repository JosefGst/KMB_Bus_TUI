import pytest
from unittest.mock import patch
from bus_eta import fetch_bus_data, parse_eta, get_bus_urls
from datetime import datetime
from zoneinfo import ZoneInfo

class DummyResponse:
    def __init__(self, json_data):
        self._json = json_data
    def json(self):
        return self._json
    def raise_for_status(self):
        pass

def test_parse_eta_minutes():
    now = datetime(2025, 10, 9, 12, 0, 0, tzinfo=ZoneInfo("Asia/Hong_Kong"))
    bus = {'route': '48X', 'eta': '2025-10-09T12:10:00+08:00'}
    result = parse_eta(bus, now)
    assert "10 min till arrival" in result

def test_parse_eta_arrived():
    now = datetime(2025, 10, 9, 12, 0, 0, tzinfo=ZoneInfo("Asia/Hong_Kong"))
    bus = {'route': '48X', 'eta': '2025-10-09T11:50:00+08:00'}
    result = parse_eta(bus, now)
    assert "Arrived" in result

def test_parse_eta_no_eta():
    bus = {'route': '48X'}
    result = parse_eta(bus)
    assert "Arrival time not available" in result

@patch('bus_eta.requests.get')
def test_fetch_bus_data(mock_get):
    mock_get.return_value = DummyResponse({'data': [{'route': '48X', 'eta': '2025-10-09T12:10:00+08:00'}]})
    url = 'http://dummy-url'
    data = fetch_bus_data(url)
    assert 'data' in data
    assert data['data'][0]['route'] == '48X'
