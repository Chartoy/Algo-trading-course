import api
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
import os




def get():

	date1 = "2023-05-08"  
	date2 = "2023-10-09"

	date1 = pd.to_datetime(date1) 
	date2 = pd.to_datetime(date2) 
	current_date = date1

	data = pd.DataFrame()

	while current_date <= date2:

		date = current_date.date()
		#get data
		df = api.get_grouped_daily(date)
		if df is not None:
			data = pd.concat([data, df], axis=0)

		#increment
		current_date += timedelta(days=1)


	#save data
	data.to_csv('data.csv', index=False) 





if not os.path.exists('data.csv'):
	get()

df = pd.read_csv('data.csv')



#drop cols we dont need
df.drop(['volumew', 'n'], axis=1, inplace=True)


#remove low volume in general
mask = df.groupby('ticker')['volume'].transform('min') >= 500000
df = df[df['ticker'].isin(df[mask]['ticker'])]

#mark change column only when change happened with a volume > x
min_vol = 600000
df['o_c'] = np.where(df['volume'] > min_vol, (df['open'] / df.groupby('ticker')['close'].shift(1) - 1) * 100, np.nan)

df.reset_index(drop=True, inplace=True)

#find and mark days with x% change
change = 10
df['signal'] = np.where(df['o_c'] > change, 1, np.where(df['o_c'] < -1*change, -1, 0))


#max next n high
rec_time = 3
df['max_h'] = df.groupby('ticker')['high'].transform(lambda x: x.shift(-rec_time).rolling(rec_time, min_periods=1).max())
#min next n low
df['min_l'] = df.groupby('ticker')['low'].transform(lambda x: x.shift(-rec_time).rolling(rec_time, min_periods=1).min())

recovery = 1.01
df['rec_up'] = df.groupby('ticker').apply(lambda group: (group['signal'] == -1) & (recovery*group['open'] < group['max_h'])).reset_index(level=0, drop=True).astype(int)
df['rec_dn'] = df.groupby('ticker').apply(lambda group: (group['signal'] == 1) & (group['open'] > recovery*group['min_l'])).reset_index(level=0, drop=True).astype(int)

df = df[ (df['signal'] == -1) | (df['signal'] == 1)]


#get only rows with action
df = df[(df['signal'] == 1) | (df['signal'] == -1)]

# remove nanas
df.dropna(inplace=True)

#mark success
df['success'] = (df['rec_dn'] | df['rec_up']).astype(int)


print(df.to_string())


success = 100 * len(df[(df['success'] == 1)])
success_down = len( df[ (df['signal'] == -1) & (df['success'] == 1)] ) /  len(df[(df['signal'] == -1)])
success_up = len( df[ (df['signal'] == 1) & (df['success'] == 1)] ) /  len(df[(df['signal'] == 1)])


print(" - - - - - - - - - ")
print(f"success rate {success/len(df)}")
print(f"success up {success_up} and success down {success_down}")
print(f"total results {len(df)}")
print(f"ups {len(df[df['rec_up'] == 1])}, downs {len(df[df['rec_dn'] == 1])}")













































