import api
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt




def back_test(df):


	#get the continius probability density estimation ( Kernel Density Estimation )
	kde = sns.kdeplot(df['returns'], cumulative=False)

	x_kde, y_kde = kde.get_lines()[0].get_data() 

	# treshold where x% of the data points in the density curve are *below* that value
	buy_threshold = np.percentile(x_kde, 30)  

	state = 'idle'
	df['signal'] = "-"
	df['profit'] = 0
	buy_price = 0

	for idx, row in df.iterrows():

		returns = row['returns']
		price = row['close']
		 

		if state == 'idle':

			if returns < buy_threshold:
				state = 'wait_sell'
				df.at[idx, 'signal'] = 'buy'
				buy_price = price

 
		elif state == 'wait_sell':

			#sell on profit/loss
			if price > 1.01 * buy_price or price < 0.98 * buy_price:
				state = 'idle'
				df.at[idx, 'signal'] = 'sell'
				df.at[idx, 'profit'] = price - buy_price



	profit = df['profit'].sum()
	win_ratio = (df['profit'] > 0).sum() / (df['profit'] != 0).sum()
	
	print(f"Returns treshold: {buy_threshold}")
	print(df[['date','close','returns','signal','profit']].to_string())
	print(profit,win_ratio)





date1 = "2022-10-03"  
date2 = "2023-09-25"

date1 = pd.to_datetime(date1) 
date2 = pd.to_datetime(date2) 

#get data using Polygon
df = api.get_underlying(ticker='TSLA',date1=date1,date2=date2,unit='day',interval='1')

#returns
df['returns'] = df['close'].pct_change() * 100


#Calculate Probability Density Function (PDF) using KDE  - Kernel Density Estimation 
  
#get the Frequency Distribution Estimation of a dataset by dividing the data into discrete bins and counting the number of data points in each bin.
sns.histplot(df['returns'], kde=True, bins=60, color='#fcdb2f')

mean = df['returns'].mean()
std_dev = df['returns'].std()
plt.axvline(mean + std_dev, color='#56e2de', linestyle='dashed')
plt.axvline(mean - std_dev, color='#56e2de', linestyle='dashed')

back_test(df)

#plt.show()









