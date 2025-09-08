import yfinance as yf
import statistics
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

#Call - Put = Stock Price - Strike + Carrying Costs - Dividends
#buy Call, sell put, short
#sell call, buy put, buy stock

def get_option_chain(Stock_ticker, expiration):
    ticker = yf.Ticker(Stock_ticker)
    opt_chain = ticker.option_chain(expiration)
    calls = opt_chain.calls[["contractSymbol", "strike", "bid", "ask", "lastPrice"]]
    puts = opt_chain.puts[["contractSymbol", "strike", "bid", "ask", "lastPrice"]]
    return calls, puts

def get_implied_interest_rates(Stock_ticker, expiration, payouts_until_exp, annual_payounts, expected_dividends=-1):
    ticker = yf.Ticker(Stock_ticker)
    quote = ticker.info
    if expected_dividends == -1:
        expected_dividends = quote["trailingAnnualDividendRate"] * payouts_until_exp/annual_payounts
    opt_chain = ticker.option_chain(expiration)
    call_ask_prices = list(opt_chain.calls["ask"])
    call_bid_prices = list(opt_chain.calls["bid"])
    put_ask_prices = list(opt_chain.puts["ask"])
    put_bid_prices = list(opt_chain.puts["bid"])
    call_strike_prices = list(opt_chain.calls["strike"])
    put_strike_prices = list(opt_chain.puts["strike"])
    bid_ask_call_dict = {}
    bid_ask_put_dict = {}
    for idx, strike in enumerate(call_strike_prices):
        bid_ask_call_dict[strike] = (call_bid_prices[idx], call_ask_prices[idx])
    for idx, strike in enumerate(put_strike_prices):
        bid_ask_put_dict[strike] = (put_bid_prices[idx], put_ask_prices[idx])
    interest_rates = {}
    for strike in bid_ask_call_dict.keys():
        key_error = False
        try:
            call_bid, call_ask = bid_ask_call_dict[strike]
            put_bid, put_ask = bid_ask_put_dict[strike]
        except KeyError:
            key_error = True
            pass
        if not key_error:
            cheap_synthetic_forward_scenario = call_ask - put_bid
            cheap_synthetic_short_scenario = call_bid - put_ask
            interest_rates[strike] = calculate_interest_rate(cheap_synthetic_forward_scenario, cheap_synthetic_short_scenario, strike, quote.get("bid"), quote.get("ask"), expected_dividends)
    
    return interest_rates

#    synthetic_forward < stock - strike + carrying_costs - dividends
#    → Arbitrage trade:
#    Buy call
#    Sell put
#    Short stock
#    (Invest PV(K))

#    synthetic_short > stock - strike +carrying_costs - dividends
#    → Arbitrage trade:
#    Sell call
#    Buy put
#    Buy stock
#    (Borrow PV(K) if needed
    
def calculate_interest_rate(synthetic_forward, synthetic_short, strike, stock_price_bid, stock_price_ask, expected_dividends=0):
    carrying_costs_exp = synthetic_forward - stock_price_bid + strike + expected_dividends
    carrying_costs_chp = synthetic_short - stock_price_ask + strike + expected_dividends
    return (carrying_costs_chp/strike, carrying_costs_exp/strike)

def find_arbitrages(Stock_ticker, expiration, yearly_interest_rate, days_until_exp, payouts_until_exp, annual_payounts, expected_dividends=-1):
    ticker = yf.Ticker(Stock_ticker)
    quote = ticker.info
    if expected_dividends == -1:
        expected_dividends = quote["trailingAnnualDividendRate"] * payouts_until_exp/annual_payounts
    opt_chain = ticker.option_chain(expiration)
    call_ask_prices = list(opt_chain.calls["ask"])
    call_bid_prices = list(opt_chain.calls["bid"])
    put_ask_prices = list(opt_chain.puts["ask"])
    put_bid_prices = list(opt_chain.puts["bid"])
    call_strike_prices = list(opt_chain.calls["strike"])
    put_strike_prices = list(opt_chain.puts["strike"])
    bid_ask_call_dict = {}
    bid_ask_put_dict = {}
    for idx, strike in enumerate(call_strike_prices):
        bid_ask_call_dict[strike] = (call_bid_prices[idx], call_ask_prices[idx])
    for idx, strike in enumerate(put_strike_prices):
        bid_ask_put_dict[strike] = (put_bid_prices[idx], put_ask_prices[idx])
    synthetic_short_opportunities = {}
    synthetic_long_opportunities = {}
    for strike in bid_ask_call_dict.keys():
        key_error = False
        try:
            call_bid, call_ask = bid_ask_call_dict[strike]
            put_bid, put_ask = bid_ask_put_dict[strike]
        except KeyError:
            key_error = True
            pass
        if not key_error:
            cheap_synthetic_forward_scenario = call_ask - put_bid
            cheap_synthetic_short_scenario = call_bid - put_ask
            carrying_costs = strike * math.exp(yearly_interest_rate*days_until_exp/365) - strike
            if strike == 635:
                print(call_ask, put_bid)
            if cheap_synthetic_forward_scenario < quote.get("bid") - strike + carrying_costs - expected_dividends:
                synthetic_long_opportunities[strike] = -cheap_synthetic_forward_scenario + (quote.get("bid") - strike + carrying_costs - expected_dividends), (bid_ask_call_dict[strike], bid_ask_put_dict[strike])
            if cheap_synthetic_short_scenario > quote.get("ask") - strike + carrying_costs - expected_dividends:
                synthetic_short_opportunities[strike] = cheap_synthetic_short_scenario - (quote.get("ask") - strike + carrying_costs - expected_dividends), (bid_ask_call_dict[strike], bid_ask_put_dict[strike])
    return synthetic_long_opportunities, synthetic_short_opportunities