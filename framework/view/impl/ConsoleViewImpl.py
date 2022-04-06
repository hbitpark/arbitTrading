import os

from framework.view.View import View

class ConsoleViewImpl(View):
    def onDataChanged(self, tickerNum, price: float):
        self.displayPrice(tickerNum, price)
        pass

    def requestBuyDisplay(self, tickerNum, price: float) -> bool:
        #self.displayPrice(tickerNum, price)
        print("buy order")
        return True

    def requestSellDisplay(self, tickerNum, price: float) -> bool:
        #self.displayPrice(tickerNum, price)
        print("sell order")
        return True

    def requestBuyAnswer(self, tickerNum, price: float) -> bool:
        self.displayPrice(tickerNum, price)
        result = input("Buy? [y/n] ")
        print("")

        return result == "y" or result == "Y"

    def requestSellAnswer(self, tickerNum, price: float) -> bool:
        self.displayPrice(tickerNum, price)
        result = input("Sell? [y/n] ")
        print("")
        return result == "y" or result == "Y"

    def displayPrice(self, tickerNum, price: float):
        #self.__clearConsole()
        print("")
        print("[View]:-------------------tk: ",tickerNum)
        print(f"[View]: Currect price : {price}")
        print("[View]:--------------------")

    def __clearConsole(self):
        command = 'clear'
        if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
            command = 'cls'
        os.system(command)