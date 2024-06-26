'''
Created on 01-Sep-2022

@brief Read in all the chart patterns from the reference folder and find new stocks matching them

@author: Anshul

Use activate-global-python-argcomplete on first install
'''

import os
import csv
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np

from lib.tradingview import Interval, convert_timeframe_to_quant, get_tvfeed_instance
from lib.misc import get_filelist
from lib.retrieval import get_stock_listing
from lib.logging import set_loglevel, log
from lib.cache import cached
from lib.indices import load_blacklist

from stocks.models import Stock, Market

from reverse_search import nse_list, bse_list, blacklist_file

local_cache = {}
ignore_list = []

def compare_stock_info(r_df, s_df, threshold, delta=False, logscale=False):
    """
    Compares stock information between two dataframes.

    Args:
        r_df: A single column dataframe containing the return data.
        s_df: A dataframe containing the stock data.
        threshold: The correlation threshold.
        delta: A boolean value indicating whether to use the daily percentage change.
        logscale: A boolean value indicating whether to use the log scale.

    Returns:
        A dictionary, with the column name as key and the correlation values as the value of the key.
    """

    # Convert r_df to a Series.
    r_df = r_df.squeeze()

    #for index, row in s_df.iterrows():
    #    print(index, row)

    # Calculate the correlation of r_df with each column of s_df.
    #corr_values = r_df.corr(s_df, numeric_only=True)
    corr_values = s_df.corrwith(r_df)
    #columns = list(s_df.columns)

    # Find the indices of the columns whose correlation values are greater than or equal to the threshold.
    indices = np.where(corr_values >= threshold)[0]

    #for ii in range(0, len(corr_values)):
    #    print(columns[ii], corr_values[ii])

    # Return a dictionary with the column names as keys and the correlation values as values.
    ret = {'max': max(corr_values),
           'min': min(corr_values),
           'map': {}}
    if len(indices)>0:
        ret['map'] = dict(zip(s_df.columns[indices], corr_values.iloc[indices]))
    return ret

def get_dataframe(stock, market, timeframe, duration, date=datetime.datetime.now(), offline=False):
    if timeframe not in [Interval.in_3_months,
                         Interval.in_monthly, 
                         Interval.in_weekly, 
                         Interval.in_daily]:
        offline = False


    if not offline:
        username = 'AnshulBot'
        password = '@nshulthakur123'

        tv = get_tvfeed_instance(username, password)
        symbol = stock.strip().replace('&', '_')
        symbol = symbol.replace('-', '_')
        symbol = symbol.replace('*', '')
        nse_map = {'UNITDSPR': 'MCDOWELL_N',
                   'MOTHERSUMI': 'MSUMI'}
        if symbol in nse_map:
            symbol = nse_map[symbol]
        
        s_df = cached(name=symbol, timeframe=timeframe)
        if s_df is not None:
            #print('Found in Cache')
            pass
        else:
            try:
                s_df = tv.get_hist(
                            symbol,
                            market,
                            interval=timeframe,
                            n_bars=duration,
                            extended_session=False,
                        )
                if s_df is not None:
                    cached(name=symbol, df=s_df, timeframe=timeframe)
            except:
                s_df = None
                print(symbol)
    else:
        try:
            market_obj = Market.objects.get(name=market)
        except Market.DoesNotExist:
            log(f"No object exists for {market}", logtype='error')
            return None
        try:
            stock_obj = Stock.objects.get(symbol=stock, market=market_obj)
        except Stock.DoesNotExist:
            log(f"Stock with symbol {stock} not found in {market}", logtype='error')
            return
        s_df = get_stock_listing(stock_obj, duration=duration, last_date = date, 
                                 resample=True if timeframe in [Interval.in_monthly, 
                                                                Interval.in_weekly] else False, 
                                 monthly=True if timeframe in [Interval.in_monthly] else False)
        s_df = s_df.drop(columns = ['delivery', 'trades'])
    return s_df

