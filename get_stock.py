from stockdex import Ticker
from datetime import datetime
import pandas as pd

HIST_STOCK_PATH = 'hist_stock_data.csv'
MONTH_STOCK_PATH = 'month_stock_data.csv'

def get_single_stock_df(ticker_str=None, isin=None, range='5y', dataGranularity='1d'):
    """Get price data for a given ticker."""
    assert ticker_str is not None or isin is not None, "Please provide either a ticker or an ISIN"
    assert ticker_str is None or isin is None, "Please provide either a ticker or an ISIN, not both"
    if ticker_str is not None:
        ticker = Ticker(ticker_str)
    elif isin is not None:
        ticker = Ticker(isin=isin)
    
    price = ticker.yahoo_api_price(range=range, dataGranularity=dataGranularity)
    return price

def get_mutliple_stock_df(tickers, save=True):
    """Get price data for multiple tickers."""
    hist_data, month_data = [], []
    for ticker in tickers:
        df = get_single_stock_df(ticker_str=ticker, range="10y", dataGranularity='1d')
        # create date column that converts timestamp to date, i.e. removes time and leaves only date
        df['date'] = df['timestamp'].dt.date
        df.set_index('date', inplace=True)
        df = df[['close']].rename(columns={'close': ticker})
        hist_data.append(df)
        df_month = get_single_stock_df(ticker_str=ticker, range='1mo', dataGranularity='30m')
        df_month['date'] = df_month['timestamp']
        df_month.set_index('date', inplace=True)
        df_month = df_month[['close']].rename(columns={'close': ticker})
        month_data.append(df_month)

    hist_price = pd.concat(hist_data, axis=1, join='outer').sort_index()
    month_price = pd.concat(month_data, axis=1, join='outer').sort_index()
    if save:
        hist_price.to_csv(HIST_STOCK_PATH)
        month_price.to_csv(MONTH_STOCK_PATH)
    return hist_price, month_price

if __name__ == "__main__":
    # Example usage
    tickers = ["QQQM", "INTC", "MBLY", "VT", "VOO", 'AAPL', 'GOOGL', 'MSFT', ] #, "IUIT"]
    start_data = datetime(2022, 1, 1)
    end_data = datetime(2023, 1, 1)
    dataGranularity = '1d'
    
    hist_price, month_price = get_mutliple_stock_df(tickers)
