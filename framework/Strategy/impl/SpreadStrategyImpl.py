from framework.Strategy.Strategy import Strategy
from framework.Data.DataSource import DataSource
import static

class SpreadStrategyImpl(Strategy):
    def __init__(self, binance: DataSource) -> None:
        super().__init__()

        self.binance: DataSource = binance
        self.addDataSource(binance)

        self.ORDER_STATE = static.ORDER_STATE_NOMAL

    def shouldBuy(self): # buy 조건
        return self.binance.getCoinPrice(static.FIRST_TICKER) > 9999999

    def shouldSell(self): # sell 조건
        return self.binance.getCoinPrice(static.FIRST_TICKER) < -10000

    def orderBuy(self):
        self.binance.buy()

    def orderSell(self):
        self.bithumb.buy()

    def start(self):
        self.binance.connect()