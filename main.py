

import string

from framework.Data.DataSource import DataSource
from framework.Strategy.Strategy import Strategy
from framework.view import View
from framework.Data.impl.BinanceDataSourceImpl import BinanceDataSourceImpl
from framework.Data.impl.FileKeyStore import FileKeyStore

from framework.view.impl.ConsoleViewImpl import ConsoleViewImpl
from framework.Strategy.impl.SpreadStrategyImpl import SpreadStrategyImpl



def main() -> None:
    """프로그램 메인
    """

    #static.chart.start()

    sampleStrategy: Strategy = SpreadStrategyImpl(
        BinanceDataSourceImpl(FileKeyStore("./binance_ticker.txt"), ['BTCBUSD','ETHBUSD'], '1m'))

    ConsoleView: View = ConsoleViewImpl()
    #QTview: View = QTviewImpl()

    sampleStrategy.setListener(ConsoleView)
    sampleStrategy.start()

if __name__ == '__main__':
    main()