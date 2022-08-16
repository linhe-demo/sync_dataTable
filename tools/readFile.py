import json


def read_json_config():
    with open(r"D:\PythonProject\sync_dataTable\config\config.json") as json_file:
        config = json.load(json_file)
    return config
