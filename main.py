from finlib import Company
import sys
import csv

### Save technical data to csv to train a neural network ###

class Technicals(object):
  def mavg(self, data, period):
    return sum(data[-period:-1]) / len(data[-period:-1])

  def macd(self, data, period1=12, period2=26):
    # technically wrong, but I feel that / is a better indicator than -
    return self.mavg(data, period1) / self.mavg(data, period2)  


class Strategy(object):
  universe = [Company('TSM'), Company('AMD'), Company('QCOM'), Company('MU')]
  price_data = {}

  def __init__(self):
    self.read_data()

  def read_data(self): 
    min_price_length = sys.maxsize-1

    for company in self.universe: 
      historical_price_data = company.get_price_data()
      historical_prices = []

      for price in historical_price_data:
        historical_prices.append(price['adjclose'])

      if len(historical_prices) <= min_price_length:
        min_price_length = len(historical_prices)
      self.price_data[company.ticker] = historical_prices

    for company in self.universe:
      data_length = len(self.price_data[company.ticker])
      if data_length > min_price_length:
        self.price_data[company.ticker] = self.price_data[company.ticker][data_length-min_price_length:-1]

  def check_data(self):
    # print(self.price_data['INTC'][-1:])
    print(self.price_data['MU'][-1:])

  def backtest_single(self):
    ta = Technicals()

    """

    MU: MACD > 0

    AMD:  price > ma5 or ma5 > ma20

    QCOM: ma5 > ma20

    TSM: 
	if ma5 < ma20:
	  my_gains.append(tomorrows_gain)
        elif price > ma5 or ma5 > ma20:
	  my_gains.append(1.00)
        else:
	  my_gains.append(tomorrows_gain)

    """

    # define strategy
    stock = "MU"

    stock_gains = []
    my_gains = []

    print(stock + ":\n")

    for i in range(30, len(self.price_data[stock])-1):
      data = self.price_data[stock][0:i]
      price = data[-1]
      yesterdays_price = data[-2]
      tomorrows_price = self.price_data[stock][i+1]

      if i == 30 or i == len(self.price_data[stock])-2:
        print(price)

      tomorrows_gain = tomorrows_price / price

      stock_gains.append(tomorrows_gain)

      ma5 = ta.mavg(data, 5)
      ma3 = ta.mavg(data, 3)
      ma20 = ta.mavg(data, 20)
      macd = ta.macd(data)

      if macd > 0:
        my_gains.append(tomorrows_gain)
      elif ma5 > ma20:
        my_gains.append(1+(1-tomorrows_gain))
      else:
        my_gains.append(1)

    strat_file = open("strat.csv","w") 
    mkt_file = open("mkt.csv","w") 

    for i in range(0, len(my_gains)):
      strat_file.write(str(my_gains[i]) + "\n")
      mkt_file.write(str(stock_gains[i]) + "\n")

    strat_file.close()
    mkt_file.close()

  def backtest(self):
    ta = Technicals()

    """

    MU: MACD > 0

    AMD: price > ma5

    QCOM: ma5 > ma20

    TSM: 
	if ma5 < ma20:
	  my_gains.append(tomorrows_gain)
        elif price > ma5 or ma5 > ma20:
	  my_gains.append(1.00)
        else:
	  my_gains.append(tomorrows_gain)

    """

    # define strategy
    mu = "MU"
    amd = "AMD"
    qcom = "QCOM"
    tsm = "TSM"

    stock_gains = []
    my_gains = []

    for i in range(30, len(self.price_data[mu])-1):

      mu_data = self.price_data[mu][0:i]
      mu_price = mu_data[-1]
      mu_tomorrows_price = self.price_data[mu][i+1]
      mu_tomorrows_gain = mu_tomorrows_price / mu_price
      mu_ma5 = ta.mavg(mu_data, 5)
      mu_ma20 = ta.mavg(mu_data, 20)
      mu_macd = ta.macd(mu_data)

      amd_data = self.price_data[amd][0:i]
      amd_price = amd_data[-1]
      amd_tomorrows_price = self.price_data[amd][i+1]
      amd_tomorrows_gain = amd_tomorrows_price / amd_price
      amd_ma5 = ta.mavg(amd_data, 5)
      amd_ma20 = ta.mavg(amd_data, 20)
      amd_macd = ta.macd(amd_data)

      qcom_data = self.price_data[qcom][0:i]
      qcom_price = qcom_data[-1]
      qcom_tomorrows_price = self.price_data[qcom][i+1]
      qcom_tomorrows_gain = qcom_tomorrows_price / qcom_price
      qcom_ma5 = ta.mavg(qcom_data, 5)
      qcom_ma20 = ta.mavg(qcom_data, 20)
      qcom_macd = ta.macd(qcom_data)

      tsm_data = self.price_data[tsm][0:i]
      tsm_price = tsm_data[-1]
      tsm_tomorrows_price = self.price_data[tsm][i+1]
      tsm_tomorrows_gain = tsm_tomorrows_price / tsm_price
      tsm_ma5 = ta.mavg(tsm_data, 5)
      tsm_ma20 = ta.mavg(tsm_data, 20)
      tsm_macd = ta.macd(tsm_data)

      index_tomorrows_gain = (mu_tomorrows_gain + amd_tomorrows_gain + qcom_tomorrows_gain + tsm_tomorrows_gain)/4

      stock_gains.append(index_tomorrows_gain)

      my_gain = 0

      mu_weight = 0.5
      amd_weight = 0.5
      qcom_weight = 0.0
      tsm_weight = 0.0

      # MU
      if mu_macd > 0:
        my_gain += mu_tomorrows_gain * mu_weight
      else:
        my_gain += 1 * mu_weight
      
      # AMD
      if amd_price > amd_ma5:
        my_gain += amd_tomorrows_gain * amd_weight
      else:
        my_gain += 1 * amd_weight
      
      # QCOM
      if qcom_ma5 > qcom_ma20:
        my_gain += qcom_tomorrows_gain * qcom_weight
      else:
        my_gain += 1 * qcom_weight
      
      # TSM
      if tsm_ma5 < tsm_ma20:
        my_gain += tsm_tomorrows_gain * tsm_weight
      elif tsm_price > tsm_ma5 or tsm_ma5 > tsm_ma20:
        my_gain += 1.00 * tsm_weight
      else:
        my_gain += tsm_tomorrows_gain * tsm_weight

      my_gains.append(my_gain)


    strat_file = open("strat.csv","w") 
    mkt_file = open("mkt.csv","w") 

    for i in range(0, len(my_gains)):
      strat_file.write(str(my_gains[i]) + "\n")
      mkt_file.write(str(stock_gains[i]) + "\n")

    strat_file.close()
    mkt_file.close()


if __name__ == "__main__":
  strat = Strategy()
  strat.backtest_single()
