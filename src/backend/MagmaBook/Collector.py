"""
Collector.py
This file contains the Collector class wich links a dataflow with a connector and handle data retrieval.
"""
import asyncio
import time

import threading

from src.backend.MagmaBook.DataFlow import FlowType


class Collector:

    def __init__(self, connector, dataflow):
        self.connector = connector
        self.dataflow = dataflow
        self.thread_running = False

    # Return true if the collector is retrieving data, false otherwise
    def get_status(self):
        return self.dataflow.header['active']

    # Start the collector
    def collect(self):
        # Check if the collector is already running
        if self.thread_running:
            return
        self.thread_running = True

        # Start the collector
        self.dataflow.header['active'] = True
        self.dataflow.dump_header()
        timeframe = int(self.dataflow.header['timeframe'])
        latest = self.dataflow.header['latest']

        # For cached dataflow
        if self.dataflow.header['type'] == FlowType.CACHED:
            self.dataflow.dump_all_data()  # Dump the cache
            saved_timestamps = []  # List of timestamps already saved

        # Compute the next timestamp
        if latest is None:
            next_timestamp = int(time.time() * 1000) + 10000
        else:
            next_timestamp = latest + timeframe
            while next_timestamp < int(time.time() * 1000) + 10000:
                next_timestamp += timeframe

        async def _collect():
            nonlocal next_timestamp

            last_data = {}
            bids, asks = [], []

            while self.thread_running:
                # Get data
                data = await self.connector.watch()
                timestamp = data['timestamp']

                if timestamp <= next_timestamp:
                    # Used to collect price data
                    bids.append(data['bids'][0][0])
                    asks.append(data['asks'][0][0])
                else:
                    # --- Handle last data ---
                    # OHLCV
                    if last_data != {}:
                        last_data['open'] = (bids[0] + asks[0]) / 2
                        last_data['high'] = max(bids)
                        last_data['low'] = min(asks)
                        last_data['close'] = (bids[-1] + asks[-1]) / 2
                        # Write last data
                        self.dataflow.write(last_data)
                        # For cached dataflow
                        if self.dataflow.header['type'] == FlowType.CACHED:
                            saved_timestamps.append(last_data['timestamp'])
                            if len(saved_timestamps) > self.dataflow.header['cache_size']:
                                try:
                                    self.dataflow.remove(saved_timestamps.pop(0))
                                except IndexError:
                                    pass

                    # --- Handle new data ---
                    _timestamp = next_timestamp + timeframe
                    while data['timestamp'] >= _timestamp:
                        next_timestamp = _timestamp
                        _timestamp += timeframe
                    data['timestamp'] = next_timestamp
                    data['max_bid'] = data['bids'][0][0]
                    data['min_ask'] = data['asks'][0][0]
                    bids, asks = [], []
                    bids.append(data['bids'][0][0])
                    asks.append(data['asks'][0][0])

                    last_data = data
                    next_timestamp = _timestamp

            await self.connector.close()

        threading.Thread(target=asyncio.run, args=[_collect()]).start()
        # TODO for testing purpose, ensure the thread to correctly start, remove this sleep for production.
        time.sleep(5)

    def stop(self):
        self.thread_running = False
        self.dataflow.header['active'] = False
        self.dataflow.dump_header()

    def start(self):
        self.collect()
        self.dataflow.header['active'] = True
        self.dataflow.dump_header()