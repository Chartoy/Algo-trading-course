import pandas as pd
import yfinance as yf
import requests
from datetime import datetime, timedelta, date
import pytz
 

# YFinance - Free


def get_underlying_y(ticker='SPY', date1=None, date2=None, interval='1m'):

	#interval = 1m,2m,5m, 15m, 30m, 60m, 90m, 1h, 1d, etc. * 1m data is only for available for last 7 days

	#get string dates
	date1 = date1.strftime("%Y-%m-%d")
	date2 = date2.strftime("%Y-%m-%d") 

	spy = yf.Ticker(ticker)
	data = spy.history(start=date1, end=date2, interval=interval)

	

	#remove Datetime from the index, reindex, and change column names
	data.reset_index(inplace=True)
	data.rename(columns={'Date':'date', 'Open':'open', 'Low':'low', 'High':'high', 'Close':'close', 'Volume':'volume'}, inplace=True)

	#remove timezone ( dates should look like : 2022-10-03 09:30)
	data['date'] = pd.to_datetime(data['date']).dt.strftime("%Y-%m-%d %H:%M:%S")

	#keep only date + OHLCV
	data = data[['date','open','low','high','close','volume']]

	print(data.to_string())

	return data

 










# POLYGON


#https://api.polygon.io/v2/aggs/ticker/SPY/range/1/minute/1664755200000/1694736000000/?adjusted=true&sort=asc&limit=50000&apiKey=abc

def get_underlying(ticker='SPY',date1=None,date2=None,unit='minute',interval='1'):

	polygon_key = 'your-api-key-here'
	date1 = str(int(date1.timestamp() * 1000))
	date2 = str(int(date2.timestamp() * 1000))
	base = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/"  
	period = f"range/{interval}/{unit}/{date1}/{date2}/"
	meta = f"?adjusted=true&sort=asc&limit=50000&apiKey={polygon_key}"  
	url = base + period + meta

	ticker_df = pd.DataFrame()

	while True:

		r = request(url)

		history = r['results'] if 'results' in r else []

		ticker_samples = []
		for s in history:
				dic = {}
				d = datetime.utcfromtimestamp(int(s['t']/1000))
				dic['date'] =  gmt_datetime_to_eastern(d)
				dic['close'] = s['c']
				dic['open'] = s['o']
				dic['high'] = s['h']
				dic['low'] = s['l']
				dic['volume'] = s['v']
				ticker_samples.append(dic)
		ticker_df = pd.concat([ticker_df, pd.DataFrame(ticker_samples)], ignore_index=True)


		if 'next_url' in r:
			url = r['next_url'] + "&apiKey=" +  polygon_key  
		else:
			break


	if unit == 'day':
		ticker_df['date'] = ticker_df['date'].dt.date

	return ticker_df




def get_grouped_daily(date):

	polygon_key = 'your-api-key-here'
	date = date.strftime('%Y-%m-%d')

	base = f"https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{date}?"  
	meta = f"?adjusted=true&include_otc=false&apiKey={polygon_key}"  
	url = base + meta
	r = request(url)

	if not 'results' in r:
		return None

	results = r['results']
	df = pd.DataFrame(results)

	#change columns names
	new_column_names = {'t': 'date', 'T': 'ticker', 'v': 'volume','vw': 'volumew', 'o': 'open','l': 'low','h': 'high','c': 'close'}
	df = df.rename(columns=new_column_names)

	#change date (like 1673298000000) into object
	df['date'] = pd.to_datetime(df['date'], unit='ms')
	df['date'] = df['date'].dt.date
	return df


  



def request(url):
	 
	response = requests.get(url)
	return response.json()






def gmt_datetime_to_eastern(gmt_datetime):
	
    # Define the GMT timezone
	gmt_timezone = pytz.timezone('GMT')
    
    # Convert the GMT datetime to the Eastern timezone (taking DST into account)
	eastern_timezone = pytz.timezone('US/Eastern')
	eastern_time = gmt_timezone.localize(gmt_datetime).astimezone(eastern_timezone).replace(tzinfo=None)
    
	return eastern_time


















