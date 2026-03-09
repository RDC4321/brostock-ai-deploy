export async function fetchStock(ticker,days) {
    const response = await fetch(`/predict?ticker=${ticker}&days=${days}`);
    const data = await response.json();
    return data;
}