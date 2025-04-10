import pandas as pd

def calculate_equal_weighted_returns(return_data_dict):
    if not return_data_dict:
        return None, None

    returns_df = pd.concat(return_data_dict.values(), axis=1)
    returns_df.columns = return_data_dict.keys()
    returns_df.dropna(inplace=True)

    if returns_df.empty:
        return None, None

    weights = [1 / returns_df.shape[1]] * returns_df.shape[1]
    portfolio_returns = returns_df.dot(weights)
    cumulative_returns = (1 + portfolio_returns).cumprod()

    return portfolio_returns, cumulative_returns
