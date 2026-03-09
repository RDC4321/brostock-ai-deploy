let currentMode = "technical";
import { toggleMovingAverage, renderAIChart } from "./charts.js";

export function updatePriceUI(data) {

    const priceElement = document.getElementById("priceText");
    const changeElement = document.getElementById("changeText");

    priceElement.innerHTML = `${data.ticker} $${data.latest_price}`;

    const change = data.change;
    const percent = data.percent_change;

    if (change >= 0) {
        changeElement.innerHTML = ` ▲ +${change} (${percent.toFixed(2)}%)`;
        changeElement.className = "change positive";
    } else {
        changeElement.innerHTML = ` ▼ ${change} (${percent.toFixed(2)}%)`;
        changeElement.className = "change negative";
    }
}

export function showLoading(show) {
    const loading = document.getElementById("loadingText");
    loading.style.display = show ? "inline" : "none";
}

export function showError(message) {
    alert(message);
}

export function setMode(mode) {
    currentMode = mode;

    const techPanels = document.getElementById("technicalPanels");
    const aiPanels = document.getElementById("aiPanels");

    const techBtn = document.getElementById("techMode");
    const aiBtn = document.getElementById("aiMode");

    const techControls = document.getElementById("technicalControls");
    const aiControls = document.getElementById("aiControls");
    const signalBox = document.getElementById("signalBox");

    techBtn.classList.remove("active");
    aiBtn.classList.remove("active");

    if (mode === "technical") {
        techPanels.style.display = "block";
        aiPanels.style.display = "none";
        techControls.style.display = "block";
        aiControls.style.display = "none";
        signalBox.style.display = "none";
        techBtn.classList.add("active");
    } else {
        techPanels.style.display = "none";
        aiPanels.style.display = "block";
        techControls.style.display = "none";
        aiControls.style.display = "block";
        signalBox.style.display = "block";
        aiBtn.classList.add("active");
    
        setTimeout(() =>{
            if (window.aiChartInt){
                window.aiChartInt.resize();
                window.aiChartInt.update();
            }
        }, 50);

        if(window.latestData && window.latestData.forecast){
                renderAIChart(
                    window.latestData.dates,
                    window.latestData.datasets.prices,
                    window.latestData.forecast.dates,
                    window.latestData.forecast.prices,
                    window.latestData.forecast.upper_band,
                    window.latestData.forecast.lower_band
            );
        }
    }
    document.querySelectorAll(".forecast-btn")
        .forEach(btn => btn.disabled = mode !== "ai");
}

export function initializeUI() {

    const techBtn = document.getElementById("techMode");
    const aiBtn = document.getElementById("aiMode");

    techBtn.addEventListener("click", () => setMode("technical"));
    aiBtn.addEventListener("click", () => setMode("ai"));

    const toggleMA7 = document.getElementById("toggleMA7");
    const toggleMA21 = document.getElementById("toggleMA21");

    toggleMA7.addEventListener("change", (e) => {
        toggleMovingAverage("ma7", e.target.checked);
    });
    toggleMA21.addEventListener("change", (e) => {
        toggleMovingAverage("ma21", e.target.checked);
    });

    setMode("technical");
}