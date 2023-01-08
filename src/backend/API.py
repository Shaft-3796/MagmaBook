"""
API.py
This files contains the DataAPI class wich is the main entry point to interact with collectors, connectors and dataflows
"""
import inspect
import json
import math
import os
import threading

from Collector import Collector
from Connectors import ConnectorBindings
from DataFlow import DataFlow
from ComputingEngine import ComputingEngine
import MagmaBookApi


class MountingError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class API:
    # --- PRIVATE ---
    def __init__(self, root: str, wakeup_all: bool = True):
        self.root = root  # Root folder for the dataflows
        self.dataflows = {}  # Dict of dataflows
        self.connectors = {}  # Dict of connectors
        self.collectors = {}  # Dict of collectors
        self.computing_engines = {}  # Dict of computing engines
        self.api_bindings = {}  # For API calls

        # Register API bindings
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        for method in methods:
            method = method[1]
            if hasattr(method, "api_endpoint"):
                self.api_bindings[method.api_endpoint] = method

        # Discover and mount all dataflows
        self.__discover_dataflows__()
        for name in self.dataflows:
            self.__mount_dataflow__(name)
            if self.dataflows[name].header["active"] and wakeup_all:
                self.collectors[name].collect()

    # Discover dataflows in the root folder
    def __discover_dataflows__(self):
        for _dir in os.listdir(self.root):
            if os.path.isdir(self.root + "/" + _dir) and (_dir.startswith("cached_") or _dir.startswith("persistent_")):
                try:
                    with open(self.root + "/" + _dir + "/header.mb", "r") as f:
                        header = json.loads(f.read())
                        self.dataflows[header["name"]] = DataFlow(self.root + "/" + _dir)
                except FileNotFoundError:
                    pass

    # Instanciate Dataflow, connector and collector objects ---
    def __mount_dataflow__(self, name: str):
        if name not in self.dataflows:
            raise MountingError("Dataflow not found")
        dataflow = self.dataflows[name]
        # Connector
        try:
            connector = ConnectorBindings.bindings[dataflow.header["source"]](dataflow.header["connector_params"])
            collector = Collector(connector, dataflow)
            computing_engine = ComputingEngine()
            self.connectors[dataflow.header["name"]] = connector
            self.collectors[dataflow.header["name"]] = collector
            self.computing_engines[dataflow.header["name"]] = computing_engine
        except Exception as e:
            raise MountingError(f"Error while mounting dataflow: {e}")

    # Decorator to register API endpoints to bindings
    @staticmethod
    def api_endpoint(endpoint: str):
        def decorator(function):
            function.__setattr__("api_endpoint", endpoint)
            return function

        return decorator

    # --- API ---
    def call(self, send_response, connection, data):
        endpoint = data["endpoint"]
        if endpoint in self.api_bindings:
            threading.Thread(target=self.api_bindings[endpoint], args=(send_response, connection, data)).start()

    def get_range(self, name: str, start: int, end: int, timeframe: int):
        if name not in self.dataflows:
            raise MountingError("Dataflow not found")
        dataflow = self.dataflows[name]
        data = []
        for timestamp in range(start, end + timeframe, timeframe):
            _data = dataflow.read(timestamp)
            if _data is None:
                _data = {"timestamp": timestamp}
            data.append(_data)
        return data

    # --- API ENDPOINTS ---
    @api_endpoint("ping")
    def api_ping(self, send_response, connection, data):
        send_response(connection, {"pong": True})

    @api_endpoint("get_initial_prices")
    def api_get_initial_prices(self, send_response, connection, data):
        # Ini
        name = data["name"]
        if name not in self.dataflows:
            raise MountingError("Dataflow not found")

        dataflow = self.dataflows[name]

        start, end = dataflow.get_latest_range(5)
        items_range = self.get_range(name, start, end, dataflow.header["timeframe"])
        price_range = []
        for item in items_range:
            if len(item.keys()) > 1:
                _item = {"open": item["open"], "close": item["close"], "high": item["high"], "low": item["low"],
                         "max_bid": item["max_bid"], "min_ask": item["min_ask"],
                         "time": round(item["timestamp"] / 1000)}
                price_range.append(_item)
            else:
                price_range.append({"time": round(item["timestamp"] / 1000)})

        response = {"endpoint": "initial_prices", "prices": price_range}
        send_response(connection, response)

    @api_endpoint("get_historical_prices")
    def api_get_historical_prices(self, send_response, connection, data):
        name = data["name"]
        time_range = data["time_range"]
        timeframe = data["timeframe"]
        if name not in self.dataflows:
            raise MountingError("Dataflow not found")
        dataflow = self.dataflows[name]
        latest = dataflow.header["latest"]
        ms_offset = int(str(latest)[-3:])  # TODO handle latest None
        timeframe = int(timeframe)
        start, end = time_range[0] * 1000 + ms_offset, time_range[1] * 1000 + ms_offset  # Convert to ms
        items_range = self.get_range(name, start, end, timeframe)
        price_range = []
        for item in items_range:
            if len(item.keys()) > 1:
                _item = {"open": item["open"], "close": item["close"], "high": item["high"], "low": item["low"],
                         "max_bid": item["max_bid"], "min_ask": item["min_ask"],
                         "time": math.floor(item["timestamp"] / 1000)}
                price_range.append(_item)
            else:
                _item = {"open": 0.0, "close": 0.0, "high": 0.0, "low": 0.0,
                         "max_bid": 0.0, "min_ask": 0.0,
                         "time": math.floor(item["timestamp"] / 1000)}
                price_range.append(_item)

        response = {"endpoint": "historical_prices", "prices": price_range}
        send_response(connection, response)

    @api_endpoint("get_heatmap")
    def api_get_heatmap(self, send_response, connection, data):
        name = data["name"]
        if name not in self.dataflows:
            raise MountingError("Dataflow not found")
        dataflow = self.dataflows[name]
        data['dataflow'] = dataflow
        response = self.computing_engines[name].compute(data)
        if response is not None:
            send_response(connection, response)





