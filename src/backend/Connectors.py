import time
from ccxt.pro import binance as binance_pro

"""
Connectors.py
This file containes diferents connectors to different sources of data.
To create a new connector, create a new class that inherits from BaseDataConnector.
__init__ of your connector has to take one argument, this argument is a dictionary containings some parameters given by 
the user for your connector.
Your connector needs an async watch() method to retrieve the latest data item from the source.
This methods needs to return a dictionary with the data following this format:
{"bids": [[price, size], [price, size], ...], 
"asks": [[price, size], [price, size], ...], 
"timestamp": timestamp}
The timestamp needs to being an integer with a milisecond precision.
"""


# Exceptions
class ParamsError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


# Base connector
class BaseDataConnector:
    def __init__(self, params: dict):
        self.params = params

    # Require override
    async def watch(self):
        pass

    # Override not required
    async def close(self):
        pass


# --- Connectors ---
class BinanceDataConnector(BaseDataConnector):
    def __init__(self, params: dict):
        super().__init__(params)

        # Required params
        try:
            self.market = params["market"]
        except KeyError:
            raise ParamsError("Missing required param: market")
        # Optional params
        try:
            self.limit = int(params["limit"])
        except KeyError:
            self.limit = None

        self.binance = binance_pro()

    # Override
    async def watch(self):
        order_book = (await self.binance.watch_order_book(self.market, self.limit)).copy()
        order_book.pop("datetime")
        order_book.pop("nonce")
        order_book.pop("symbol")
        order_book["timestamp"] = order_book["timestamp"] if order_book["timestamp"] is not None else \
            int(time.time() * 1000)
        return order_book

    async def close(self):
        await self.binance.close()


# ------------------

# Bindings
class ConnectorBindings:
    bindings = {'binance': BinanceDataConnector}
