from stockdex import Ticker
from datetime import datetime
import pandas as pd

def price_df(ticker, start_data, end_data, dataGranularity='1d'):
    """Get price data for a given ticker."""
    ticker = Ticker(ticker)
    price = ticker.yahoo_api_price(range='5y', dataGranularity=dataGranularity)
    return price

def get_mutliple_stock_df(tickers, start_data, end_data, dataGranularity='1d'):
    """Get price data for multiple tickers."""
    all_data = []
    for ticker in tickers:
        df = price_df(ticker, start_data, end_data, dataGranularity)
        # create date column that converts timestamp to date, i.e. removes time and leaves only date
        df['date'] = df['timestamp'].dt.date
        df.set_index('date', inplace=True)
        df = df[['close']].rename(columns={'close': ticker})
        all_data.append(df)

    price = pd.concat(all_data, axis=1, join='outer')
    return price

if __name__ == "__main__":
    # Example usage
    tickers = ['AAPL', 'GOOGL', 'MSFT']
    start_data = datetime(2022, 1, 1)
    end_data = datetime(2023, 1, 1)
    dataGranularity = '1d'
    
    price_data = get_mutliple_stock_df(tickers, start_data, end_data, dataGranularity)
    print(price_data)