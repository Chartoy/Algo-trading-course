import api
import pandas as pd
from datetime import datetime, timedelta, date


date1 = "2022-10-03"  
date2 = "2023-09-15"

date1 = pd.to_datetime(date1) 
date2 = pd.to_datetime(date2) 


df = api.get_underlying(ticker='SPY',date1=date1, date2=date2, interval='1', unit='day')
print(df)