def load_references(folder):
    files = get_filelist(folder=folder)
    df_arr = []
    for file in files:
        if file[-3:] == 'csv':
            #print(f'Read {file}')
            r_df = pd.read_csv(os.path.join(folder, file))
            if 'date' in r_df.columns:
                r_df = r_df.drop(columns = ['Candle Color','Candle Length','open','change', 'date'])
            else:
                r_df = r_df.drop(columns = ['Candle Color','Candle Length','open','change'])

            r_df.set_index('index', inplace = True)
            r_df = r_df.sort_index()

            r_df = r_df.reindex(columns = ['close'])
            r_df.rename(columns={'close': 'change'},
                                inplace = True)
            #r_df.drop(r_df.iloc[len(r_df)-1].name, inplace=True) #Last entry is the month which may still be running
            
            #start_date = r_df.index.values[0]
            #end_date = r_df.index.values[-1]
            
            r_df.drop(r_df.iloc[0].name, inplace=True) #First entry is not the change, just the baseline
            r_df.reset_index(inplace = True)
            r_df = r_df.drop(columns=['index'])
            #print(r_df.tail(10))
            #print(len(r_df))
            df_arr.append(r_df)
    print('Loaded references', flush=True)
    
    return (df_arr, files)

def load_stocks_data(timeframe, n_bars, offline, logscale, min_length, match='close', exchange='both'):
    '''
    Load all the stocks into a single dataframe to enable vector processing of correlation across
    all of them rather than iterating one by one, which is slow.
    '''
    indices = []
    b_indices = []
    global ignore_list 
    global local_cache
    ref_columns = ['open', 'high', 'low', 'close', 'volume'] 
    ref_columns.remove(match)
    
    blacklist = load_blacklist(blacklist_file)

    if exchange in ['nse', 'both']:
        with open(nse_list, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if f"NSE:{row['SYMBOL'].strip().upper()}" in blacklist:
                    log(f"Skip blacklisted symbol: NSE:{row['SYMBOL'].strip().upper()}", logtype='info')
                    continue
                indices.append(row['SYMBOL'].strip())
    
    if exchange in ['bse', 'both']:
        with open(bse_list, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Security Id'].strip() not in indices:
                    if f"BSE:{row['Security Id'].strip().upper()}" in blacklist:
                        log(f"Skip blacklisted symbol: BSE:{row['Security Id'].strip().upper()}", logtype='info')
                        continue
                    b_indices.append(row['Security Id'].strip())

    df_arr = []
    for stock in indices:
        s_df = None
        if stock in local_cache:
            s_df = local_cache[stock].copy(deep=True)
        else:
            if stock in ignore_list:
                continue
            print('.', end='', flush=True)
            s_df = get_dataframe(stock=stock, 
                                market='NSE', 
                                timeframe=timeframe, 
                                duration=n_bars, 
                                offline=offline)
            if s_df is not None:
                local_cache[stock] = s_df.copy(deep=True)
        if s_df is not None and len(s_df)>=min_length:
            s_df = s_df.drop(columns = ref_columns)
            s_df = s_df.sort_index()
            s_df.reset_index(inplace = True)
            if 'datetime' in s_df.columns:
                s_df = s_df.drop(columns='datetime')
            else:
                s_df = s_df.drop(columns='date')
            s_df.rename(columns={match: stock},
                        inplace = True)
            s_df = s_df.reindex(columns = [stock])
            s_df = s_df[~s_df.index.duplicated(keep='first')]
            s_df = s_df.tail(min_length)
            # If logscale is True, convert s_df to the log scale.
            if logscale:
                s_df = np.log10(s_df)
            s_df = s_df - s_df.mean()
            s_df.reset_index(inplace = True, drop=True)
            df_arr.append(s_df)
        elif s_df is None:
            ignore_list.append(stock)
    for stock in b_indices:
        if stock in local_cache:
            s_df = local_cache[stock].copy(deep=True)
        else:
            if stock in ignore_list:
                continue
            print('.', end='', flush=True)
            s_df = get_dataframe(stock=stock, 
                                market='BSE', 
                                timeframe=timeframe, 
                                duration=n_bars, 
                                offline=offline)
            if s_df is not None:
                local_cache[stock] = s_df.copy(deep=True)

        if s_df is not None and len(s_df)>=min_length:
            s_df = s_df.drop(columns = ref_columns)
            s_df = s_df.sort_index()
            s_df.reset_index(inplace = True)
            if 'datetime' in s_df.columns:
                s_df = s_df.drop(columns='datetime')
            else:
                s_df = s_df.drop(columns='date')
            s_df.rename(columns={match: stock},
                        inplace = True)
            s_df = s_df.reindex(columns = [stock])
            s_df = s_df[~s_df.index.duplicated(keep='first')]
            s_df = s_df.tail(min_length)
            # If logscale is True, convert s_df to the log scale.
            if logscale:
                s_df = np.log10(s_df)
            s_df = s_df - s_df.mean()
            s_df.reset_index(inplace = True, drop=True)
            df_arr.append(s_df)
        elif s_df is None:
            ignore_list.append(stock)
    #print('Condensing dataframes.', flush=True)
    df = None
    if len(df_arr)>0:
        df = pd.concat(df_arr, axis=1, join='outer')
    #print('Loaded stock data for the run', flush=True)
    #print(f'Ignore list: {ignore_list}')
    return df

def main(reference, timeframe, logscale=False, match = 'close', offline=False,
         exchange='both'):
    cutoff_date = datetime.datetime.strptime('01-Aug-2018', "%d-%b-%Y")
    delta = False
    
    # Load the reference candlestick charts from the folder
    (df_arr, fnames) = load_references(reference)
    c_thresh = 0.96

    max_df_len = 0
    for a in df_arr:
        max_df_len = max(max_df_len, len(a))

    #cutoff_date = r_df.index.values[0]

    d = relativedelta(datetime.datetime.today(), cutoff_date)
    if timeframe == Interval.in_monthly:
        #print('Monthly')
        n_bars = max((d.years*12) + d.months+1, max_df_len)+10
    elif timeframe == Interval.in_3_months:
        #print('3 Monthly')
        n_bars = max((d.years*4) + d.months+1, max_df_len)+10
    elif timeframe == Interval.in_weekly:
        #print('Weekly')
        n_bars = max((d.years*52) + (d.months*5) + d.weeks+1, max_df_len)+10
    elif timeframe == Interval.in_4_hour:
        #print('4 Hourly')
        n_bars = max(500, max_df_len)+10
    elif timeframe == Interval.in_2_hour:
        #print('2 Hourly')
        n_bars = max(500, max_df_len)+10
    elif timeframe == Interval.in_1_hour:
        #print('Hourly')
        n_bars = max(500, max_df_len)+10
    else:
        #print('Daily')
        n_bars = max(500, max_df_len)+10
    
    #print(f'Get {n_bars} candles')
    
    for ii, r_df in enumerate(df_arr):
        s_df = load_stocks_data(timeframe=timeframe, 
                                n_bars=n_bars, 
                                offline=offline, 
                                logscale=logscale, 
                                min_length=len(r_df)+1, 
                                match=match,
                                exchange=exchange)
        if s_df is not None:
            c = compare_stock_info(r_df, s_df, threshold=c_thresh, delta=delta, logscale=logscale)
            #print(f'\n {fnames[ii]}: Shortlist: {json.dumps(c, indent=2)}\n')
            if len(c["map"])>0:
                print(f'\n {fnames[ii]}: Shortlist: {sorted( ((v,k) for k,v in c["map"].items()), reverse=True)}')
        else:
            continue
        
if __name__ == "__main__":
    day = datetime.date.today()
    import argparse
    parser = argparse.ArgumentParser(description='Perform reverse search for indices')
    parser.add_argument('-t', '--timeframe', help="Timeframe")
    parser.add_argument('-f', '--folder', help="Folder containing CSV reference files of the candlesticks patterns to search for")
    parser.add_argument('-l', '--log', action="store_true", default=False, help="Use log scaling for price values ")
    parser.add_argument('-o', '--offline', help="Run the analysis using offline data", action = "store_true", default=False)
    parser.add_argument('-e', '--exchange', help="Specify the stock exchange where symbols must be searched", default='both')
    timeframe = '1M'
    reference = './images/references/'
    #Can add options for weekly sampling and monthly sampling later
    args = parser.parse_args()
    if args.folder is not None and len(args.folder)>0:
        print('Reference folder: {}'.format(args.folder))
        reference = args.folder
    if args.timeframe is not None and len(args.timeframe)>0:
        timeframe=args.timeframe
    exchange = 'both'
    if args.exchange is not None and len(args.exchange)>0:
        if args.exchange.strip().lower() not in ['both', 'bse', 'nse']:
            print('Unknown exchange. Defaulting to "both"')
        else:
            exchange = args.exchange
    set_loglevel('error')
    np.seterr(divide='ignore', invalid='ignore')
    main(reference, 
         timeframe=convert_timeframe_to_quant(timeframe),
         logscale=args.log, 
         match = 'close',
         offline = args.offline,
         exchange=exchange)
