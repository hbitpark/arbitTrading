import os

from framework.view.View import View

class ConsoleViewImpl(View):
    def onDataChanged(self, price: float):
        self.displayPrice(price)
        pass

    def requestBuyDisplay(self, price: float) -> bool:
        self.displayPrice(price)
        print("buy order")
        return True

    def requestSellDisplay(self, price: float) -> bool:
        self.displayPrice(price)
        print("sell order")
        return True

    def requestBuyAnswer(self, price: float) -> bool:
        self.displayPrice(price)
        result = input("Buy? [y/n] ")
        print("")

        return result == "y" or result == "Y"

    def requestSellAnswer(self, price: float) -> bool:
        self.displayPrice(price)
        result = input("Sell? [y/n] ")
        print("")
        return result == "y" or result == "Y"

    def displayPrice(self, symbol, price: float):
        #self.__clearConsole()
        print("")
        print("[View]:--------------------")
        print(f"[View]: Currect price : {price}")
        print("[View]:--------------------")

    def __clearConsole(self):
        command = 'clear'
        if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
            command = 'cls'
        os.system(command)