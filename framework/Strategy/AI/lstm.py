
import pandas as pd
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler


import yfinance as yf
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense

import pytz
import time
import datetime as dt
#!pip install yahoo_fin
#from yahoo_fin import stock_info as si
from yahoo_fin.stock_info import get_live_price

# split a univariate sequence into samples
def split_sequence(sequence, n_steps):
	X, y = list(), list()
	for i in range(len(sequence)):
		# find the end of this pattern
		end_ix = i + n_steps
		# check if we are beyond the sequence
		if end_ix > len(sequence)-1:
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
		X.append(seq_x)
		y.append(seq_y)
	return array(X), array(y)

stock_name = "BTC-USD"

data = yf.download(tickers=stock_name,
 period="7d",
 interval="1m")
data.reset_index(inplace=True)

print("data: ",data)

train, test = train_test_split(data, test_size = 0.2, shuffle = False)
trainf = train['Close']


# define input sequence
raw_seq = trainf.copy()
# choose a number of time steps
n_steps = 5
# split into samples
X, y = split_sequence(raw_seq, n_steps)


scaler = MinMaxScaler()
scaled_train = scaler.fit_transform(X)

scaler_y = MinMaxScaler()
scaled_y = scaler_y.fit_transform(y.reshape(-1,1))

n_features = 1
X = X.reshape((X.shape[0], X.shape[1], n_features))
print("X.shape: ",X.shape)

# define model
model = Sequential()
model.add(LSTM(100, activation='swish', input_shape=(n_steps, n_features), return_sequences=True))  #Newest Activation function found by Google
model.add(LSTM(50, activation = 'swish'))                                                           #You can also use a Relu, both works fine
model.add(Dense(1))
model.compile(optimizer='adam', loss='mse', metrics = 'mse')
model.fit(X,y,epochs=100)

#Make a queue to render the real-time data into it used as input for the model
tz = pytz.timezone('Asia/Kolkata')
data_queue = list(test['Close'].tail(5))       #Input
predictions = [0,0]                           #To keep track of past and the present predictions made by the model
temp = []                                     #To keep track of P/L
print("data -> ",data_queue)
count = 0 
p_nd_l = 0
_df = []
p = None
while True:
  min = dt.datetime.now(tz = tz).minute
  if (min%1 == 0 and (dt.datetime.now(tz=tz).second % 60) == 0):
    try:
      price = get_live_price(stock_name)       #Live quotes
    except ValueError:
      continue
    print("\nmin_",min,":",price)

    data_queue.pop(0)
    data_queue.append(price)
    print("data -> ",data_queue)

    if count>=5:

      scaled_data = scaler.transform(np.array(data_queue).reshape(1,-1))
      n_features = 1
      scaled_data = scaled_data.reshape((scaled_data.shape[0], scaled_data.shape[1], n_features))
      pred = model.predict(scaled_data)
      inv_pred = np.rint(scaler_y.inverse_transform(pred))

      print("Prediction -> ",inv_pred,'\n')
      predictions.pop(0)
      predictions.append(inv_pred)

      _p = p

      print("_p: ",_p,"p: ",p)

      if (predictions[1] - predictions[0] > 0):
        p = 1
        print("BUY")
        _ = 'BUY'
        temp.append(price)
        print("temp -> ",temp)

      else:
        p = 0
        print("SELL")
        _ = 'SELL'
        temp.append(price)
        print("temp -> ",temp)

      if (_p != p):
        if (p==1 and _p==0):
          p_nd_l+=temp[0]-temp[-1]
          temp = []
          p = None
        if (p==0 and _p==1):
          p_nd_l+=temp[-1]-temp[0]
          temp = []
          p = None

      print("_p: ",_p,"p: ",p)
      print("P/L: ",p_nd_l,'\n')
      _df.append([_,temp,p_nd_l,dt.datetime.now(tz = tz)])

    count+=1

  time.sleep(1)
