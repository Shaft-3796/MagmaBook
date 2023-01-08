class App {
    constructor() {
        this.elements = {
            control: document.querySelector("div#control"),
            content: document.getElementById("content"), // Content div
            heatmap: undefined, //Placeholder
        }
        this.control = {
            dataflow_label: document.querySelector("p#data-flow-selector-on-control-label"),
            aggregation_slider: document.querySelector("input#aggregation-slider"),
            timeframe_input: document.querySelector("span#timeframe-input"),
        }
        this.charting = {
            min_timestamp: undefined, // Placeholder
            max_timestamp: undefined, // Placeholder
            price_data: undefined, // Placeholder
            chart: undefined, //Placeholder
            price_scale: undefined, //Placeholder
            price_series: undefined, //Placeholder
            elements: {
                chart_container: undefined, //Placeholder
            }
        }
        this.websocket = {
            update_price_timer: undefined, // Placeholder
            websocket_server: undefined, //Placeholder
            websocket_host: WEBSOCKET_HOST, //Placeholder
            websocket_port: WEBSOCKET_PORT, //Placeholder
        }
        this.metadata = {
            dataflow_name: "BTC",
            timeframe: "1D",
            timeframe_numerical: 1000,
            vmax: 1000,
            vmin: 0,
            vagg: 50,
        }
    }
}

async function wait_for_websocket_connection(){
    function getPromiseFromEvent(item, event) {
        return new Promise((resolve) => {
            const listener = () => {
                item.removeEventListener(event, listener);
                resolve();
            }
            item.addEventListener(event, listener);
        })
    }
    app.websocket.websocket_client = new WebSocketServer(app.websocket.websocket_host, app.websocket.websocket_port)
    await getPromiseFromEvent(app.websocket.websocket_client.socket, "open")
}


/* ENTRY POINT */
const app = new App();
async function setup_app(){
    setup_chart();
    setup_heatmap();
    setup_control();

    // Wait for websocket connection
    await wait_for_websocket_connection()

    // Request default price data
    app.websocket.websocket_client.get_initial_prices(app.metadata.dataflow_name)

    // Update historical data
    subscribe_time_range_change()

    document.onclick = function(event){
        app.websocket.websocket_client.get_heatmap(app.metadata.dataflow_name, [1672272381, 1672272791],
            18000, 16000, 100, 1000, 1)
    }


}

setup_app()
