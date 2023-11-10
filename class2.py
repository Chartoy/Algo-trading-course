import api
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt



date1 = "2022-10-03"  
date2 = "2023-09-15"

date1 = pd.to_datetime(date1) 
date2 = pd.to_datetime(date2) 


df = api.get_underlying(ticker='SPY',date1=date1,date2=date2,unit='day',interval='1')


#returns
df['returns'] = df['close'].pct_change() * 100




average = df['returns'].mean()
atr = np.abs(df['returns']).mean()
print(f"average:{average}, ATR:{atr}")



# 3 consecutive negative returns
n = 3
total = len(df['returns']) - n
neg_3 =  df['returns'].rolling(n).apply(lambda x: all(x < 0)).fillna(False).astype(int).sum()
print(f"Three consecutive negative empirical probability:{neg_3/total}")



#probability of having more than 1% change?
for i in range(1,4):
	ret = sum(df['returns'].abs()>i)
	ratio = 100*(ret/len(df))
	print(f"probability of moving more than ±{i}%: {round(ratio,2)}%")



#plot
plt.plot(df.index, df['returns'], color='#FFD700')
plt.show()







