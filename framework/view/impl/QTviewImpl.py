from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

form_class = uic.loadUiType("resource/main.ui")[0]

class MyWindow(QMainWindow, form_class):
    global g_api_key
    global g_secret_key
    global g_coinName
    global g_candlePeriod

    def __init__(self, q):
        super().__init__()
        self.setupUi(self)

        self.ratio1 = ""
        self.ratio2 = ""
        self.ratio3 = ""
        self.CoinCount1 = ""
        self.CoinCount2 = ""
        self.CoinCount3 = ""

        self.total_balance = 0
        self.total_balance_free = 0
        self.leverage1 = 1
        self.leverage2 = 1
        self.leverage3 = 1

        self.isLongCoin1_Buyall = True
        self.isLongCoin2_Buyall = False
        self.isLongCoin1_Sellall = False
        self.isLongCoin2_Sellall = True

        self.setWindowTitle("Arbitrader3 v0.1")

        self.pushBtn_Start.clicked.connect(self.start_trade)
        self.pushBtn_test.clicked.connect(self.testBun)
        self.pushBtn_DrawChart.clicked.connect(self.DrawChartOnce)
        self.pushBtn_SavaHistoryCandle.clicked.connect(self.saveHistorycalCandleAll)
        self.btnBuyALL.clicked.connect(self.buy_All)
        self.btnBuyCoin1.clicked.connect(self.buy_Coin1)
        self.btnBuyCoin2.clicked.connect(self.buy_Coin2)

        self.btnSellALL.clicked.connect(self.sell_All)
        self.btnSellCoin1.clicked.connect(self.sell_Coin1)
        self.btnSellCoin2.clicked.connect(self.sell_Coin2)

        self.btnCancle1.clicked.connect(self.cancle1)
        self.btnCancle2.clicked.connect(self.cancle2)

        self.radio_market1.clicked.connect(self.setRadioMarket1)
        self.radio_limit1.clicked.connect(self.setRadioLimit1)
        self.radio_market2.clicked.connect(self.setRadioMarket2)
        self.radio_limit2.clicked.connect(self.setRadioLimit2)

        if not self.radio_limit1.isChecked():
            self.radio_limit1.setChecked(True)

        if self.radio_market2.isChecked():
            self.radio_market2.toggle()
            self.radio_limit2.setChecked(True)

        self.edit1stRatio.textChanged[str].connect(self.onRatio1_Changed)
        self.edit2ndRatio.textChanged[str].connect(self.onRatio2_Changed)
        self.edit1stCount.textChanged[str].connect(self.onCoinCount1_Changed)
        self.edit2ndCount.textChanged[str].connect(self.onCoinCount2_Changed)

        self.radio_coin1Long_BuyAll.clicked.connect(self.onRadio_Changed_Coin1BuyAll_long)
        self.radio_coin1Short_BuyAll.clicked.connect(self.onRadio_Changed_Coin1BuyAll_short)
        self.radio_coin2Long_BuyAll.clicked.connect(self.onRadio_Changed_Coin2BuyAll_long)
        self.radio_coin2Short_BuyAll.clicked.connect(self.onRadio_Changed_Coin2BuyAll_short)

        self.radio_coin1Long_SellAll.clicked.connect(self.onRadio_Changed_Coin1SellAll_long)
        self.radio_coin1Short_SellAll.clicked.connect(self.onRadio_Changed_Coin1SellAll_short)
        self.radio_coin2Long_SellAll.clicked.connect(self.onRadio_Changed_Coin2SellAll_long)
        self.radio_coin2Short_SellAll.clicked.connect(self.onRadio_Changed_Coin2SellAll_short)

        self.settings = QSettings('devTream3', 'ArbiTest3')
        if self.settings.value(BINANCE_SECRET_KEY) is not None:
            self.Edit_sec_key.setText(self.settings.value(BINANCE_SECRET_KEY))
        if self.settings.value('leverage_1') is not None:
            self.lineEdit_leverage1.setText(str(self.settings.value('leverage_1')))
        if self.settings.value('leverage_2') is not None:
            self.lineEdit_leverage2.setText(str(self.settings.value('leverage_2')))
        
        self.editCoinName1.setText(self.coinName[0])
        self.editCoinName2.setText(self.coinName[1])

        self.create_table_widget()

        self.Edit_api_key.setText(api_key)

        self.client_binance = self.__createClient(api_key, secret_key)

        self.getBalanceAll()
        self.getLeverage()

    def create_table_widget(self):
        #self.table = QTableWidget()
        columns = ["코인", "ask price", "ask size", "bid price", "bid size"]
        self.tableWidgetPrice.verticalHeader().setVisible(False)
        self.tableWidgetPrice.setColumnCount(len(columns))
        self.tableWidgetPrice.setRowCount(3)
        self.tableWidgetPrice.setHorizontalHeaderLabels(columns)

     # 코인비율 EditBox
    def onRatio1_Changed(self, text):
        self.setCount1()
    
    def onRatio2_Changed(self, text):
        self.setCount2()

    # 코인개수 EditBox
    def onCoinCount1_Changed(self, text):
        self.setRatio1()
        
        self.label_coinCount1.setText(self.edit1stCount.text())
    
    def onCoinCount2_Changed(self, text):
        self.setRatio2()

        self.label_coinCount2.setText(self.edit2ndCount.text())

    # 코인 Long/Short 지정 체크박스
    def onRadio_Changed_Coin1BuyAll_long(self): # buy all button
        self.isLongCoin1_Buyall = True
        self.radio_coin1Short_BuyAll.setChecked(False)
        if not self.radio_coin1Long_BuyAll.isChecked():
            self.radio_coin1Long_BuyAll.setChecked(True)

    def onRadio_Changed_Coin1BuyAll_short(self):
        self.isLongCoin1_Buyall = False
        self.radio_coin1Long_BuyAll.setChecked(False)
        if not self.radio_coin1Short_BuyAll.isChecked():
            self.radio_coin1Short_BuyAll.setChecked(True)

    def onRadio_Changed_Coin2BuyAll_long(self):
        self.isLongCoin2_Buyall = True
        self.radio_coin2Short_BuyAll.setChecked(False)
        if not self.radio_coin2Long_BuyAll.isChecked():
            self.radio_coin2Long_BuyAll.setChecked(True)
        
    def onRadio_Changed_Coin2BuyAll_short(self):
        self.isLongCoin2_Buyall = False
        self.radio_coin2Long_BuyAll.setChecked(False)
        if not self.radio_coin2Short_BuyAll.isChecked():
            self.radio_coin2Short_BuyAll.setChecked(True)

    def onRadio_Changed_Coin1SellAll_long(self): # sell all button
        self.isLongCoin1_Sellall = True
        self.radio_coin1Short_SellAll.setChecked(False)
        if not self.radio_coin1Long_SellAll.isChecked():
            self.radio_coin1Long_SellAll.setChecked(True)

    def onRadio_Changed_Coin1SellAll_short(self):
        self.isLongCoin1_Sellall = False
        self.radio_coin1Long_SellAll.setChecked(False)
        if not self.radio_coin1Short_SellAll.isChecked():
            self.radio_coin1Short_SellAll.setChecked(True)

    def onRadio_Changed_Coin2SellAll_long(self):
        self.isLongCoin2_Sellall = True
        self.radio_coin2Short_SellAll.setChecked(False)
        if not self.radio_coin2Long_SellAll.isChecked():
            self.radio_coin2Long_SellAll.setChecked(True)

    def onRadio_Changed_Coin2SellAll_short(self):
        self.isLongCoin2_Sellall = False
        self.radio_coin2Long_SellAll.setChecked(False)
        if not self.radio_coin2Short_SellAll.isChecked():
            self.radio_coin2Short_SellAll.setChecked(True)
            
    # edit box 변경
    def setRatio1(self): # count1 바뀔때 호출
        try:
            self.CoinCount1 = self.edit1stCount.text()
            self.CoinCount1 = round(float(self.CoinCount1),1)

            nowPercent = (self.CoinCount1*float(self.ask[0])/self.total_balance_free)*100
            nowPercent = round(nowPercent,1)
            self.edit1stRatio.setText(str(nowPercent))
        except Exception as e:
            pass

    def setRatio2(self):
        try:
            self.CoinCount2 = self.edit2ndCount.text()
            self.CoinCount2 = round(float(self.CoinCount2),1)

            nowPercent = (self.CoinCount2*float(self.ask[1])/self.total_balance_free)*100
            nowPercent = round(nowPercent,1)
            
            self.edit2ndRatio.setText(str(nowPercent))
        except Exception as e:
            pass
            
    def setCount1(self): # ratio1 바뀔때 호출
        self.ratio1 = self.edit1stRatio.text()
        if self.ratio1 != "":
            try:
                self.ratio1 = round(float(self.ratio1),1)

                nowCount = (self.total_balance_free/float(self.ask[0]))*(self.ratio1/100)
                nowCount = round(nowCount,1)

                self.label_coinCount1.setText(str(nowCount))
            except Exception:
                pass

    def setCount2(self): # ratio2 바뀔때 호출
        self.ratio2 = self.edit2ndRatio.text()
        if self.ratio2 != "":
            try:
                self.ratio2 = round(float(self.ratio2),1)

                nowCount2 = (self.total_balance_free/float(self.ask[1]))*(self.ratio2/100)
                nowCount2 = round(nowCount2,1)
                self.label_coinCount2.setText(str(nowCount2))
            except Exception:
                pass

    # 지정가 / 시장가 라디오버튼
    def setRadioMarket1(self):
        print("setRadioMarket1")
    def setRadioLimit1(self):
        print("setRadioLimit1")
    def setRadioMarket2(self):
        print("setRadioMarket2")
        self.radio_limit2.toggle()
    def setRadioLimit2(self):
        print("setRadioLimit2")
        self.radio_market2.toggle()

    def testBun(self):
        #limitBuyResult0 = self.ccxt_binance.create_limit_buy_order(self.coinName[0], round(2,self.CoinCount_cipher0), self.ask[0])
        #print("Buy : coin 0 - limitBuyResult0: ",limitBuyResult0)
        MarketBuyResult0 = self.ccxt_binance.create_market_buy_order(self.coinName[0], round(2,self.CoinCount_cipher0))
        if MarketBuyResult0['info']['status']=='FILLED':
            print("filled")

    def saveUserPram(self):
        # get key info
        api_key = "KAF8yqrcCe0LFprfftp0gg0DwIimAPGzemOwk7BGEiZMR5esOOEWhu5wxGRO8YmG" 
        secret_key = str(self.Edit_sec_key.text())

        self.settings = QSettings('devTream', 'ArbiTest3')
        self.settings.setValue('binance_api_key', api_key)
        self.settings.setValue('binance_secret_key', secret_key)
        self.settings.setValue('leverage_1', self.leverage1)
        self.settings.setValue('leverage_2', self.leverage2)
        self.settings.sync()

    def start_trade(self):
        self.leverage1 = int(self.lineEdit_leverage1.text())
        self.leverage2 = int(self.lineEdit_leverage2.text())

        leverageResult1 = self.client_binance.futures_change_leverage(symbol=self.coinName[0], leverage=self.leverage1)
        leverageResult2 = self.client_binance.futures_change_leverage(symbol=self.coinName[1], leverage=self.leverage2)
        if self.leverage1==int(leverageResult1['leverage']):
            print(self.coinName[0] + "-> 레버리지 변경 성공. ",self.leverage1,"배")
        if self.leverage2==int(leverageResult2['leverage']):
            print(self.coinName[1] + "-> 레버리지 변경 성공. ",self.leverage2,"배")
        
        self.saveUserPram()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()