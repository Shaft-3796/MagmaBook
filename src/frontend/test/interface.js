// Socket initialisation
const socket = new WebSocket('ws://localhost:10001');


// Handlers
let handlers = {
    "alert": socket_alert,
    "computed_payload": socket_computed_payload
}

function handler(data){
    let parsed = JSON.parse(data)
    console.log(parsed)
    handlers[parsed["type"]](parsed)
}

function socket_alert(data){
    console.log(data)
    alert(data["body"])
}

function socket_computed_payload(data){
    console.log(data['body'])
    let matrix = data['body']
    parseSizeToColor(matrix, 200, 0)
    plot_chart_canvas(matrix, true)
}

// REGISTER EVENTS
socket.addEventListener('message', function (event) {
    console.log('Message from server ', event.data);
    handler(event.data)
});

socket.onopen = function (event) {
    console.log('Connected to server');
    socket.send(JSON.stringify({"type": "test", "body": "foo"}))
}

socket.onerror = function (error) {
    alert("Connection to server failed, reload the page to retry.");
}