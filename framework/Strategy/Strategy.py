from abc import *
from framework.Data.DataSource import DataSource, DataSourceListener

class StrategyListener(metaclass=ABCMeta):
    @abstractmethod
    def onDataChanged(self, price: int):
        pass

    @abstractmethod
    def requestBuyAnswer(self, price: int) -> bool:
        pass

    @abstractmethod
    def requestSellAnswer(self, price: int) -> bool:
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

    def onDataReceived(self, dataSource: DataSource, price: int):
        #print("onDataReceived() : Strategy")
        if self.listener == None:
            return

        self.listener.onDataChanged(price)

        if self.shouldBuy():
            if self.listener.requestBuyDisplay(price):
                self.orderBuy()
        elif self.shouldSell():
            if self.listener.requestSellDisplay(price):
                self.orderSell()

    @abstractmethod
    def shouldBuy(self):
        pass

    @abstractmethod
    def shouldSell(self):
        pass

    @abstractmethod
    def orderBuy(self):
        pass

    @abstractmethod
    def orderSell(self):
        pass

    @abstractmethod
    def start(self):
        pass
