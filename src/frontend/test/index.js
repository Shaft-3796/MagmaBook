const chart = window.LightweightCharts.createChart(document.querySelector("#app"), { width: document.querySelector("#app").clientWidth,
    height: document.querySelector("#app").clientHeight });

const heatmapData = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
    [13, 14, 15, 16],
];

const areaSeries = chart.addAreaSeries({
    fill: 'gradient(#ff0000, #ffff00, #00ff00, #0000ff)',
});

areaSeries.setData(heatmapData.map((row, i) => ({ x: i, y: row })));

const xAxis = chart.addXAxis();
xAxis.setLabels(['row 1', 'row 2', 'row 3', 'row 4']);

const yAxis = chart.addYAxis();
yAxis.setLabels(['col 1', 'col 2', 'col 3', 'col 4']);