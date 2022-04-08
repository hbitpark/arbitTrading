import pandas as pd    
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.model_selection import cross_val_score

def knn(self, sDiff):
    regDF = pd.DataFrame()
    regDF['datetime'] = self.candleDF0["datetime"]
    #regDF.set_index('datetime', inplace=True)
    regDF['Close'] = sDiff
    regDF['MA20'] = regDF['Close'].rolling(window=10).mean()
    regDF['Corr'] = regDF['Close'].rolling(window=10).corr(regDF['MA20'])
    regDF = regDF.dropna()

    print("regDF: ",regDF)
    print("----------------------------")

    X = regDF[['Close', 'MA20', 'Corr']]
    y = np.where(regDF['Close'].shift(-1) > regDF['Close'],1,-1)

    train_pct = 0.7
    split = int(train_pct * len(regDF))
    X_train, X_test, y_train, y_test = X[:split], X[split:], y[:split], y[split:]

    knn = KNeighborsClassifier(n_neighbors = 15)
    knn.fit(X_train, y_train)
    accuracy_train = accuracy_score(y_train, knn.predict(X_train))
    accuracy_test = accuracy_score(y_test, knn.predict(X_test))

    print('Train data Accuracy: %.2f' % accuracy_train)
    print('Test  data Accuracy: %.2f' % accuracy_test)

    regDF['Signal'] = knn.predict(X)
    regDF['predict'] = np.log(regDF['Close']/regDF['Close'].shift(1))
    Cum_SPY_Returns = regDF[split:]['predict'].cumsum()*100

    regDF['Strategy'] = regDF['predict']*regDF['Signal'].shift(1)
    Cum_Strategy = regDF[split:]['Strategy'].cumsum()*100

    plt.figure(figsize=(10,5))
    plt.plot(Cum_SPY_Returns, color='r', label='predict')
    plt.plot(Cum_Strategy, color='b', label='Strategy')
    plt.legend()
    plt.show()

def regression(self, sDiff):
    regDF = pd.DataFrame()
    regDF['datetime'] = self.candleDF0["datetime"]
    #regDF.set_index('datetime', inplace=True)
    regDF['Close'] = sDiff
    regDF['MA20'] = regDF['Close'].rolling(window=10).mean()
    regDF['Corr'] = regDF['Close'].rolling(window=10).corr(regDF['MA20'])
    regDF = regDF.dropna()

    print("regDF: ",regDF)
    print("----------------------------")

    X = regDF[['Close', 'MA20', 'Corr']]
    y = np.where(regDF['Close'].shift(-1) > regDF['Close'],1,-1)

    train_pct = 0.7
    split = int(train_pct * len(regDF))
    X_train, X_test, y_train, y_test = X[:split], X[split:], y[:split], y[split:]

    # train
    model = LogisticRegression()
    model = model.fit(X_train, y_train)
    pd.DataFrame(zip(X.columns, np.transpose(model.coef_)))
    #print("X_test: ",X_test)
    #print("X_test len: ",len(X_test))

    probability = model.predict_proba(X_test)
    #print(probability)
    predicted = model.predict(X_test)
    #print(predicted)

    print(metrics.confusion_matrix(y_test, predicted))
    print(metrics.classification_report(y_test, predicted))
    print("model score: ",model.score(X_test,y_test))

    cross_val = cross_val_score(LogisticRegression(), X, y, scoring='accuracy', cv=10)
    print(cross_val)
    print(cross_val.mean())

    regDF['Signal'] = model.predict(X)
    print("================")
    print("regDF['Signal']: ",regDF['Signal'])
    regDF['predict'] = np.log(regDF['Close']/regDF['Close'].shift(1))
    Cumulative_Predict = np.cumsum(regDF[split:]['predict'])*-1

    regDF['predict'] = regDF['predict']* regDF['Signal'].shift(1)
    Cumulative_Strategy = np.cumsum(regDF[split:]['predict'])

    plt.figure(figsize=(10,5))
    plt.plot(Cumulative_Predict, color='r',label = 'predict')
    plt.plot(Cumulative_Strategy, color='b', label = 'Strategy')
    plt.legend()
    plt.show()