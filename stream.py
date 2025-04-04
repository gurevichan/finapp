import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def get_rand_data():
    """Load stock data."""
    df = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=365, freq='D'),
        'Stock A': pd.Series(range(100, 465)),
        'Stock B': pd.Series(range(200, 565)),
        'Stock C': pd.Series(range(300, 665))
    }).set_index('date')
    # Simulate some stock data
    df['Stock A'] = df['Stock A'] + (df.index.dayofyear * 0.3)
    df['Stock B'] = df['Stock B'] + (df.index.dayofyear * 0.1)
    df['Stock C'] = df['Stock C'] + (df.index.dayofyear * 0.2)
    # # Add some noise
    df['Stock A'] += np.random.normal(45, 100, size=len(df)) + np.random.normal(0, 10, size=len(df))
    df['Stock B'] += np.random.normal(-10, 50, size=len(df)) + np.random.normal(0, 5, size=len(df))
    df['Stock C'] += np.random.normal(5, 150, size=len(df)) + np.random.normal(0, 15, size=len(df))
    return df

def load_data():
    df = pd.read_csv("/Users/andreygurevich/Coding/text.csv", index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    return df

def filter_data(data, time_range):
    """Filter data based on the selected time range."""
    end_date = data.index.max()
    if "Week" in time_range:
        start_date = end_date - pd.Timedelta(days=7) * int(time_range.split()[0])
    elif "Month" in time_range:
        start_date = end_date - pd.Timedelta(days=30) * int(time_range.split()[0])
    elif "Year" in time_range:
        start_date = end_date - pd.Timedelta(days=365) * int(time_range.split()[0])
    else:
        return data
    return data.loc[start_date:end_date]

def apply_moving_average(data, window_size):
    """Apply a moving average to smooth the data."""
    return data.rolling(window=window_size).mean()

def plot_stocks(data, stocks):
    """Plot the selected stocks using Plotly."""
    fig = go.Figure()
    for stock in stocks:
        fig.add_trace(go.Scatter(x=data.index, y=data[stock], mode='lines', name=stock))
    fig.update_layout(
        title="Stock Prices Over Time",
        xaxis_title="Time",
        yaxis_title="Stock Value",
        legend_title="Stocks",
        template="plotly_white"
    )
    st.plotly_chart(fig)

def main():
    """Main function to run the Streamlit app."""
    st.title("Stock Price Visualization")    
    data = load_data()
    
    stocks = st.multiselect("Select stocks to plot:", options=data.columns, default=data.columns)    
    # time_range = st.selectbox("Select time range:", options=["Week", "Month", "Year"])
    time_range = st.selectbox("Select time range:", options=["1 Weeks", "2 Weeks", "1 Months", "3 Months", "6 Months", "1 Years", "3 Years"], index=2)
    filtered_data = filter_data(data, time_range)
    
    # Add a slider for moving average window size
    smooth = st.checkbox("Smooth data with moving average")
    if smooth:
        window_size = st.slider("Select moving average window size:", min_value=1, max_value=30, value=5)
        filtered_data = apply_moving_average(filtered_data, window_size)
    
    # Plot the selected stocks
    if stocks:
        st.write(f"Showing data for: {', '.join(stocks)}")
        plot_stocks(filtered_data, stocks)
    else:
        st.write("Please select at least one stock to display.")

if __name__ == "__main__":
    df_load = load_data()
    df_rand = get_rand_data()
    main()