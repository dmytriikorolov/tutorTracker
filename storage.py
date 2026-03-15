import json
import os

DATA_FILE = "tracker_data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        initial_data = {"students": [], "lessons": [], "payments": []}
        with open(DATA_FILE, "w") as f:
            json.dump(initial_data, f, indent=4)
        return initial_data

    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)