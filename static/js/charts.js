let charts = {
    price: null,
    rsi: null,
    macd: null
};

export function renderPriceChart(data,signals) {

    const ctx = document.getElementById("stockChart").getContext("2d");
    const buyMarkers = signals?.buy.map(point => ({
        x: data.dates[point[0]],
        y: point[1]
    })) || [];
    const sellMarkers = signals?.sell.map(point => ({
        x: data.dates[point[0]],
        y:point[1]
    })) || [];
    const strongBuyMarkers = signals?.strong_buy?.map(point => ({
        x: data.dates[point[0]],
        y: point[1]
    })) || [];
    const strongSellMarkers = signals?.strong_sell?.map(point => ({
        x: data.dates[point[0]],
        y: point[1]
    })) || [];

    if (charts.price) charts.price.destroy();

    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, "rgba(0,255,204,0.8)");
    gradient.addColorStop(1, "rgba(0,255,204,0.05)");

    charts.price = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.dates,
            datasets: [
                {
                    type: "bar",
                    label: "Volume",
                    data: data.datasets.volume,
                    yAxisID: "yVolume",
                    backgroundColor: "rgba(0,255,204,0.15)",
                    borderWidth: 0
                },
                {
                    label: data.ticker + " Price",
                    data: data.datasets.prices,
                    borderColor: "#00ffcc",
                    backgroundColor: gradient,
                    fill: true,
                    borderWidth: 3,
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label: "MA 7",
                    data: data.datasets.ma7,
                    borderColor: "#FFD700",
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 0,
                    fill: false
                },
                {
                    label: "MA 21",
                    data: data.datasets.ma21,
                    borderColor: "#FF8C00",
                    borderWidth: 1.5,
                    tension: 0.4,
                    pointRadius: 0,
                    fill: false
                },
                {
                    type: "scatter",
                    label: "Buy Signal",
                    data: buyMarkers,
                    pointBackgroundColor: "#00ff88",
                    pointBorderColor: "#00ff88",
                    pointRadius: 6,
                    pointHoverRadius: 10,
                    borderWidth: 2,
                    pointStyle: "triangle",
                },
                {
                    type: "scatter",
                    label: "Sell Signal",
                    data: sellMarkers,
                    pointBackgroundColor: "#ff4d4d",
                    pointBorderColor: "#ff4d4d",
                    pointRadius: 6,
                    pointHoverRadius: 10,
                    borderWidth: 2,
                    pointStyle: "triangle",
                    rotation: 180
                },
                {
                    type: "scatter",
                    label: "Strong Buy",
                    data: strongBuyMarkers,
                    pointBackgroundColor: "#00ffcc",
                    pointBorderColor: "#00ffcc",
                    pointRadius: 10,
                    pointHoverRadius: 12,
                    borderWidth: 2,
                    pointStyle: "star"
                },
                {
                    type: "scatter",
                    label: "Strong Sell",
                    data: strongSellMarkers,
                    pointBackgroundColor: "#ff0066",
                    pointBorderColor: "#ff0066",
                    pointRadius: 10,
                    pointHoverRadius: 12,
                    borderWidth: 2,
                    pointStyle: "rectRot"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 200
            },
            plugins: {
                legend: {
                    labels: { color: "white" }
                }
            },
            scales: {
                x: {
                    ticks: { color: "white" },
                    grid: { color: "rgba(255,255,255,0.1)" }
                },
                y: {
                    ticks: { color: "white" },
                    grid: { color: "rgba(255,255,255,0.1)" }
                },
                yVolume: {
                    position: "right",
                    grid: { display: false },
                    ticks: { display: false }
                }
            }
        }
    });

    renderRSIChart(data);
}

