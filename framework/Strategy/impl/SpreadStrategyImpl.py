from framework.Strategy.Strategy import Strategy
from framework.Data.DataSource import DataSource
import static
import numpy as np
import cufflinks as cf
import pandas as pd

class SpreadStrategyImpl(Strategy):
    def __init__(self, binance: DataSource) -> None:
        super().__init__()

        self.binance: DataSource = binance
        self.addDataSource(binance)

        self.ORDER_STATE = static.ORDER_STATE_NOMAL

    def preCalc(self):
        candleDF0 = self.binance.getCandleDataFrame(static.FIRST_TICKER)
        candleDF1 = self.binance.getCandleDataFrame(static.SECOND_TICKER)
        coin0_close = candleDF0['close']
        coin1_close = candleDF1['close']

        coin0_close[len(coin0_close)] = self.binance.getBidPrice(static.FIRST_TICKER)
        coin1_close[len(coin1_close)] = self.binance.getBidPrice(static.SECOND_TICKER)

        # to log
        logCoin0 = np.log(coin0_close)
        logCoin1 = np.log(coin1_close)

        if static.DRAW_GRAPH:
            self.drawNormalization(coin0_close, coin1_close, candleDF0)
        
        coeffi = self.calcCoefficient(logCoin0, logCoin1)
        spreadDiff = self.calcSpreadDiff(coeffi, logCoin0, logCoin1)

        if static.DRAW_GRAPH:
            self.drawSpreadDiffChart(spreadDiff, candleDF0)
            static.DRAW_GRAPH = False
        return coeffi, spreadDiff

    def calcCoefficient(self, logCoin0, logCoin1):
        # COVAR(coin0로그, coin1로그) / VAR(coin1로그)
        covCoinTwo = logCoin0.cov(logCoin1)
        variance1 = np.var(logCoin1)
        coeffi = covCoinTwo/variance1
        return coeffi

    def calcSpreadDiff(self, coeffi, logCoin0, logCoin1):
        # 로그 스프레드
        logSpread = logCoin0 - coeffi*logCoin1
        
        # 로그 스프레드 평균
        logSpreadAvg = np.average(logSpread)

        # 스프레드 차이
        spreadDiff = ((logSpread - logSpreadAvg)*100)
        return spreadDiff

    def drawNormalization(self, coin0_close, coin1_close):
        averageCoin0 = coin0_close.mean()
        averageCoin1 = coin1_close.mean()

        # 표준편차
        stdCoin0 = np.std(coin0_close)
        stdCoin1 = np.std(coin1_close)

        normalization0 = (coin0_close - averageCoin0)/stdCoin0
        normalization1 = (coin1_close - averageCoin1)/stdCoin1
        self.drawNormalizationChart(normalization0, normalization1)
        return

    def drawNormalizationChart(self, norm0, norm1, candleDF0):
        self.normalDF = pd.DataFrame()
        self.normalDF['coin0'] = norm0
        self.normalDF['coin1'] = norm1
        self.normalDF['datetime'] = self.candleDF0["datetime"]
        for i in range(len(self.normalDF['datetime'])):
            self.normalDF['datetime'][i] = pd.to_datetime(self.normalDF['datetime'][i])#.strftime("%x")
        cf.set_config_file(theme='pearl',sharing='public',offline=True)
        self.normalDF.iplot(kind='spread',x="datetime",xTitle="time"
                            ,yTitle='coin0',title='코인0/코인1정규화 차이')

    def drawSpreadDiffChart(self, spread_diff, candleDF0):
        spreadDiffDF = pd.DataFrame()
        spreadDiffDF['diff'] = spread_diff
        spreadDiffDF['datetime'] = self.candleDF0["datetime"]

        spreadDiffDF.iplot(kind='scatter',x="datetime",xTitle="time"
                            ,yTitle='diff',title='스프레드 변화')
    def calcCoinPercent(self, spread_diff) -> float:
        # spread diff step 당 coinNumPercent
        coinPercent = spread_diff[len(spread_diff)-1]/self.diffStep * self.coinNumPercentStep # 수량 퍼센트로
        step = int(coinPercent/self.coinNumPercentStep)
        calcedCoinPercent = step * self.coinNumPercentStep
        print("---------------------------------------")
        print("spread diff: ",spread_diff[len(spread_diff)-1], " /coinPercent: ",coinPercent, " /오더 퍼센트: ",calcedCoinPercent, " %")
        print("단계 : ",step)
        return calcedCoinPercent
    
    def adaptAI(self, spdDiff):
        self.regression(spdDiff)
        self.knn(spdDiff)

    def calcCoinQuantities(self):
        coeffi, spreadDiff = self.preCalc()

        percent = self.calcCoinPercent(spreadDiff)

        balance_free = ""
        if balance_free != "":
            fBalance_free = round(float(balance_free),1)
            ratio1 = round(float(percent),1)
            orderCount0 = (fBalance_free/float(self.ask[0]))*(ratio1/100)
            orderCount1 = (fBalance_free/float(self.ask[1]))*(ratio1/100)

        orderCount0 = abs(round(orderCount0, static.DIGITS_COIN_NUM0))
        orderCount1 = abs(round(orderCount1 * coeffi, static.DIGITS_COIN_NUM1))

        return orderCount0, orderCount1

    def verifyOrderStateBuy(self):
        #spreadDiffAfterAI = self.adaptAI(spreadDiff)
        
        balance = self.binance.getBalance()
        nowCoinNum0 = self.getCoinNumber(balance, self.coinName[0])
        nowCoinNum1 = self.getCoinNumber(balance, self.coinName[1])

    def shouldBuy(self, tickerNum): # buy 조건
        self.calcCoinQuantities()
        return self.verifyOrderStateBuy()

    def shouldSell(self, tickerNum): # sell 조건
        self.calcCoinQuantities()
        return self.verifyOrderStateSell()

    def orderBuy(self, tickerNum):
        self.binance.buy(tickerNum)

    def orderSell(self, tickerNum):
        self.binance.buy(tickerNum)

    def start(self):
        self.binance.connect()