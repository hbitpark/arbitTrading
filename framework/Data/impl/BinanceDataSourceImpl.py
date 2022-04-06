
import asyncio
import multiprocessing as mp
import string
from http import client

from binance import AsyncClient, BinanceSocketManager
from binance.client import Client
from framework.Data.DataSource import DataSource
from datetime import datetime
import pandas as pd
from util.scrapeData import scrape_candles_to_csv, scrape_candles_to_return
import static
import ccxt

class BinanceDataSourceImpl(DataSource):
    def __init__(self, FileKeyStore, tickerList, candlePeriod) -> None:
        super().__init__()
        self.queue = mp.Queue()
        self.filekeystore = FileKeyStore
        self.client = self.__createClient()
        self.clientCcxt = self.__createClientCcxt('future')

        self.coinName = tickerList
        self.candlePeriod = candlePeriod
        self.ask = [0, 0, 0]
        self.bid = [0, 0, 0]
        self.ask_volume = [0, 0, 0]
        self.bid_volume = [0, 0, 0]
        self.tickerMaxNum = len(self.coinName)

        print("ticker num: ", self.tickerMaxNum)
        for i in range(self.tickerMaxNum):
            print("ticker ",i,"번 : ",self.coinName[i])
            self.ask.append('')
            self.bid.append('')
        
        self.g_CandleDF = self.makeHistoryCandleDataFrame(False, static.MAX_COIN_DATA)

    def __createClient(self) -> Client:
        return Client(api_key=self.filekeystore.getAPIKey(), api_secret=self.filekeystore.getAPISecretKey())

    def __createClientCcxt(self, clientType):
        ccxt_binance = ccxt.binance(config={
            'apiKey': self.filekeystore.getAPIKey(), 
            'secret': self.filekeystore.getAPISecretKey(),
            'enableRateLimit': True,
            'options': {
                'defaultType': clientType
            }
        })
        return ccxt_binance

    def makeHistoryCandleDataFrame(self, getHistoryLarge, historyNumber):
        candleDf = []
        coin_ohlcv = []

        if getHistoryLarge:
            ohlcv = scrape_candles_to_return('binance', 10000, 'BTC/BUSD', self.candlePeriod, '2022-02-2400:00:00Z', 1000)
            coin_ohlcv.append(ohlcv)
            candleDf.append(pd.DataFrame(coin_ohlcv[0], columns=['datetime', 'open', 'high', 'low', 'close', 'volume']))
            
            ohlcv = scrape_candles_to_return('binance', 10000, 'ETH/BUSD', self.candlePeriod, '2022-02-2400:00:00Z', 1000)
            coin_ohlcv.append(ohlcv)
            candleDf.append(pd.DataFrame(coin_ohlcv[1], columns=['datetime', 'open', 'high', 'low', 'close', 'volume']))
        else:
            for i in range(self.tickerMaxNum):
                coin_ohlcv.append(self.clientCcxt.fetch_ohlcv(symbol=self.coinName[i], timeframe=self.candlePeriod, 
                                                            since=None, limit=historyNumber))
                candleDf.append(pd.DataFrame(coin_ohlcv[i], columns=['datetime', 'open', 'high', 'low', 'close', 'volume']))
        return candleDf

    def getName(self) -> string:
        return "Binance"
    
    def buy(self):
        print("buy() : %s" % self.getName())

    def sell(self):
        print("sell() : %s" % self.getName())

    def getCandleDataFrame(self, tickerNum):
        return self.g_CandleDF[tickerNum]

    def getCoinPrice(self, tickerNum): # ask
        strPrice = self.ask[tickerNum]
        if strPrice == '':
            return 0
        else:
            return float(strPrice)
        
    def getAskPrice(self, tickerNum): # ask
        strPrice = self.ask[tickerNum]
        if strPrice == '':
            return 0
        else:
            return float(strPrice)

    def getBidPrice(self, tickerNum): # bid
        strPrice = self.bid[tickerNum]
        if strPrice == '':
            return 0
        else:
            return float(strPrice)

    def getOrderbook(self, tickerNum):
        orderbook = self.client.futures_order_book(symbol=self.coinName[tickerNum])
        #print(orderbook.keys())
        return orderbook

    def getHistoryKlines(self, ticker, interval='1m'):
        klines = self.client.futures_historical_klines(symbol=ticker,interval=interval,
            start_str="1 day ago UTC+9") #start_str='2022-02-13'
        print("time:  ",  datetime.utcfromtimestamp((int((klines[0]) / 1000))))
        print("klines: ",klines)
        #Date.append(datetime.utcfromtimestamp((int((klines[0]) / 1000))))
        #Open.append(float(kline[1]))
        #Close.append(float(kline[4]))
        #High.append(float(kline[2]))
        #Low.append(float(kline[3]))
        #Volume.append(float(kline[7]))

    def addCloseCandle(self, data, candleIndex):
            closeCandle = [data['data']['k']['o'], data['data']['k']['h'], data['data']['k']['l'], data['data']['k']['c'], data['data']['k']['v']]
            nowTime = pd.to_datetime(data['data']['E'], unit='ms')
            self.g_CandleDF[candleIndex].loc[nowTime] = closeCandle # insert OHLC
            self.g_CandleDF[candleIndex].drop(self.g_CandleDF[candleIndex].head(1).index,inplace=True) # drop old candle

    def connect(self):      
        process = mp.Process(name="Binance", target=self.connectBinance, args=(), daemon=True)        
        process.start()
        
        while True:
            data = self.queue.get()

            if 'bookTicker' in data['stream']:
                for i in range(self.tickerMaxNum):
                    if self.coinName[i] in data['data']['s']:
                        self.bid[i] = data['data']['b']
                        self.ask[i] = data['data']['a']

                        self.notifyOnDataReceived(self.bid[i])
            elif 'continuousKline' in data['stream']:
                if data['data']['k']['x']:
                    for i in range(self.tickerMaxNum):
                        if data['data']['ps'] == self.coinName[i]:
                            self.addCloseCandle(data, i)
                            #self.notifyOnDataReceived(data)

    
    def connectBinance(self):
        asyncio.run(self.createBinanceWebsockekClient())
    
    async def createBinanceWebsockekClient(self):
        tickerStreamStr = []
        for i in self.coinName:
            tickerStreamStr.append(i.lower() + '@bookTicker')
            tickerStreamStr.append(i.lower() + '_perpetual@continuousKline_' + self.candlePeriod)

        asycClient = await AsyncClient.create(self.filekeystore.getAPIKey(), self.filekeystore.getAPISecretKey())
        binanceSocketManager = BinanceSocketManager(asycClient)
        ts = binanceSocketManager.futures_multiplex_socket(tickerStreamStr)
        async with ts as tscm:
            while True:
                response = await tscm.recv()
                #await asyncio.sleep(0.5)
                self.queue.put(response)
