from abc import *
from framework.Data.DataSource import DataSource, DataSourceListener

class StrategyListener(metaclass=ABCMeta):
    @abstractmethod
    def onDataChanged(self, tickerNum, price: int):
        pass

    @abstractmethod
    def requestBuyAnswer(self, tickerNum, price: int) -> bool:
        pass

    @abstractmethod
    def requestSellAnswer(self, tickerNum, price: int) -> bool:
        pass

class Strategy(DataSourceListener):
    def __init__(self) -> None:
        super().__init__()
        self.listener = None
        self.dataSources = list()
    
    def setListener(self, listener: StrategyListener):
        self.listener = listener

    def addDataSource(self, dataSource: DataSource):
        self.dataSources.append(dataSource)
        dataSource.addListener(self)
    
    def removeDataSource(self, dataSource: DataSource):
        self.dataSources.remove(dataSource)
        dataSource.removeListener(self)
    
    def removeAllDataSources(self):
        for dataSource in self.dataSources:
            self.removeDataSource(dataSource)

    def onDataReceived(self, tickerNum, price: int):
        #print("onDataReceived() : Strategy")
        if self.listener == None:
            return

        self.listener.onDataChanged(tickerNum, price)

        if self.shouldBuy(tickerNum):
            if self.listener.requestBuyDisplay(tickerNum, price):
                self.orderBuy(tickerNum)
        #elif self.shouldSell(tickerNum):
        #    if self.listener.requestSellDisplay(tickerNum, price):
        #        self.orderSell(tickerNum)

    @abstractmethod
    def preCalc(self):
        pass

    @abstractmethod
    def shouldBuy(self, tickerNum):
        pass

    @abstractmethod
    def shouldBuy(self, tickerNum):
        pass

    @abstractmethod
    def shouldSell(self, tickerNum):
        pass

    @abstractmethod
    def orderBuy(self, tickerNum):
        pass

    @abstractmethod
    def orderSell(self, tickerNum):
        pass

    @abstractmethod
    def start(self):
        pass
