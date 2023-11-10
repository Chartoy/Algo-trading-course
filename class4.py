import api
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt



def back_test(df):

	state = 'wait'
	position = 0
	delta = 0.25
	take_loss = 1 
	take_profit = 1
	df['signal'] = '-'
	df['profit'] = 0.0

	for idx, row in df.iterrows():

		price = row['close']

		#wait for price to be bewtween bands
		if state == 'wait':

			if abs(price-row['mean']) < row['mean']*0.02:
				state = 'idle'
				position = 0
				plt.scatter(idx, price, color='gray', marker='o', s=20)
	   	
	   	# ready to take position
		elif state == 'idle':
			#sell
			if price > (row['upper_band'] * (1 + delta/100)):
				position = price
				df.at[idx, 'signal'] = 'sell'
				plt.scatter(idx, price, color='red', marker='o', s=20)
				state = 'sold'
				continue
			#buy
			elif price < (row['lower_band'] * (1 - delta/100)):
				position = price
				df.at[idx, 'signal'] = 'buy'
				plt.scatter(idx, price, color='red', marker='o', s=20)
				state='bought'
				continue


		elif state == 'sold':

			#buy back on a lost or buy back on a profit
			if price > (position * (1 + take_loss/100)) or (price < (position * (1-take_profit/100))):
				p = round((position - price),2)
				df.at[idx, 'profit'] =  p
				df.at[idx, 'signal'] = 'buy'
				plt.scatter(idx, price, color='green', marker='o', s=20)
				plt.annotate(p, (idx, price), textcoords="offset points", xytext=(-15,-5), ha='center', fontsize=8)
				state = 'wait'


		elif state == 'bought':

			#sell on a lost or sell on a profit
			if price < (position * (1 - take_loss/100)) or (price > (position * (1 + take_profit/100))):
				p = round((price - position),2)
				df.at[idx, 'profit'] = p
				df.at[idx, 'signal'] = 'sell'
				plt.scatter(idx, price, color='green', marker='o', s=20)
				plt.annotate(p, (idx, price), textcoords="offset points", xytext=(-15,-5), ha='center', fontsize=8)
				state = 'wait'	

	print(df[['close','lower_band','upper_band','signal','profit']].to_string())
	print(df['profit'].sum())





date1 = "2022-10-03"  
date2 = "2023-10-02"

date1 = pd.to_datetime(date1) 
date2 = pd.to_datetime(date2) 

#get data using Polygon
df = api.get_underlying(ticker='SPY',date1=date1,date2=date2,unit='day',interval='1')

window = 20  
std_multiplier = 1.5


# Calculate the rolling mean and standard deviation
df['mean'] = df['close'].rolling(window=window).mean()
df['std'] = df['close'].rolling(window=window).std()

#calculate upper and lower bands
df['upper_band'] = df['mean'] + (df['std'] * std_multiplier )
df['lower_band'] = df['mean'] - (df['std'] * std_multiplier )
 
back_test(df)

plt.plot(df.index, df[['close']],label='Close', color='black')
plt.plot(df.index, df[['mean']],label='Mean', color='gray')
plt.plot(df.index, df[['upper_band']],label='upper_band', color='green')
plt.plot(df.index, df[['lower_band']],label='lower_band', color='red')
plt.legend()
plt.show()










 





