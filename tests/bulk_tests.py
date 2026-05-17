from pathlib import Path
from datetime import datetime
from vaapi.client import Vaapi
import logging
import os

def test(log_root_path, client):
    my_list = []

    game1 = {
        "event": 1,
        "team1": 3,
        "team2": 9,
        "half": "blabla1",
        "start_time": "2099-07-18_12-30-00"
    }

    game2 = {
        "event": 1,
        "team1": 3,
        "team2": 9,
        "half": "blabla2",
        "start_time": "2099-07-18_12-30-00"
    }
    my_list.append(game1)
    my_list.append(game2)

    response = client.games.bulk_create(data_list=my_list)

def test2(log_root_path, client):
    my_list = []

    event1 = {
        "name": "Test Event 1"
    }

    event2 = {
        "name": "Test Event 2"
    }
    my_list.append(event1)
    my_list.append(event2)

    response = client.events.bulk_create(data_list=my_list)


if __name__ == "__main__":
    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    test2("/mnt/repl", v_client)