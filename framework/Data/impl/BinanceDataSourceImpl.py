
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

class OrderInfo():
    def __init__(self, tickerName, tickerNum, ccxtClient):
        self.tickerName = tickerName
        self.tickerNum = tickerNum
        self.pendingOrder =  []
        self.openOrder  = []
        self.openOrderBuy  = []
        self.openOrderSell  = []

        self.initPendingOrder(ccxtClient)
        self.initOpenOrder(ccxtClient)
    
    def initPendingOrder(self, ccxtclient):
        orderStream = ccxtclient.fetch_open_orders(symbol=self.tickerName)
        self.pendingOrder  = pd.DataFrame(columns=['datetime', 'side', 'symbol', 'id', 'status', 'origin_qty','exec_qty', 'price'])

        for i in range(len(orderStream)):
            orderData = orderStream[i]
            orderinfo = [orderData['info']['time'], orderData['side'], orderData['info']['symbol'], orderData['info']['orderId'], 
                         orderData['info']['status'], orderData['info']['origQty'], orderData['info']['executedQty'], orderData['info']['price']]
            #self.pendingOrder.append(pd.DataFrame(orderinfo))
            if orderData['info']['status']=='OPEN':
                
                self.openOrder = self.pendingOrder.append(pd.DataFrame([orderinfo], 
                    columns=['datetime', 'side', 'symbol', 'id', 'status', 'origin_qty','exec_qty', 'price']), ignore_index=True)    
            elif orderData['info']['status']=='NEW':
                self.pendingOrder = self.pendingOrder.append(pd.DataFrame([orderinfo], 
                    columns=['datetime', 'side', 'symbol', 'id', 'status', 'origin_qty','exec_qty', 'price']), ignore_index=True)

    def initOpenOrder(self, ccxtclient):
        balance = ccxtclient.fetch_balance()
        orderStream = balance['info']['positions']
        for position in orderStream:
            if position["symbol"] == self.tickerName:
                print("open oder: ")
                print(position)

        self.openOrder  = pd.DataFrame(columns=['datetime', 'side', 'symbol', 'id', 'status', 'origin_qty','exec_qty', 'price'])
        self.openOrderBuy  = pd.DataFrame(columns=['datetime', 'side', 'symbol', 'id', 'status', 'origin_qty','exec_qty', 'price'])
        self.openOrderSell = pd.DataFrame(columns=['datetime', 'side', 'symbol', 'id', 'status', 'origin_qty','exec_qty', 'price'])
        """
        for i in range(len(orderStream)):
            orderData = orderStream[i]
            orderinfo = [orderData['info']['time'], orderData['side'], orderData['info']['symbol'], orderData['info']['orderId'], 
                         orderData['info']['status'], orderData['info']['origQty'], orderData['info']['executedQty'], orderData['info']['price']]
            #self.pendingOrder.append(pd.DataFrame(orderinfo))
            if orderData['info']['status']=='OPEN':
                self.openOrder = self.pendingOrder.append(pd.DataFrame([orderinfo], 
                    columns=['datetime', 'side', 'symbol', 'id', 'status', 'origin_qty','exec_qty', 'price']), ignore_index=True)    
        """

    def addNewPendingOrder(self, orderData):
        orderinfo = [orderData['T'], orderData['o']['S'], orderData['o']['s'], orderData['o']['i'], 
                         orderData['o']['X'], orderData['o']['q'], orderData['o']['z'], orderData['o']['p']]

        self.pendingOrder = self.pendingOrder.append(pd.DataFrame([orderinfo], 
            columns=['datetime', 'side', 'symbol', 'id', 'status', 'origin_qty','exec_qty', 'price']), ignore_index=True)

    def delCanclePendigOrder(self, orderData):
        for i in range(len(self.pendingOrder)):
            if orderData['o']['i']==int(self.pendingOrder.iloc[i]['id']):
                    self.pendingOrder.drop(i, inplace=True) # del self.pendingOrder row
                    self.pendingOrder.reset_index(drop=True,inplace=True)
                    return

    def delPendigOrder(self, orderData):
        for i in range(len(self.pendingOrder)):
            if orderData['o']['i']==int(self.pendingOrder.iloc[i]['id']):
                if orderData['o']['z']==self.pendingOrder.iloc[i]['origin_qty']:
                    self.pendingOrder.drop(i, inplace=True) # del self.pendingOrder row
                    self.pendingOrder.reset_index(drop=True,inplace=True)
                    return

    def displayPendingOrder(self):
        if len(self.pendingOrder) > 0:
            print("pending orders: \n",self.pendingOrder)
            print("--------------------------------------")
            #print("pending orders0: \n",self.pendingOrder.iloc[0:2])

    def displayOpenOrder(self):
        if len(self.openOrder) > 0:
            print("open orders : \n",self.openOrder)
            print("--------------------------------------")
            #print("pending orders0: \n",self.pendingOrder.iloc[0:2])

    def addNewOpenOrder(self, orderData):
        orderinfo = [orderData['T'], orderData['o']['S'], orderData['o']['s'], orderData['o']['i'], 
                         orderData['o']['X'], orderData['o']['q'], orderData['o']['z'], orderData['o']['p']]

        self.pendingOrder = self.pendingOrder.append(pd.DataFrame([orderinfo], 
            columns=['datetime', 'side', 'symbol', 'id', 'status', 'origin_qty','exec_qty', 'price']), ignore_index=True)
