import api
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller



def backtest(df):

 
	state = 'idle'
	df['profit'] = 0.0

	for idx, row in df.iterrows():

 
		p1 = row['s1']
		p2 = row['s2']
		spread = row['spread']
		lower = row['lower']
		upper = row['upper']
 

		if state == 'idle':
			if spread > lower and spread < upper:
				state = ''

		else:

			if spread < lower and state == '':
				df.at[idx, 'profit'] = p2 - p1
				plt.scatter(idx, spread, color='green', marker='o', s=40)
				state = 'in_lower'

			if spread > upper and state == '':
				df.at[idx, 'profit'] = p1 - p2
				plt.scatter(idx, spread, color='green', marker='o', s=40)
				state = 'in_upper'

			if spread > lower and state == 'in_lower':
				df.at[idx, 'profit'] = p1 - p2
				plt.scatter(idx, spread, color='red', marker='o', s=40)
				state = 'idle'

			if spread < upper and state == 'in_upper':
				df.at[idx, 'profit'] = p2 - p1
				plt.scatter(idx, spread, color='red', marker='o', s=40)
				state = 'idle'

	print(df['profit'].sum())	






date1 = "2022-12-05"  
date2 = "2023-10-02"

date1 = pd.to_datetime(date1) 
date2 = pd.to_datetime(date2) 

#get data using Polygon
s1 = api.get_underlying(ticker='SPY',date1=date1,date2=date2,unit='day',interval='1')
s2 = api.get_underlying(ticker='AMZN',date1=date1,date2=date2,unit='day',interval='1')


spread = s1['close'] - s2['close']


# Test for stationarity of the spread using the Dickey-Fuller test
adf_test = adfuller(spread, autolag='AIC')
adf_statistic = adf_test[0]
adf_p_value = adf_test[1]
print(adf_p_value)

spread_mean = spread.rolling(window=20).mean()
spread_std = spread.rolling(window=20).std()
lower = spread_mean - spread_std
upper = spread_mean + spread_std

df = pd.DataFrame({'s1':s1['close'],'s2':s2['close'],'spread':spread,'lower':lower,'upper':upper})

backtest(df)

print(df.to_string())

plt.plot(s1.index, spread, color='#000000')
plt.plot(s1.index, lower, color='#67c4d3')
plt.plot(s1.index, upper, color='#e58fd3')
plt.show()








 