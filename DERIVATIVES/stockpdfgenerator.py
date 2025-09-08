import yfinance as yf
import statistics
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

def get_data(Stock_ticker, start="2020-01-01", end="2025-6-23"):
    #input date + 1
    data = yf.download(Stock_ticker, start, end)
    return data

def get_last_quote(Stock_ticker):
    ticker = yf.Ticker(Stock_ticker)
    quote = ticker.fast_info
    return quote["lastPrice"]

def get_option_chain(Stock_ticker, expiration):
    ticker = yf.Ticker(Stock_ticker)
    opt_chain = ticker.option_chain(expiration)
    calls = opt_chain.calls[["contractSymbol", "strike", "bid", "ask", "lastPrice"]]
    puts = opt_chain.puts[["contractSymbol", "strike", "bid", "ask", "lastPrice"]]
    return calls, puts

def call_buy_prices(Stock_ticker, expiration):
    ticker = yf.Ticker(Stock_ticker)
    opt_chain = ticker.option_chain(expiration)
    call_prices = list(opt_chain.calls["ask"])
    call_strike_prices = list(opt_chain.calls["strike"])
    call_price_dict = {}
    for idx, price in enumerate(call_strike_prices):
        call_price_dict[price] = call_prices[idx]
    return call_price_dict

def call_sell_prices(Stock_ticker, expiration):
    ticker = yf.Ticker(Stock_ticker)
    opt_chain = ticker.option_chain(expiration)
    call_prices = list(opt_chain.calls["bid"])
    call_strike_prices = list(opt_chain.calls["strike"])
    call_price_dict = {}
    for idx, price in enumerate(call_strike_prices):
        call_price_dict[price] = call_prices[idx]
    return call_price_dict

def put_buy_prices(Stock_ticker, expiration):
    ticker = yf.Ticker(Stock_ticker)
    opt_chain = ticker.option_chain(expiration)
    put_prices = list(opt_chain.puts["ask"])
    put_strike_prices = list(opt_chain.puts["strike"])
    put_price_dict = {}
    for idx, price in enumerate(put_strike_prices):
        put_price_dict[price] = put_prices[idx]
    return put_price_dict

def put_sell_prices(Stock_ticker, expiration):
    ticker = yf.Ticker(Stock_ticker)
    opt_chain = ticker.option_chain(expiration)
    put_prices = list(opt_chain.puts["bid"])
    put_strike_prices = list(opt_chain.puts["strike"])
    put_price_dict = {}
    for idx, price in enumerate(put_strike_prices):
        put_price_dict[price] = put_prices[idx]
    return put_price_dict

def create_cdf_values_bear_call_method(Stock_ticker, expiration, start, end, skip):
    call_buy_prices_dict = call_buy_prices(Stock_ticker, expiration)
    call_sell_prices_dict = call_sell_prices(Stock_ticker, expiration)
    ticker = yf.Ticker(Stock_ticker)
    opt_chain = ticker.option_chain(expiration)
    pdf_dict = {}
    strikes = []
    i = 0
    while (start + i*skip) <= end + skip:
        strikes.append(round(start + i * skip, 2))
        i += 1
    strikes_lag1 = strikes.copy()
    strikes_lag1.insert(0, None)
    del strikes_lag1[-1]
    spread = strikes[1] - strikes[0]
    for idx, strike_price in enumerate(strikes_lag1):
        if idx <= 1:
            pass
        else:
            try:
                win_value = call_sell_prices_dict[strikes_lag1[idx]] - call_buy_prices_dict[strikes[idx]]
                pdf_dict[strike_price] = (spread - win_value) / spread
            except KeyError:
                pdf_dict[strike_price] = 0
    return pdf_dict

def create_cdf_values_put_spread_method(Stock_ticker, expiration, start, end, skip):
    put_buy_prices_dict = put_buy_prices(Stock_ticker, expiration)
    put_sell_prices_dict = put_sell_prices(Stock_ticker, expiration)
    ticker = yf.Ticker(Stock_ticker)
    opt_chain = ticker.option_chain(expiration)
    pdf_dict = {}
    strikes = []
    i = 0
    while (start + i*skip) <= end + skip:
        strikes.append(round(start + i * skip, 2))
        i += 1
    strikes_lag1 = strikes.copy()
    strikes_lag1.insert(0, None)
    del strikes_lag1[-1]
    win_value = strikes[1] - strikes[0]
    for idx, strike_price in enumerate(strikes_lag1):
        if idx <= 1:
            pass
        else:
            try:
                bet_value = put_buy_prices_dict[strikes[idx]] - put_sell_prices_dict[strikes_lag1[idx]]
                pdf_dict[strike_price] = bet_value/win_value
            except KeyError:
                pdf_dict[strike_price] = 0
    return pdf_dict

