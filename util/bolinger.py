import math, numpy

def sma(closes_candles, n):
    res = 0
    for x in closes_candles:
        if x == numpy.nan:
            continue
        else:
            res += x
    return (res / n)

def lwma(closes_candles): # WMA = SUM (CLOSE (i) * i, N) / SUM (i, N) 
    res = 0
    nSum = 0
    i = 0
    for x in closes_candles:
        if x == numpy.nan:
            continue
        else:
            i = i+1
            res += (x*i)
            nSum += i
    return (res / nSum)


def standardDeviation(candles, n):
    deviation = 0.0
    average = sma(candles, n)
    for x in candles:
        if x == numpy.nan:
            continue
        else:
            deviation += pow(x - average, 2)
    return math.sqrt(deviation / n)

def bollinger_strat(candles, n, stdMux):
    n = n - 1
    #("####################################")
    #print("sma")
    x = sma(candles[-n:], n)
    #print(x)
    #print("std_dev")
    std_dev = standardDeviation(candles[-n:], n)
    #print(std_dev)
    #print("####################################")
    print("candles: ",candles," /n: ",n, " /std_dev: ",std_dev)
    A1 = x + std_dev * stdMux
    A2 = x - std_dev * stdMux
    close = candles[-1]
    #print("up: ",A1, " /dn: ",A2)
    if (close >= A1):# and close <= A1):
        #print("bollinger: sell")
        return 1
    elif (close < A2):# and close >= A2):
        #print("bollinger: buy")
        return -1
    else:
        #("bollinger : nothing to do")
        return 0
