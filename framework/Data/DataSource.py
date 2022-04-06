from abc import *
import string

class DataSourceListener(metaclass=ABCMeta):
    @abstractmethod
    def onDataReceived(self, dataSource: 'DataSource', price: int):
        pass

    def onConnected(self, dataSource: 'DataSource'):
        pass

    def onDisconnected(self, dataSource: 'DataSource'):
        pass

class DataSource(metaclass=ABCMeta):

    def __init__(self) -> None:
        self.listeners = list()
        pass

    @abstractmethod
    def getName(self) -> string:
        pass

    @abstractmethod
    def buy(self):
        pass

    @abstractmethod
    def sell(self):
        pass

    # @abstractmethod
    # def cancelOrder(self):
    #     pass

    @abstractmethod
    def getCoinPrice(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    # @abstractmethod
    # def disconnect(self):
    #     pass

    # @abstractmethod
    # def isConnect(self):
    #     pass

    # @abstractmethod
    # def getMyAccount(self):
    #     pass

    # @abstractmethod
    # def getMyCoins(self):
    #     pass

    def addListener(self, listener: DataSourceListener):
        self.listeners.append(listener)

    def removeListener(self, listener: DataSourceListener):
        self.listeners.remove(listener)

    def removeAllLiteners(self, listener: DataSourceListener):
        self.listeners.clear()

    def notifyOnDataReceived(self, price: int):
        #print("notifyOnDataReceived():  %s" % self.getName())
        for listener in self.listeners:
            listener.onDataReceived(self, price)

    def notifyOnConnected(self):
        for listener in self.listeners:
            listener.onConnected(self)

    def notifyOnDisconnected(self):
        for listener in self.listeners:
            listener.onDisconnected(self)
