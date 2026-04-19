import json
import os
import tempfile

DATA_FILE = "tracker_data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        initial_data = {"students": [], "lessons": [], "payments": []}
        save_data(initial_data)
        return initial_data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    directory = os.path.dirname(os.path.abspath(DATA_FILE)) or "."

    with tempfile.NamedTemporaryFile(
        "w",
        dir=directory,
        delete=False,
        encoding="utf-8",
    ) as temp_file:
        json.dump(data, temp_file, indent=4)
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_name = temp_file.name

    os.replace(temp_name, DATA_FILE)
