import json
import os
from shutil import rmtree

"""
DataFlow.py
This file contains the DataFlow class wich represent a dataflow implemented as a folder with a header file containing 
informations about the flow.
"""


class FlowType:
    PERSISTENT = "persistent"
    CACHED = "cached"


class DataFlow:

    @staticmethod
    def create_new_flow(root: str, flow_type: str, flow_name: str, source: str, connector_params: dict, timeframe: int,
                        cache_size: int = 1000):
        name = f"{flow_type}_{flow_name}"
        path = root + "/" + name
        if os.path.exists(path):
            raise FileExistsError("Data flow already exists")
        else:
            os.mkdir(path)
            # Header
            with open(path + "/header.mb", "w") as f:
                header = {
                    "type": flow_type,
                    "name": flow_name,
                    "source": source,
                    "connector_params": connector_params,
                    "timeframe": timeframe,
                    "active": False,
                    "latest": None
                }
                if flow_type == FlowType.CACHED:
                    header["cache_size"] = cache_size
                json.dump(header, f)
            return DataFlow(path)

    def __init__(self, root: str):
        self.root = root
        with open(root + "/header.mb", "r") as f:
            self.header = json.loads(f.read())

    def dump_header(self):
        with open(self.root + "/header.mb", "w") as f:
            json.dump(self.header, f)

    def write(self, data: dict):
        self.header["latest"] = data["timestamp"]
        with open(self.root + f"/{data['timestamp']}.mb", "w") as f:
            json.dump(data, f)
        self.dump_header()

    def read(self, timestamp: int):
        try:
            with open(self.root + f"/{timestamp}.mb", "r") as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return None

    def remove(self, timestamp: int):
        try:
            os.remove(f"{self.root}/{timestamp}.mb")
        except FileNotFoundError:
            pass

    def dump_all_data(self):
        rmtree(self.root)
        os.mkdir(self.root)
        self.header["latest"] = None
        self.dump_header()

    def get_latest_range(self, n: int):
        end = self.header["latest"]
        start = end - (n * self.header["timeframe"])
        return start, end
