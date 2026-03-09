import yfinance as yf
import math
import numpy as np
from sklearn.linear_model import LinearRegression

class StockAnalyzer:

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.data = None
        self.close_prices = None
        self.volume = None
    
    def fetch_data(self):
        self.data = yf.download(self.ticker, period="3mo", progress=False)
        if self.data.empty:
            return False
        return True
    
    def prepare_data(self):
        self.close_prices = self.data["Close"]
        self.volume = self.data["Volume"]

        if hasattr(self.close_prices, "columns"):
            self.close_prices = self.close_prices.iloc[:,0]

        if hasattr(self.volume,"columns"):
            self.volume = self.volume.iloc[:,0]

    def calculate_indicators(self):

        self.ma7 = self.close_prices.rolling(window=7).mean()
        self.ma21 = self.close_prices.rolling(window=21).mean()

        delta = self.close_prices.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()

        avg_loss = avg_loss.replace(0, 1e-10)

        rs = avg_gain / avg_loss
        self.rsi = 100 - (100 / (1 + rs))

        ema12 = self.close_prices.ewm(span=12, adjust=False).mean()
        ema26 = self.close_prices.ewm(span=26, adjust=False).mean()

        self.macd = ema12 - ema26
        self.macd_signal = self.macd.ewm(span=9, adjust=False).mean()
        self.macd_hist = self.macd - self.macd_signal
    
    def build_response(self, days=7):
        def safe_float(value):
            try:
                value = float(value)
                if math.isnan(value) or math.isinf(value):
                    return None
                return value
            except:
                return None
        
        dates = self.data.index.strftime("%Y-%m-%d").tolist()
        prices = [safe_float(x) for x in self.close_prices]

        previous_price = self.close_prices.iloc[-2]
        latest_price = self.close_prices.iloc[-1]

        change = latest_price - previous_price
        percent_change = (change/previous_price) * 100

        forecast_dates, forecast_prices, upper_band, lower_band = self.forecast_prices(days)
        buy_points, sell_points, strong_buy_points, strong_sell_points = self.detect_signals()

        return{
            "ticker":self.ticker,
            "latest_price":safe_float(round(float(latest_price),2)),
            "dates": dates,
            "datasets": {
                "prices":prices,
                "ma7": [safe_float(x) for x in self.ma7],
                "ma21": [safe_float(x) for x in self.ma21],
                "rsi": [safe_float(x) for x in self.rsi],
                "volume": [safe_float(x) for x in self.volume.fillna(0)],
                "macd": [safe_float(x) for x in self.macd],
                "macd_signal": [safe_float(x) for x in self.macd_signal],
                "macd_hist": [safe_float(x) for x in self.macd_hist],
            },
            "forecast": {
                "dates": forecast_dates,
                "prices": [safe_float(x) for x in forecast_prices],
                "upper_band": [safe_float(x) for x in upper_band],
                "lower_band": [safe_float(x) for x in lower_band],
            },
            "change":safe_float(round(float(change),2)),
            "percent_change":safe_float(round(float(percent_change),2)),
            "ai_signal": self.generate_signal(),
            "signals":{
                "buy":buy_points,
                "sell": sell_points,
                "strong_buy": strong_buy_points,
                "strong_sell": strong_sell_points
            }
        }

    def forecast_prices(self, days_ahead=7):
        prices = np.array(self.close_prices).reshape(-1,1)

        X = np.arange(len(prices)).reshape(-1,1)

        model = LinearRegression()
        model.fit(X,prices)

        future_x = np.arange(len(prices), len(prices)+days_ahead).reshape(-1,1)

        forecast = model.predict(future_x)
        residuals = prices.flatten() - model.predict(X).flatten()
        std_dev = np.std(residuals)
        upper_band = forecast.flatten() + (std_dev * 1.5)
        lower_band = forecast.flatten() - (std_dev * 1.5)

        last_date = self.data.index[-1]

        forecast_dates = [
            (last_date + np.timedelta64(i+1,'D')).strftime("%Y-%m-%d")
            for i in range(days_ahead)
        ]
        
        return forecast_dates, forecast.flatten(), upper_band, lower_band

    def generate_signal(self):

        latest_rsi = self.rsi.iloc[-1]
        latest_macd = self.macd.iloc[-1]
        latest_signal = self.macd_signal.iloc[-1]
        ma7 = self.ma7.iloc[-1]
        ma21 = self.ma21.iloc[-1]

        score = 0

        # RSI momentum
        if latest_rsi < 35:
            score += 1
        elif latest_rsi > 65:
            score -= 1

        # MACD trend
        if latest_macd > latest_signal:
            score += 1
            macd_state = "Bullish Momentum"
        else:
            score -= 1
            macd_state = "Bearish Momentum"

        # Moving Average trend
        if ma7 > ma21:
            score += 1
            trend = "Bullish"
        else:
            score -= 1
            trend = "Bearish"

        # Determine signal
        if score >= 2:
            signal = "STRONG BUY"
        elif score == 1:
            signal = "BUY"
        elif score == 0:
            signal = "HOLD"
        elif score == -1:
            signal = "SELL"
        else:
            signal = "STRONG SELL"

        confidence = abs(score) * 33

        return {
            "signal": signal,
            "confidence": confidence,
            "trend": trend,
            "rsi": round(float(latest_rsi), 2),
            "macd": macd_state
        }
        
    def detect_signals(self):
        buy_points = []
        sell_points = []
        strong_buy_points = []
        strong_sell_points = []

        prices = self.close_prices.values
        ma7 = self.ma7.values
        ma21 = self.ma21.values
        rsi = self.rsi.values
        macd = self.macd.values
        signal = self.macd_signal.values

        for i in range(1, len(prices)):

            score = 0
            price = prices[i]

            # TREND
            prev_ma7 = ma7[i-1]
            prev_ma21 = ma21[i-1]
            curr_ma7 = ma7[i]
            curr_ma21 = ma21[i]

            # MOMENTUM
            curr_rsi = rsi[i]

            # MACD
            prev_macd = macd[i-1]
            prev_signal = signal[i-1]
            curr_macd = macd[i]
            curr_signal = signal[i]

            if prev_ma7 < prev_ma21 and curr_ma7 > curr_ma21:
                score += 30
            if prev_ma7 > prev_ma21 and curr_ma7 < curr_ma21:
                score -=30

            if curr_rsi < 35:
                score += 25
            elif curr_rsi > 65:
                score -= 25
            
            if prev_macd < prev_signal and curr_macd > curr_signal:
                score += 20
            if prev_macd > prev_signal and curr_macd < curr_signal:
                score -= 20
            
            if score >= 50:
                strong_buy_points.append((i,price))
            elif score >= 25:
                buy_points.append((i,price))
            elif score <= -50:
                strong_sell_points.append((i,price))
            elif score <= -25:
                sell_points.append((i,price))

        return buy_points,sell_points, strong_buy_points, strong_sell_points
        