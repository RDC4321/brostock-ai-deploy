from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from services.stock_analyzer import StockAnalyzer

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")

@app.get("/predict")
def predict(ticker: str, days: int = 7):

    analyzer = StockAnalyzer(ticker)

    if not analyzer.fetch_data():
        return {"error":"Invalid Ticker"}
    
    analyzer.prepare_data()
    analyzer.calculate_indicators()

    return analyzer.build_response(days)