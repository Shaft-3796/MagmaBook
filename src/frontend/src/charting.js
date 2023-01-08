function setup_chart(){
    app.charting.chart = window.LightweightCharts.createChart(app.elements.content, { width: app.elements.content.clientWidth,
        height: app.elements.content.clientHeight });


    // Price scale selection
    app.charting.price_scale = app.charting.chart.priceScale("left");
    app.charting.price_scale.applyOptions({"visible": true})
    app.charting.chart.priceScale("right").applyOptions({"visible": false})

    // time scale options
    app.charting.chart.timeScale().applyOptions({"timeVisible": true})

    // Background styling
    app.charting.chart.applyOptions({
        layout: {
            background: { color: 'rgba(0, 0, 0, 0)' }, // No background color
            textColor: '#DDD',
        },
        grid: {
            vertLines: { visible: false },
            horzLines: { visible: false },
        },
    });

    app.charting.price_series = app.charting.chart.addCandlestickSeries();
}

function add_historical(historical){
    data = [...historical, ...app.charting.price_data];
    app.charting.price_data = data;
    app.charting.price_series.setData(data);
}

function add_new(data){
    for(item of data){
        app.charting.price_data.push(item); // TODO HANDLE CANDLE UPDATE
        app.charting.price_series.update(item);
    }
}

function set_default(data){
    app.charting.price_data = data;
    app.charting.price_series.setData(data);
    app.charting.chart.timeScale().setVisibleLogicalRange({from: data[0].time, to: data[data.length-1].time});
    app.charting.price_scale.applyOptions({"autoScale": false})

}

function get_visible_time_range(){
    const barsInfo = app.charting.price_series.barsInLogicalRange(app.charting.chart.timeScale().getVisibleLogicalRange());
    let new_end; let new_start;
    if(barsInfo.barsBefore >= 0){
        new_start = barsInfo.from
    }
    else{
        new_start = barsInfo.from + app.metadata.timeframe_numerical*(Math.floor(barsInfo.barsBefore))
    }
    if(barsInfo.barsAfter >= 0){
        new_end = barsInfo.to
    }
    else{
        new_end = barsInfo.to - app.metadata.timeframe_numerical*(Math.floor(barsInfo.barsAfter))
    }
    return [new_start, new_end]
}

function subscribe_time_range_change(){
    app.charting.chart.timeScale().subscribeVisibleLogicalRangeChange(() => {
        if (app.websocket.update_price_timer !== undefined) {
            return;
        }
        app.websocket.update_price_timer = setTimeout(() => {
            let logicalRange = app.charting.chart.timeScale().getVisibleLogicalRange();
            if (logicalRange !== null) {
                const barsInfo = app.charting.price_series.barsInLogicalRange(app.charting.chart.timeScale().getVisibleLogicalRange())
                if(barsInfo.barsBefore < 10){
                    let number = Math.round(Math.abs(barsInfo.barsBefore)) + 500
                    let from = app.charting.price_data[0].time - number*(app.metadata.timeframe_numerical/1000)
                    let to = app.charting.price_data[0].time - (app.metadata.timeframe_numerical/1000)
                    app.websocket.websocket_client.get_historical_prices(app.metadata.dataflow_name, [from, to])
                }
                else{
                    app.websocket.update_price_timer = undefined
                }
            }
        }, 50);
    })
}