"""
    def create_dataflow(self, flow_type: str, flow_name: str, source: str, connector_params: dict, timeframe: int,
                        cache_size: int = 1000):
        dataflow = DataFlow.create_new_flow(self.root, flow_type, flow_name, source, connector_params, timeframe,
                                            cache_size)
        self.dataflows[flow_name] = dataflow
        self.__mount_dataflow__(flow_name)

    def start_dataflow(self, name: str):
        if name not in self.collectors:
            raise MountingError("Dataflow not found")
        self.collectors[name].start()

    def set_timeframe(self, name: str, timeframe: int):
        if name not in self.dataflows:
            raise MountingError("Dataflow not found")
        dataflow = self.dataflows[name]
        dataflow.header["timeframe"] = timeframe
        dataflow.dump_header()

    def reset_dataflow(self, name: str):
        if name not in self.dataflows:
            raise MountingError("Dataflow not found")
        dataflow = self.dataflows[name]
        dataflow.dump_all_data()

    def stop_dataflow(self, name: str):
        if name not in self.collectors:
            raise MountingError("Dataflow not found")
        self.collectors[name].stop()


    @staticmethod
    def make_raw_paylod(items: dict, vmax: (int, float), vmin: (int, float), vagg: (int, float), grid_max_height: int,
                        parse_size: bool):
        payload = {"items": items, "vmax": vmax, "vmin": vmin, "vagg": float(vagg), "grid_max_height": grid_max_height,
                   "parse_size": int(parse_size)}
        return payload

    @staticmethod
    def compute_raw_payload(raw_payload: dict):
        return MagmaBookApi.raw_to_computed(raw_payload)

    def get_heatmap(self, name: str, start: int, end: int, timeframe: int,
                    vmax: (int, float), vmin: (int, float), vagg: (int, float), grid_max_height: int, parse_size: bool):
        if name not in self.dataflows:
            raise MountingError("Dataflow not found")
        dataflow = self.dataflows[name]
        data = {
            "dataflow": dataflow,
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "vmax": vmax,
            "vmin": vmin,
            "vagg": vagg,
            "grid_max_height": grid_max_height,
            "parse_size": parse_size,
        }
        # return self.computing_engines[name].compute(data)
        self.computing_engines[name].compute(data)

    def get_historical(self, name, time_range, timeframe):
        if name not in self.dataflows:
            raise MountingError("Dataflow not found")
        dataflow = self.dataflows[name]
        latest = dataflow.header["latest"]
        ms_offset = int(str(latest)[-3:]) # TODO handle latest None
        timeframe = int(timeframe)
        start, end = time_range[0]*1000+ms_offset, time_range[1]*1000+ms_offset  # Convert to ms
        items_range = self.get_range(name, start, end, timeframe)
        price_range = []
        for item in items_range:
            if len(item.keys()) > 1:
                _item = {"open": item["open"], "close": item["close"], "high": item["high"], "low": item["low"],
                         "max_bid": item["max_bid"], "min_ask": item["min_ask"], "time": math.floor(item["timestamp"]/1000)}
                price_range.append(_item)
            else:
                _item = {"open": 0.0, "close": 0.0, "high": 0.0, "low": 0.0,
                         "max_bid": 0.0, "min_ask": 0.0,
                         "time": math.floor(item["timestamp"] / 1000)}
                price_range.append(_item)
        return price_range
"""