function renderRSIChart(data) {

    const ctx = document.getElementById("rsiChart").getContext("2d");

    if (charts.rsi) charts.rsi.destroy();

    charts.rsi = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.dates,
            datasets: [
                {
                    label: "RSI (14)",
                    data: data.datasets.rsi,
                    borderColor: "#ff00ff",
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: 0
                },
                {
                    label: "Overbought",
                    data: new Array(data.dates.length).fill(70),
                    borderColor: "rgba(255,0,0,0.5)",
                    borderDash: [5,5],
                    pointRadius: 0
                },
                {
                    label: "Oversold",
                    data: new Array(data.dates.length).fill(30),
                    borderColor: "rgba(0,255,0,0.5)",
                    borderDash: [5,5],
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 200
            },
            plugins: {
                legend: { labels: { color: "white" } }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    ticks: { color: "white" },
                    grid: { color: "rgba(255,255,255,0.1)" }
                },
                x: { display: false }
            }
        }
    });
}

export function renderMACD(data) {

    const ctx = document.getElementById("macdChart").getContext("2d");

    if (charts.macd) charts.macd.destroy();

    charts.macd = new Chart(ctx, {
        type: "bar",
        data: {
            labels: data.dates,
            datasets: [
                {
                    type: "bar",
                    label: "Histogram",
                    data: data.datasets.macd_hist,
                    backgroundColor: data.datasets.macd_hist.map(v =>
                        v >= 0 ? "rgba(0,255,0,0.6)" : "rgba(255,0,0,0.6)"
                    )
                },
                {
                    type: "line",
                    label: "MACD",
                    data: data.datasets.macd,
                    borderColor: "#00ffff",
                    borderWidth: 2,
                    pointRadius: 0
                },
                {
                    type: "line",
                    label: "Signal",
                    data: data.datasets.macd_signal,
                    borderColor: "#ffcc00",
                    borderWidth: 2,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 200
            },
            plugins: {
                legend: { labels: { color: "white" } }
            },
            scales: {
                x: { display: false },
                y: {
                    ticks: { color: "white" },
                    grid: { color: "rgba(255,255,255,0.1)" }
                }
            }
        }
    });
}

export function toggleMovingAverage(type, visible){
    if (!charts.price) return;
    const datasetIndex = type === "ma7" ? 2 : 3;
    charts.price.data.datasets[datasetIndex].hidden = !visible;
    charts.price.update();
}

export function renderAIChart(dates, prices, forecastDates = [], forecastPrices = [], upperBand = [], lowerBand = []){
    const ctx = document.getElementById("aiChart").getContext("2d");

    if (window.aiChartInt){
        window.aiChartInt.destroy();
    }
    window.aiChartInt = new Chart(ctx, {
        type: "line",
        data: {
            labels: [...dates, ...forecastDates],
            datasets: [
                {
                    label: "Historical Price",
                    data: [...prices, ...Array(forecastPrices.length).fill(null)],
                    borderColor: "#00ffcc",
                    borderWidth: 3,
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label: "AI Forecast",
                    data: [
                        ...Array(prices.length).fill(null),
                        ...forecastPrices
                    ],
                    borderColor: "#ff00ff",
                    borderDash: [6,6],
                    borderWidth: 3,
                    tension: 0.4,
                    pointRadius: 0
                },
                {
                    label:"Upper Bound",
                    data:[...Array(prices.length).fill(null), ...upperBand],
                    borderColor:"rgba(255,0,255,0.3)",
                    borderWidth:1,
                    pointRadius:0
                },
                {
                    label:"Lower Bound",
                    data:[...Array(prices.length).fill(null), ...lowerBand],
                    borderColor:"rgba(255,0,255,0.3)",
                    borderWidth:1,
                    pointRadius:0,
                    fill:"-1",
                    backgroundColor:"rgba(255,0,255,0.12)"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation:{
                duration:200
            },
            interaction:{
                intersect:false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    labels: {color: "white"}
                }
            },
            scales: {
                x: {
                    ticks: {color: "white"},
                    grid: {color: "rgba(255,255,255,0.1)"}
                },
                y: {
                    ticks: {color: "white"},
                    grid: {color: "rgba(255,255,255,0.1)"}
                }
            }
        }
    });
}