import atexit

@atexit.register
def goodbye():
    print('You are now leaving the Python sector.')

class BinanceDataSourceImpl(DataSource):
    def __init__(self, FileKeyStore, tickerList, candlePeriod) -> None:
        super().__init__()
        self.queue = mp.Queue()
        self.queueUser = mp.Queue()

        self.filekeystore = FileKeyStore
        self.client = self.__createClient()
        self.clientCcxt = self.__createClientCcxt('future')
        self.coinName = tickerList

        self.pendingOrders = OrderInfo(self.coinName[0], 0, self.clientCcxt)
        self.pendingOrders.displayPendingOrder()
        self.pendingOrders.displayOpenOrder()

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
        #print("df: ",self.g_CandleDF)

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
    
    def buy(self, quantities):
        limitBuyResult0 = self.clientCcxt.create_limit_buy_order(self.coinName[0], quantities, self.bid[0])
        print("Buy : coin 0 - limitBuyResult0: ",limitBuyResult0)
        #print("buy() : %s" % self.getName())

    def sell(self, quantities):
        limitSellResult1 = self.clientCcxt.create_limit_sell_order(self.coinName[1], quantities, self.ask[1])
        print("Buy : coin 1 - limitSellResult1: ",limitSellResult1)
        #print("sell() : %s" % self.getName())

    def getBalance(self):
        return self.clientCcxt.fetch_balance()
        
    def getTickerName(self, tickerNum):
        return self.coinName[tickerNum]

    def getCandleDataFrame(self, tickerNum):
        return self.g_CandleDF[tickerNum]

    def getCoinPrice(self, tickerNum): # ask
        strPrice = self.bid[tickerNum]
        strPrice = float(strPrice)
        if strPrice <= 0:
            strPrice = self.clientCcxt.fetch_ticker(self.coinName[tickerNum])
            self.bid[tickerNum] = float(strPrice['close'])
            return self.bid[tickerNum]
        else:
            return strPrice
        
    def getAskPrice(self, tickerNum): # ask
        strPrice = self.ask[tickerNum]
        strPrice = float(strPrice)
        if strPrice <= 0:
            strPrice = self.clientCcxt.fetch_ticker(self.coinName[tickerNum])
            return float(strPrice['close'])
        else:
            return strPrice

    def getBidPrice(self, tickerNum): # bid
        strPrice = self.bid[tickerNum]
        strPrice = float(strPrice)
        if strPrice <= 0:
            strPrice = self.clientCcxt.fetch_ticker(self.coinName[tickerNum])
            self.bid[tickerNum] = float(strPrice['close'])
            return self.bid[tickerNum]
        else:
            return strPrice

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
            nowTime = pd.to_datetime(data['data']['E'], unit='ms')
            closeCandle = [nowTime, data['data']['k']['o'], data['data']['k']['h'], data['data']['k']['l'], data['data']['k']['c'], data['data']['k']['v']]
            self.g_CandleDF[candleIndex].loc[len(self.g_CandleDF[candleIndex]['open'])] = closeCandle
            self.g_CandleDF[candleIndex].drop(self.g_CandleDF[candleIndex].head(1).index,inplace=True) # drop old candle
            self.g_CandleDF[candleIndex].reset_index(drop=True,inplace=True)

    def connect(self):      
        process = mp.Process(name="Binance", target=self.connectBinance, args=(), daemon=True)        
        process.start()
        
        while True:
            if not self.queue.empty():
                data = self.queue.get()
                if data:
                    if 'bookTicker' in data['stream']:
                        for i in range(self.tickerMaxNum):
                            if self.coinName[i] in data['data']['s']:
                                self.bid[i] = data['data']['b']
                                self.ask[i] = data['data']['a']

                                self.notifyOnDataReceived(i, self.bid[i])
                    elif 'continuousKline' in data['stream']:
                        if data['data']['k']['x']:
                            for i in range(self.tickerMaxNum):
                                if data['data']['ps'] == self.coinName[i]:
                                    self.addCloseCandle(data, i)
                                    #self.notifyOnDataReceived(data)
            if not self.queueUser.empty():
                dataUser = self.queueUser.get()
                if dataUser:
                    if 'ORDER_TRADE_UPDATE' in dataUser['e']:
                        print("-: ",dataUser)
                        print("--------------------------------------")
                        if dataUser['o']['X']=='NEW':
                            self.pendingOrders.addNewPendingOrder(dataUser)
                            self.pendingOrders.displayPendingOrder()
                        elif dataUser['o']['X']=='CANCELED':
                            self.pendingOrders.delCanclePendigOrder(dataUser)
                            self.pendingOrders.displayPendingOrder()
                        elif dataUser['o']['X']=='FILLED':
                            self.pendingOrders.delPendigOrder(dataUser)
                            self.pendingOrders.displayPendingOrder()

    def connectBinance(self):
        myLoop = asyncio.get_event_loop()
        myLoop.run_until_complete(asyncio.gather(
            *[self.connctWebsocketFutureMuliplex(), self.connctWebsocketFutureUser()]
            ))
        myLoop.close()

    async def connctWebsocketFutureMuliplex(self):
        tickerStreamStr = []
        for i in self.coinName:
            tickerStreamStr.append(i.lower() + '@bookTicker')
            #tickerStreamStr.append(i.lower() + '_perpetual@continuousKline_' + self.candlePeriod)

        asycClient = await AsyncClient.create(self.filekeystore.getAPIKey(), self.filekeystore.getAPISecretKey())
        binanceSocketManager = BinanceSocketManager(asycClient)

        ts = binanceSocketManager.futures_multiplex_socket(tickerStreamStr)

        async with ts as tscm:
            while True:
                response = await tscm.recv()
                #await asyncio.sleep(0.5)
                self.queue.put(response)

    async def connctWebsocketFutureUser(self):
        asycClient = await AsyncClient.create(self.filekeystore.getAPIKey(), self.filekeystore.getAPISecretKey())
        binanceSocketManager = BinanceSocketManager(asycClient)

        ts = binanceSocketManager.futures_user_socket()

        async with ts as tscm:
            print('Connected to user socket')
            while True:
                response = await tscm.recv()
                self.queueUser.put(response)