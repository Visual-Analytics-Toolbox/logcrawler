from pathlib import Path
from datetime import datetime
from vaapi.client import Vaapi
import logging
import os


def has_duplicates(data_list, fieldname):
    # Create a set of all values for that specific key
    values = [d[fieldname] for d in data_list if fieldname in d]
    return len(values) != len(set(values))

if __name__ == "__main__":
    v_client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    #test("/mnt/repl", v_client)
    logs = list(v_client.logs.list())
    games = list(v_client.games.list())

    print(has_duplicates(logs, "log_path"))  # Output: True
    print(has_duplicates(games, "2025-03-15_17-15-00"))  # Output: True