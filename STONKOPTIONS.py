import yfinance as yf
import statistics
import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

def test(x):
    print(x)
def get_data(Stock_ticker, start="2020-01-01", end="2025-3-06"):
    #input date + 1
    data = yf.download(Stock_ticker, start, end)
    return data

def get_last_quote(data):
    last_quote = data["Close"].iloc[-1]
    return last_quote

def get_list_of_changes_prop_to_mean_at_a_price(data, quote):
    stonk_data = pd.DataFrame(data)
    list_of_changes = []
    for x in range(len(stonk_data) - 1):
        close, close_next_day = (stonk_data.iloc[x,3], stonk_data.iloc[x + 1,3])
        list_of_changes.append((close_next_day - close) * quote / close)
    return list_of_changes

def get_list_of_changes_prop_to_mean(data):
    """
    """
    stonk_data = pd.DataFrame(data)
    list_of_changes = []
    for x in range(len(stonk_data) - 1):
        close, close_next_day = (stonk_data.iloc[x,3], stonk_data.iloc[x + 1,3])
        list_of_changes.append((close_next_day - close)/close)
    return list_of_changes

def get_list_of_changes_prop_to_mean_over_time_period_at_a_price(data, time_period, price):
    stonk_data = pd.DataFrame(data)
    list_of_changes = []
    for x in range(len(stonk_data) - time_period):
        close, close_next_day = (stonk_data.iloc[x,3], stonk_data.iloc[x + time_period,3])
        list_of_changes.append((close_next_day - close) * price / close)
    return list_of_changes

def get_average_and_standard_deviation_of_daily_changes_prop_to_mean(data):
    list_o_changes = get_list_of_changes_prop_to_mean(data)
    s = round(statistics.stdev(list_o_changes), 4)
    m = round(statistics.mean(list_o_changes), 4)
    return (m, s)

def get_average_and_standard_deviation_of_time_period_prop_to_mean(data, time_period):
    (mean, stdev) = get_average_and_standard_deviation_of_daily_changes_prop_to_mean(data)
    return (time_period * mean, math.sqrt(time_period * (stdev ** 2)))

def get_average_and_standard_deviation_of_time_period_prop_to_mean2(data, time_period):
    stonk_data = pd.DataFrame(data)
    list_of_changes = []
    for x in range(len(stonk_data) - time_period):
        close, close_next_day = (stonk_data.iloc[x,3], stonk_data.iloc[x + time_period,3])
        list_of_changes.append((close_next_day - close)/close)
    s = round(statistics.stdev(list_of_changes), 4)
    m = round(statistics.mean(list_of_changes), 4)
    return (m, s)

def get_call_price(data, Strike_price, time_period, current_price, drift=False):
    (mean_p, stdev_p) = get_average_and_standard_deviation_of_time_period_prop_to_mean(data, 
        time_period)
    (mean, stdev) = (mean_p * current_price, stdev_p * current_price)
    if not drift:
        mean = 0
    part1 = (current_price - Strike_price) * (1 - norm.cdf(((Strike_price - 
        current_price) - mean)/stdev))
    part2 = mean * (1 - norm.cdf((Strike_price - current_price - mean)/stdev))
    part3 = (stdev / math.sqrt(2 * 3.14159)) * math.exp(-((current_price ** 2) +
        ((2 * mean - 2 * Strike_price) * current_price) + (Strike_price ** 2) +
        (mean ** 2) - (2 * mean * Strike_price))/(2 * (stdev ** 2)))
    return part1 + part2 + part3

def get_put_price(data, Strike_price, time_period, current_price, drift=False):
    (mean_p, stdev_p) = get_average_and_standard_deviation_of_time_period_prop_to_mean(data, time_period)
    (mean, stdev) = (mean_p * current_price, stdev_p * current_price)
    if not drift:
        mean = 0
    efactor = (math.exp(((Strike_price * mean)/(stdev ** 2)) + ((Strike_price * current_price)/(stdev ** 2))) - math.exp((Strike_price ** 2)/(2 * (stdev ** 2))))
    part1 = Strike_price * norm.cdf((-current_price - mean)/stdev)
    part2 = (Strike_price - current_price) * (norm.cdf((Strike_price - current_price - mean)/stdev) - norm.cdf((-current_price - mean)/stdev))
    part3 = -mean * (norm.cdf((Strike_price - current_price - mean)/stdev) - norm.cdf((-current_price - mean)/stdev))
    part4 = math.exp(-(mean ** 2)/(2 * (stdev ** 2)) - (mean * current_price / (stdev ** 2)) - ((Strike_price ** 2)/(2 * (stdev ** 2))) - ((current_price ** 2)/(2 * (stdev ** 2)))) * stdev * efactor / (math.sqrt(3.14159 * 2))
    return part1 + part2 + part3 + part4

def make_a_histogram(data):
    data_mod = get_list_of_changes_prop_to_mean(data)
    plt.hist(data_mod, bins=50, edgecolor="black")
    plt.title("Histogram")
    plt.xlabel("Change in Price")
    plt.ylabel("Frequency")
    plt.show()

def make_a_histogram2(data, time_period, last_quote):
    data_mod = get_list_of_changes_prop_to_mean_over_time_period_at_a_price(data, time_period, last_quote)
    plt.hist(data_mod, bins=50, edgecolor="black")
    plt.title("Histogram")
    plt.xlabel("Change in Price")
    plt.ylabel("Frequency")
    plt.show()

def make_a_histogram3(data):
    plt.hist(data, bins=50, edgecolor="black")
    plt.title("Histogram")
    plt.xlabel("Change in Price")
    plt.ylabel("Frequency")
    plt.show()


def find_stdev(option_price):
    ###
    return
def find_daily_stdev(option_price, days_til_exp):
    total_stdev = find_stdev(option_price)
    return total_stdev / math.sqrt(days_til_exp)
def make_a_histogram_with_stdev_and_mean_change(stdev, mean_change=0):
    data = np.random.normal(loc=mean_change, scale=stdev, size=1000)
    make_a_histogram3(data)
    return
def run_test():
    data = get_data("KSS")
    t = get_average_and_standard_deviation_of_daily_changes_prop_to_mean(data)
    x = get_average_and_standard_deviation_of_time_period_prop_to_mean(data, 252)
    y = get_average_and_standard_deviation_of_time_period_prop_to_mean2(data, 252)
    print(t)
    print(x)
    print(y)
    last_quote = get_last_quote(data)
    f = get_call_price(data, 27.5, 252, last_quote)
    g = get_put_price(data, 27.5, 252, last_quote)
    print(f)
    print(g)
    print(last_quote)
    make_a_histogram_with_stdev_and_mean_change(x[1] * last_quote)