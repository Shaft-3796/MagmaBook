import asyncio
import json
import threading

from websockets import serve
from websockets.exceptions import ConnectionClosed
from bottle import route, run, static_file

from backend.python.src.API import API


# Websocket server
class WebsocketServer:
    def __init__(self, host, port, api):
        self.host = host
        self.port = port
        self.api = api
        self.connections = []

    def start(self):
        async def main():
            async with serve(self.handler, self.host, self.port):
                await asyncio.Future()  # run forever

        # threading.Thread(target=asyncio.run, args=(main(),)).start()  # NON-BLOCKING CALL
        self.log_server_started()
        asyncio.run(main())  # BLOCKING CALL

    async def handler(self, websocket, path):
        self.connections.append(websocket)
        self.log_new_connection(websocket)
        nonces = [-1 for i in range(10)]  # Nonce used to avoid requests duplication
        while True:
            try:
                _data = (await websocket.recv()).replace('\\', '').lstrip('"').rstrip('"')
                parsed_data = json.loads(_data)

                # -- NONCE TO ENSURE NO DUPLICATION OF REQUESTS --
                nonce = parsed_data["nonce"]
                if nonce in nonces:
                    continue
                nonces.append(nonce)
                nonces.pop(0)
                # ------------------------------------------------

                self.log_data_recieved(websocket, parsed_data)
                self.api.call(WebsocketServer.response, websocket, parsed_data)  # NON BLOCKING API CALL (returns almost immediately)
            except ConnectionClosed:
                self.log_connection_closed(websocket)
                try:
                    self.connections.remove(websocket)
                except ValueError:
                    pass
                return # Stop the handler


    @staticmethod
    def response(connection, data):
        response = json.dumps(data)
        WebsocketServer.log_data_sent(connection, data)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(connection.send(response))

    # LOG ----------------------------------
    def log_server_started(self):
        print(f"Websocket server started on {self.host}:{self.port}")

    @staticmethod
    def log_new_connection(connection):
        host = connection.remote_address[0]
        port = connection.remote_address[1]
        print(f"<SocketServer>: NewConnectionEstablished Remote: {host}:{port}")

    @staticmethod
    def log_connection_closed(connection):
        host = connection.remote_address[0]
        port = connection.remote_address[1]
        print(f"<SocketServer>: ConnectionClosed Remote: {host}:{port}")

    @staticmethod
    def log_data_recieved(connection, data):
        host = connection.remote_address[0]
        port = connection.remote_address[1]
        print(f"<SocketServer>: {host}:{port} --> {data}")

    @staticmethod
    def log_data_sent(connection, data):
        host = connection.remote_address[0]
        port = connection.remote_address[1]
        print(f"<SocketServer>: {host}:{port} <-- {data['endpoint']}")


# HTTP server
def start_http_server(host, port, frontend_path):
    @route('/')
    def get_index():
        return static_file("index.html", root=frontend_path)

    @route('/<filepath:path>')
    def get_server_static(filepath):
        return static_file(filepath, root=frontend_path)

    # threading.Thread(target=run, kwargs={"host": host, "port": port}).start() NON BLOCKING CALL
    run(host=host, port=port)  # BLOCKING CALL


# Application
class App:
    def __init__(self, host, http_port, websocket_port, frontend_path, api_root_path, wakeup=False):
        self.host = str(host)
        self.http_port = str(http_port)
        self.websocket_port = str(websocket_port)
        self.frontend_path = frontend_path
        self.api = API(api_root_path, wakeup)
        self.websocket_server = WebsocketServer(self.host, self.websocket_port, self.api)
        with open(self.frontend_path + "/config.js", "w") as f:
            with open(self.frontend_path + "/config_template.tpl", "r") as t:
                f.write(t.read().replace("{{port}}", self.websocket_port).replace("{{host}}", self.host))

    def start(self):
        threading.Thread(target=self.websocket_server.start).start()
        start_http_server(self.host, self.http_port, self.frontend_path)


App("localhost",
    10000, 10001,
    "/media/x/Projects/Dev/Web/MagmaBook/frontend/src",
    "/media/x/Projects/Dev/Web/MagmaBook/backend/python/DataFlows",
    False).start()
