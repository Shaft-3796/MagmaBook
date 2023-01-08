import multiprocessing
import sys
import threading
import time
from multiprocessing import Process
from multiprocessing.managers import BaseManager
import MagmaBookApi


class ComputingEngine:
    # SHARED CLASS
    class SharedMemory:
        def __init__(self):
            self.res = None

        def get(self):
            return self.res

        def set(self, value):
            self.res = value

    # CONSTRUCTOR
    def __init__(self):
        self.manager = BaseManager()
        self.manager.register('SharedMemory', self.SharedMemory)
        self.manager.start()
        self.shared_object = self.manager.SharedMemory()
        self.process = None

    @staticmethod
    def target(shared_object, data: dict):
        try:
            # Getting items
            dataflow = data["dataflow"]
            start, end = data["time_range"]
            timeframe = int(data["timeframe"])
            latest = dataflow.header["latest"]
            ms_offset = int(str(latest)[-3:])  # TODO handle latest None
            start, end = start * 1000 + ms_offset, end * 1000 + ms_offset  # Convert to ms
            items = []
            for timestamp in range(start, end + timeframe, timeframe):
                item = dataflow.read(timestamp)
                if item is None:
                    item = {"timestamp": timestamp}
                items.append(item)

            # Crafting raw_payload
            vmax = data["vmax"]
            vmin = data["vmin"]
            vagg = data["vagg"]
            grid_max_height = data["grid_max_height"]
            parse_size = data["parse_size"]
            raw_payload = {"items": items, "vmax": vmax, "vmin": vmin, "vagg": float(vagg),
                           "grid_max_height": grid_max_height,
                           "parse_size": int(parse_size)}

            # Compute payload
            computed_payload = MagmaBookApi.raw_to_computed(raw_payload)
            response = {"endpoint": "heatmap", "payload": computed_payload}
            shared_object.set(response)
        except Exception as e:
            print(e)
            shared_object.set(None)

    def compute(self, data: dict):
        try:
            if self.process is not None:
                self.process.terminate()
            self.process = Process(target=ComputingEngine.target, args=(self.shared_object, data))
            self.process.start()
            self.process.join()
            return self.shared_object.get()
        except Exception as e:
            print(e)
            return None