def create_flipped_cdf_values_call_spread_method(Stock_ticker, expiration, start, end, skip):
    call_buy_prices_dict = call_buy_prices(Stock_ticker, expiration)
    call_sell_prices_dict = call_sell_prices(Stock_ticker, expiration)
    ticker = yf.Ticker(Stock_ticker)
    opt_chain = ticker.option_chain(expiration)
    pdf_dict = {}
    strikes = []
    i = 0
    while (start + i*skip) <= end:
        strikes.append(round(start + i * skip, 2))
        i += 1
    strikes_lag1 = strikes.copy()
    strikes_lag1.insert(0, None)
    win_value = strikes[1] - strikes[0]
    for idx, strike_price in enumerate(strikes):
        if idx == 0:
            pass
        else:
            try:
                bet_value = call_buy_prices_dict[strikes_lag1[idx]] - call_sell_prices_dict[strikes[idx]]
                pdf_dict[strike_price] = bet_value/win_value
            except KeyError:
                pdf_dict[strike_price] = 0
    return pdf_dict

def create_flipped_cdf_values_bull_put_spread_method(Stock_ticker, expiration, start, end, skip):
    put_buy_prices_dict = put_buy_prices(Stock_ticker, expiration)
    put_sell_prices_dict = put_sell_prices(Stock_ticker, expiration)
    ticker = yf.Ticker(Stock_ticker)
    opt_chain = ticker.option_chain(expiration)
    pdf_dict = {}
    strikes = []
    i = 0
    while (start + i*skip) <= end:
        strikes.append(round(start + i * skip, 2))
        i += 1
    strikes_lag1 = strikes.copy()
    strikes_lag1.insert(0, None)
    spread = strikes[1] - strikes[0]
    for idx, strike_price in enumerate(strikes):
        if idx == 0:
            pass
        else:
            try:
                win_value = put_sell_prices_dict[strikes[idx]] - put_buy_prices_dict[strikes_lag1[idx]]
                pdf_dict[strike_price] = (spread-win_value) / spread
            except KeyError:
                pdf_dict[strike_price] = 0
    return pdf_dict

def create_hybrid_pdf_values(Stock_ticker, expiration, start, end, skip):
    out_the_money_CDF_values = create_cdf_values_bear_call_method(Stock_ticker, expiration, start, end, skip)
    in_the_money_CDF_values = create_cdf_values_put_spread_method(Stock_ticker, expiration, start, end, skip)
    out_the_money_flipped_CDF_values = create_flipped_cdf_values_call_spread_method(Stock_ticker, expiration, start, end, skip)
    in_the_money_flipped_CDF_values = create_flipped_cdf_values_bull_put_spread_method(Stock_ticker, expiration, start, end, skip)
    stock_price = get_last_quote(Stock_ticker)
    strikes = list(out_the_money_CDF_values.keys())
    strikes_lag1 = list(out_the_money_CDF_values.keys())
    strikes_lag1.insert(0, None)
    pdf_dict = {}
    for idx, strike in enumerate(strikes):
        if idx == 0:
            pass
        elif strike < stock_price:
            probability = in_the_money_CDF_values[strike] + in_the_money_flipped_CDF_values[strikes_lag1[idx]] - 1
            if probability < 0:
                probability = 0
            pdf_dict[strike] = probability

        elif strike >= stock_price:
            probability = out_the_money_CDF_values[strike] + out_the_money_flipped_CDF_values[strikes_lag1[idx]] - 1
            if probability < 0:
                probability = 0
            pdf_dict[strike] = probability
    return pdf_dict

def graph_the_pdf_values(Stock_ticker, expiration, start, end, skip):
    pdf_values = create_hybrid_pdf_values(Stock_ticker, expiration, start, end, skip)
    strikes = list(pdf_values.keys())
    probabilities = list(pdf_values.values())
    print(sum(probabilities))
    plt.bar(strikes, probabilities, width=2.0)
    plt.show()