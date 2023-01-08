class WebSocketServer {
    constructor(host, port) {
        this.nonce = 0
        this.socket = new WebSocket(`ws://${host}:${port}`);
        this.bindings = {
            "alert": this.handle_alert,
            "initial_prices": this.handle_initial_prices,
            "historical_prices": this.handle_historical_prices,
            "heatmap": this.handle_heatmap,
        }
        // REGISTER EVENTS
        this.socket.onmessage = (event) => {
            this.handle(event.data)
        }
        this.socket.onopen = function (event) {
            console.log('WebSocket connected');
        }
        this.socket.onerror = function (error) {
            alert("Connection to server failed, reload the page to retry.");
        }

    }
    handle(data){
        let parsed = JSON.parse(data)
        this.bindings[parsed["endpoint"]](parsed)
    }
    send(data) {
        data.nonce = this.nonce
        this.nonce += 1
        this.socket.send(JSON.stringify(data))
    }

    // Handlers
    handle_alert(data){
        alert(data["body"])
    }

    handle_initial_prices(data){
        console.log("Received initial prices")
        console.log(data)
        set_default(data.prices)
    }

    handle_historical_prices(data){
        add_historical(data.prices)
        app.websocket.update_price_timer = undefined // Release timer
    }

    handle_heatmap(data){
        console.log(data)
    }

    // Requests
    get_initial_prices(name){
        this.send({
            "endpoint": "get_initial_prices",
            "name": name,
        })
    }

    get_historical_prices(name, time_range){
        this.send({
            "endpoint": "get_historical_prices",
            "name": name,
            "time_range": time_range,
            "timeframe": app.metadata.timeframe_numerical,
        })
    }

    get_heatmap(name, time_range, vmax, vmin, vagg, max_grid_height, parse_size){
        this.send({
            "endpoint": "get_heatmap",
            "name": name,
            "time_range": time_range,
            "timeframe": app.metadata.timeframe_numerical,
            "vmax": vmax,
            "vmin": vmin,
            "vagg": vagg,
            "grid_max_height": max_grid_height,
            "parse_size": parse_size,
        })
    }
}