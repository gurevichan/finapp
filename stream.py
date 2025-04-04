import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def load_data(path="stock_data.csv"):
    df = pd.read_csv(path, index_col=0, parse_dates=True)
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

def normalize_to_first_date(data):
    """Normalize data so the first date in the range is zero for all stocks."""
    return (data/data.iloc[0] - 1) * 100

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
    time_range = st.selectbox("Select time range:", options=["1 Weeks", "2 Weeks", "1 Months", "3 Months", "6 Months", "1 Years", "3 Years"], index=2)
    filtered_data = filter_data(data, time_range)
    
    # Add a checkbox for relative Y-axis normalization
    relative_y_axis = st.checkbox("Relative Y axis", value=True)
    # Add a radio button to select the stock to normalize to
    normalize_stock = st.radio("Normalize to:", options=["First Date"] + list(data.columns), index=0)

    if relative_y_axis:
        filtered_data = normalize_to_first_date(filtered_data)        
    if normalize_stock != "First Date":
        # subtract normalize_stock from all stocks
        filtered_data = filtered_data.apply(lambda x: x - filtered_data[normalize_stock] if x.name != normalize_stock else x)
        filtered_data[normalize_stock] = 0

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
    # data = load_data('/Users/andreygurevich/Coding/fin_app/test_stocks.csv')
    main()