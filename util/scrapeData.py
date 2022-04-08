import os
from pathlib import Path

import sys
import csv

# -----------------------------------------------------------------------------

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(''))))
sys.path.append(root + '/python')

import ccxt


# -----------------------------------------------------------------------------

def retry_fetch_ohlcv(exchange, max_retries, symbol, timeframe, since, limit):
    num_retries = 0
    try:
        num_retries += 1
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        # print('Fetched', len(ohlcv), symbol, 'candles from', exchange.iso8601 (ohlcv[0][0]), 'to', exchange.iso8601 (ohlcv[-1][0]))
        return ohlcv
    except Exception:
        if num_retries > max_retries:
            raise  # Exception('Failed to fetch', timeframe, symbol, 'OHLCV in', max_retries, 'attempts')


def scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit):
    earliest_timestamp = exchange.milliseconds()
    timeframe_duration_in_seconds = exchange.parse_timeframe(timeframe)
    timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
    timedelta = limit * timeframe_duration_in_ms
    all_ohlcv = []
    while True:
        fetch_since = earliest_timestamp - timedelta
        ohlcv = retry_fetch_ohlcv(exchange, max_retries, symbol, timeframe, fetch_since, limit)
        # if we have reached the beginning of history
        if ohlcv[0][0] >= earliest_timestamp:
            break
        earliest_timestamp = ohlcv[0][0]
        all_ohlcv = ohlcv + all_ohlcv
        print(len(all_ohlcv), symbol, 'candles in total from', exchange.iso8601(all_ohlcv[0][0]), 'to', exchange.iso8601(all_ohlcv[-1][0]))
        # if we have reached the checkpoint
        if fetch_since < since:
            break
    return all_ohlcv


def write_to_csv(filename, exchange, data):
    p = Path("./data/raw/", str(exchange))
    p.mkdir(parents=True, exist_ok=True)
    full_path = p / str(filename)
    with Path(full_path).open('w+', newline='') as output_file:
        csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerows(data)


def scrape_candles_to_csv(filename, exchange_id, max_retries, symbol, timeframe, since, limit):
    # instantiate the exchange by id
    exchange = getattr(ccxt, exchange_id)({
        'enableRateLimit': True,  # required by the Manual
    })
    # convert since from string to milliseconds integer if needed
    if isinstance(since, str):
        since = exchange.parse8601(since)
    # preload all markets from the exchange
    exchange.load_markets()
    # fetch all candles
    ohlcv = scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)
    # save them to csv file
    write_to_csv(filename, exchange, ohlcv)
    print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]), 'to', filename)

def scrape_candles_to_return(exchange_id, max_retries, symbol, timeframe, since, limit):
    # instantiate the exchange by id
    exchange = getattr(ccxt, exchange_id)({
        'enableRateLimit': True,  # required by the Manual
    })
    # convert since from string to milliseconds integer if needed
    if isinstance(since, str):
        since = exchange.parse8601(since)
    # preload all markets from the exchange
    exchange.load_markets()
    # fetch all candles
    ohlcv = scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)
    # save them to csv file
    print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]))
    return ohlcv

def calcSpreadCandle(g_CandleDF):
    logCoin0 = np.log(g_CandleDF[0]['close'])
    logCoin1 = np.log(g_CandleDF[1]['close'])
    covCoinTwo = logCoin0.cov(logCoin1)
    variance1 = np.var(logCoin1)
    coeffi = covCoinTwo/variance1

    return calcSpread(g_CandleDF[0], g_CandleDF[1], coeffi)

def calcSpread(coin0, coin1, coEffi):
    logCoin0 = np.log(coin0)
    logCoin1 = np.log(coin1)
    logSpread = (logCoin0/(coEffi*logCoin1))
    logSpreadAvg = np.average(logSpread)
    return (logSpread - logSpreadAvg)*100

def scrape_SpreadCandlesTwoSymbol_to_csv(filename, exchange_id, max_retries, symbol0, symbol1, timeframe, since, limit):
    # instantiate the exchange by id
    exchange = getattr(ccxt, exchange_id)({
        'enableRateLimit': True,  # required by the Manual
    })
    # convert since from string to milliseconds integer if needed
    if isinstance(since, str):
        since = exchange.parse8601(since)
    # preload all markets from the exchange
    exchange.load_markets()
    # fetch all candles
    ohlcv0 = scrape_ohlcv(exchange, max_retries, symbol0, timeframe, since, limit)
    ohlcv1 = scrape_ohlcv(exchange, max_retries, symbol1, timeframe, since, limit)

    g_CandleDF = []
    g_CandleDF.append(pd.DataFrame(ohlcv0, columns=['datetime', 'open', 'high', 'low', 'close', 'volume']))
    g_CandleDF.append(pd.DataFrame(ohlcv1, columns=['datetime', 'open', 'high', 'low', 'close', 'volume']))
    ohlcv = calcSpreadCandle(g_CandleDF)
    ohlcv['datetime'] = g_CandleDF[0]['datetime']
    ohlcv['volume'] = g_CandleDF[0]['volume']
    ohlcv_list = ohlcv.values

    # save them to csv file
    write_to_csv(filename, exchange, ohlcv_list)
    print('Saved', len(ohlcv_list), 'candles from', exchange.iso8601(ohlcv_list[0][0]), 'to', exchange.iso8601(ohlcv_list[-1][0]), 'to', filename)