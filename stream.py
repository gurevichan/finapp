import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from get_stock import MONTH_STOCK_PATH, HIST_STOCK_PATH


# Constants
TIME_RANGES = ["1 Weeks", "2 Weeks", "1 Months", "3 Months", "6 Months", "1 Year", "2 Years", "5 Years"]
# Force wider layout using latest working CSS hack
st.set_page_config(layout="wide")

st.markdown("""
    <style>
        /* Make main content wider */
        section.main > div { max-width: 95% !important; }
    </style>
""", unsafe_allow_html=True)

import pandas as pd
import streamlit as st

def color_performance(val, max_diff=20):
    """
    Colors cell background:
    - Green for positive values, red for negative.
    - Color intensity reflects magnitude.
    """
    try:
        val_float = float(val)
        #: check that val_float is a number
        if np.isnan(val_float):
            return ""
    except:
        return ""

    # Cap values for intensity scaling
    max_diff = 20
    capped = min(abs(val_float), max_diff)
    intensity = int(255 * (capped / max_diff))  # Scale 0–max_diff to 0–255

    if val_float > 0:
        return f"background-color: rgba(0, {intensity}, 0, 0.5)"
    elif val_float < 0:
        return f"background-color: rgba({intensity}, 0, 0, 0.5)"
    else:
        return ""

def load_data(path="stock_data.csv"):
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    return df

def filter_data(data, time_range):
    curr_data = data.copy()
    end_date = curr_data.index.max()
    start_date = calc_start_date(time_range, end_date)
    return curr_data.loc[(curr_data.index >= start_date) & (curr_data.index <= end_date)]

def calc_start_date(time_range, end_date):
    if "Week" in time_range:
        start_date = end_date - pd.Timedelta(days=7) * int(time_range.split()[0])
    elif "Month" in time_range:
        start_date = end_date - pd.Timedelta(days=30) * int(time_range.split()[0])
    elif "Year" in time_range:
        start_date = end_date - pd.Timedelta(days=365) * int(time_range.split()[0])
    else:
        start_date = end_date - pd.Timedelta(days=365 * 5)
    return start_date

def apply_moving_average(data, window_size):
    return data.rolling(window=window_size).mean()

def normalize_to_value(data, value):
    return (data / value - 1) * 100

def plot_stocks(data, stocks):
    fig = go.Figure()

    for stock in stocks:
        fig.add_trace(go.Scatter(
            x=data.index.astype(str),  # Convert timestamps to strings
            y=data[stock],
            mode='lines',
            name=stock
        ))

    fig.update_layout(
        title="Stock Prices Over Time",
        xaxis_title="Time",
        yaxis_title="Stock Value",
        legend_title="Stocks",
        template="plotly_dark",
        xaxis=dict(
            type='category', # Force categorical x-axis to skip empty dates and times
            tickmode='linear',
            dtick=13  # Show one tick every 20 data points (tune this as needed)
        )
    )

    st.plotly_chart(fig, use_container_width=True)

def calculate_performance(data, time_ranges):
    performance = {}
    for stock in data.columns:
        end_date = data.index.max()
        last_price = data[stock][end_date]
        
        stock_performance = []
        for time_range in time_ranges:
            start_date = calc_start_date(time_range, end_date)
            closest_date = data.loc[(data.index >= start_date)][stock].index[0]
            start_price = data[stock][closest_date]
            # if the found date is too far from intended date skip it
            if (start_date - closest_date).days > 5:
                stock_performance.append(0)
                continue
            if start_price != 0:
                perf = ((last_price - start_price) / start_price) * 100
            else:
                perf = 0
            stock_performance.append(perf)

        performance[stock] = stock_performance
    return pd.DataFrame(performance, index=time_ranges).T

def main():
    st.title("Stock Price Visualization")
    hist_data = load_data(HIST_STOCK_PATH)
    month_data = load_data(MONTH_STOCK_PATH)
    stocks = hist_data.columns.tolist()

    # Sidebar controls
    with st.sidebar:
        stocks = st.multiselect("Select stocks to plot:", options=stocks, default=stocks)    
        relative_y_axis = st.checkbox("Relative Y axis", value=True)
        normalize_stock = st.radio("Normalize to:", options=["First Date", "First Week"] + list(stocks), index=0, horizontal=False)
        smooth = st.checkbox("Smooth data with moving average")
        if smooth:
            window_size = st.slider("Moving average window size:", min_value=1, max_value=30, value=5)
    
    time_range = st.radio("Select time range:", 
                          options=TIME_RANGES, index=2,
                          horizontal=True)

    # Data processing
    data = month_data if time_range in ["1 Weeks", "2 Weeks", "1 Months"] else hist_data
    filtered_data = filter_data(data, time_range)

    filtered_data = normalize_data(relative_y_axis, normalize_stock, filtered_data)
    if smooth:
        filtered_data = apply_moving_average(filtered_data, window_size)

    # Plot
    if stocks:
        plot_stocks(filtered_data, stocks)
    else:
        st.write("Please select at least one stock to display.")

    # Performance table
    table_data = hist_data[stocks].copy()
    if not (normalize_stock in ["First Date", "First Week"]):
        table_data = normalize_to_stock(normalize_stock, table_data)
    performance_table = calculate_performance(table_data, TIME_RANGES)
    # Assuming `performance_table` is a DataFrame of floats (as %)
    styled_df = performance_table.style \
        .format("{:.2f}%") \
        .applymap(color_performance)

    st.write("### Stock Performance Summary")
    st.dataframe(styled_df)

def normalize_data(relative_y_axis, normalize_stock, filtered_data):
    if relative_y_axis:
        if "First" in normalize_stock:
            if "Date" in normalize_stock:
                normalization_val = filtered_data.iloc[0]
            elif "Week" in normalize_stock:
                end_date = filtered_data.index[0] + pd.Timedelta(days=7)
                normalization_val = filtered_data.loc[filtered_data.index <= end_date].mean()
            filtered_data = normalize_to_value(filtered_data, normalization_val)
        else:
            filtered_data = normalize_to_value(filtered_data, filtered_data.iloc[0]) # normalize to first date first TODO: better way?
            filtered_data = normalize_to_stock(normalize_stock, filtered_data)
    return filtered_data

def normalize_to_stock(normalize_stock, filtered_data):
    filtered_data = filtered_data.apply(
            lambda x: x - filtered_data[normalize_stock] if x.name != normalize_stock else x)
    filtered_data[normalize_stock] = 0
    return filtered_data
    # st.dataframe(performance_table.style.format("{:.2f}%"))


if __name__ == "__main__":
    main()
