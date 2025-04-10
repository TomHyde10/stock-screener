import streamlit as st
import plotly.figure_factory as ff
import pandas as pd
from datetime import date
import yfinance as yf

from modules.fetch_data import clean_ticker_input, get_all_data
from modules.portfolio_analysis import calculate_equal_weighted_returns

# --- Page Layout ---
st.set_page_config(page_title='Stock Screener', layout='wide')
st.title('Stock Screener')

# --- Sidebar ---
st.sidebar.title('Options')
tickers_input = st.sidebar.text_input('Enter Tickers (Comma-Separated)')
start_date = st.sidebar.date_input('Start Date', value=pd.to_datetime('2020-01-01'))
end_date = st.sidebar.date_input('End Date', value=pd.to_datetime('2024-12-31'), min_value=start_date)
create_portfolio = st.sidebar.checkbox('Create Portfolio?')

#Runs when 'Individual View' button checked
def handle_portfolio_view(tickers_list, all_return_data):
    all_returns = []
    all_labels = []

    for ticker, returns in all_return_data.items():
        if len(returns) > 1:
            all_returns.append(returns.to_numpy().flatten())
            all_labels.append(ticker)
        else:
            st.warning(f"Not enough data to calculate returns for {ticker}")

    if not all_returns:
        st.warning("No tickers had enough data to generate a distribution.")
        return

    st.header('Individual Return Distribution(s):')
    bin_size = max(0.005, 0.03 / len(all_returns))
    fig = ff.create_distplot(all_returns, group_labels=all_labels, bin_size=bin_size)
    st.plotly_chart(fig, key='Individual Distribution')

    portfolio_returns, cumulative_returns = calculate_equal_weighted_returns(all_return_data)

    if portfolio_returns is None:
        st.warning("Not enough aligned data for portfolio return calculation.")
        return

    st.header('Portfolio Return Distribution')
    port_return_dist = ff.create_distplot(
        [portfolio_returns.values],
        group_labels=['Portfolio'],
        bin_size=bin_size
    )
    st.plotly_chart(port_return_dist, key='Portfolio Distribution')

    st.header('Equal-Weighted Portfolio Return')
    st.subheader("Monthly Portfolio Return")
    st.line_chart(portfolio_returns)

    st.subheader("Cumulative Portfolio Return")
    st.line_chart(cumulative_returns)

#Runs when 'Portfolio View Clicked
def handle_individual_view(tickers_list, all_data):
    if all_data:
        st.header(f'Stock Prices from {start_date} to {end_date}')
        combined_prices = pd.concat(all_data.values(), axis=1)
        combined_prices.columns = all_data.keys()
        st.line_chart(combined_prices)

    st.header('Fundamentals Summary')
    fundamentals_list = []

    for ticker in tickers_list:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            fundamentals_list.append({
                "Ticker": ticker,
                "Company Name": info.get("longName"),
                "Sector": info.get("sector"),
                "Market Cap": info.get("marketCap"),
                "Trailing PE": info.get("trailingPE"),
                "Forward PE": info.get("forwardPE"),
                "EPS (TTM)": info.get("trailingEps"),
                "Dividend Yield": info.get("dividendYield"),
                "52-Week High": info.get("fiftyTwoWeekHigh"),
                "52-Week Low": info.get("fiftyTwoWeekLow"),
                "Price-to-Book": info.get("priceToBook"),
                "Beta": info.get("beta")
            })

        except Exception as e:
            st.warning(f"Could not fetch fundamentals for {ticker}: {e}")

    if fundamentals_list:
        fundamentals_df = pd.DataFrame(fundamentals_list)
        st.dataframe(fundamentals_df)
    else:
        st.warning("No fundamentals data could be retrieved.")


#Validates User Inputs
def validate_and_fetch_data(tickers_input, start_date, end_date): 
    if not tickers_input.strip(): #Checks if at least one ticker has been entered
        st.warning('Please enter at least one ticker symbol')
        return None, None, None

    tickers_list = clean_ticker_input(tickers_input)

    if len(tickers_list) != len(set(tickers_list)): #Checks if duplicate tickers used
        st.warning('Duplicate Tickers Used')
        return None, None, None

    all_data, all_return_data = get_all_data(tickers_list, start_date, end_date)
    return tickers_list, all_data, all_return_data

# --- Main UI logic ---
if st.sidebar.button('Individual View'):
    tickers_list, all_data, all_return_data = validate_and_fetch_data(tickers_input, start_date, end_date)
    if tickers_list:
        handle_individual_view(tickers_list, all_data)

if st.sidebar.button('Portfolio View'):
    tickers_list, all_data, all_return_data = validate_and_fetch_data(tickers_input, start_date, end_date)
    if tickers_list:
        handle_portfolio_view(tickers_list, all_return_data)
        
