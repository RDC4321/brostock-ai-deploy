import yfinance as yf
import math
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier


class StockAnalyzer:

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.data = None
        self.close_prices = None
        self.volume = None


    def fetch_data(self):
        self.data = yf.download(self.ticker, period="1y", progress=False)
        if self.data.empty:
            return False
        return True


    def prepare_data(self):
        self.close_prices = self.data["Close"]
        self.volume = self.data["Volume"]

        if hasattr(self.close_prices, "columns"):
            self.close_prices = self.close_prices.iloc[:, 0]

        if hasattr(self.volume, "columns"):
            self.volume = self.volume.iloc[:, 0]


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


    def build_features(self):

        df = self.data.copy()

        df["MA7"] = self.ma7
        df["MA21"] = self.ma21
        df["RSI"] = self.rsi
        df["MACD"] = self.macd
        df["MACD_SIGNAL"] = self.macd_signal
        df["RETURN"] = self.close_prices.pct_change()

        df.dropna(inplace=True)

        features = df[[
            "MA7",
            "MA21",
            "RSI",
            "MACD",
            "MACD_SIGNAL",
            "RETURN"
        ]]

        return df, features


    def forecast_prices(self, days_ahead, df, features):

        target = df["Close"]

        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            random_state=42
        )

        model.fit(features, target)

        last_features = features.iloc[-1:].values

        forecast_prices = []

        for _ in range(days_ahead):
            prediction = model.predict(last_features)[0]
            forecast_prices.append(prediction)

        residuals = target.values - model.predict(features)
        std_dev = np.std(residuals)

        upper_band = np.array(forecast_prices) + std_dev
        lower_band = np.array(forecast_prices) - std_dev

        last_date = self.data.index[-1]

        forecast_dates = [
            (last_date + np.timedelta64(i + 1, 'D')).strftime("%Y-%m-%d")
            for i in range(days_ahead)
        ]

        return forecast_dates, forecast_prices, upper_band, lower_band


    def generate_signal(self, df, features):
        df_ml = df.copy()

        df_ml["TARGET"] = (df_ml["Close"].shift(-1) > df_ml["Close"]).astype(int)

        df_ml = df_ml.dropna()

        X = features.loc[df_ml.index]
        y = df_ml["TARGET"].values.ravel()

        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=42
        )

        model.fit(X, y)

        latest_features = X.iloc[-1:].values

        probabilities = model.predict_proba(latest_features)[0]

        buy_prob = probabilities[1]
        sell_prob = probabilities[0]

        if buy_prob > 0.6:
            signal = "BUY"
        elif sell_prob > 0.6:
            signal = "SELL"
        else:
            signal = "HOLD"

        confidence = round(max(buy_prob, sell_prob) * 100, 2)

        importance = model.feature_importances_
        feature_names = X.columns

        importance_map = {
            feature_names[i]: round(float(importance[i]), 3)
            for i in range(len(feature_names))
        }

        return {
            "signal": signal,
            "confidence": confidence,
            "trend": "ML-based",
            "rsi": round(float(self.rsi.iloc[-1]), 2),
            "macd": "ML",
            "feature_importance": importance_map
        }


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
        percent_change = (change / previous_price) * 100

        df, features = self.build_features()

        forecast_dates, forecast_prices, upper_band, lower_band = self.forecast_prices(
            days, df, features
        )

        ai_signal = self.generate_signal(df, features)

        return {
            "ticker": self.ticker,
            "latest_price": safe_float(round(float(latest_price), 2)),
            "dates": dates,
            "datasets": {
                "prices": prices,
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
            "change": safe_float(round(float(change), 2)),
            "percent_change": safe_float(round(float(percent_change), 2)),
            "ai_signal": ai_signal
        }