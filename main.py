

import string

from framework.Data.DataSource import DataSource
from framework.Strategy.Strategy import Strategy
from framework.view import View
from framework.Data.impl.BinanceDataSourceImpl import BinanceDataSourceImpl
from framework.Data.impl.FileKeyStore import FileKeyStore

from framework.view.impl.ConsoleViewImpl import ConsoleViewImpl
from framework.Strategy.impl.SpreadMmStrategyImpl import SpreadMmStrategyImpl



def main() -> None:

    #static.chart.start()

    spreadStrategy: Strategy = SpreadMmStrategyImpl(
        BinanceDataSourceImpl(FileKeyStore("./binance_ticker.txt"), ['BTCBUSD','ETHBUSD'], '1m'))

    ConsoleView: View = ConsoleViewImpl()
    #QTview: View = QTviewImpl()

    spreadStrategy.setListener(ConsoleView)
    spreadStrategy.start()

if __name__ == '__main__':
    main()