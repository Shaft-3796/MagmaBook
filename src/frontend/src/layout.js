function setup_heatmap(){
    // Lightweight Charts chart div
    app.charting.elements.chart_container = document.querySelector("div.tv-lightweight-charts")
        .querySelector("table")
        .querySelectorAll("tr")[0]
        .querySelectorAll("td")[1]
        .querySelector("div")


    // Creating heatmap canvas
    heatmap = document.createElement("canvas")
    heatmap.setAttribute("id", `heatmap`)
    heatmap.style.height = "100%"
    heatmap.style.width = "100%"
    heatmap.style.position = "absolute"
    heatmap.style.top = "0"
    heatmap.style.left = "0"
    heatmap.style.zIndex = "0"
    app.charting.elements.chart_container.appendChild(heatmap)
    // For the canvas
    heatmap.setAttribute("height", `${heatmap.clientHeight}px`)
    heatmap.setAttribute("width", `${heatmap.clientWidth}px`)

    app.elements.heatmap = heatmap
}

function setup_control(){
    app.control.dataflow_label.innerText = app.metadata.dataflow_name
    app.control.aggregation_slider.value = app.metadata.vagg
    app.control.timeframe_input.innerText = app.metadata.timeframe
}



