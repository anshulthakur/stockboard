'''
Created on 02-May-2022

@author: anshul
'''

import os
import sys
import init
import numpy as np
import pandas as pd
import traceback
import datetime
import json
import csv
import requests

# format price data
pd.options.display.float_format = '{:0.2f}'.format

#Prepare to load stock data as pandas dataframe from source. In this case, prepare django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from django.conf import settings
from stocks.models import Stock, Market


# imports
from talib.abstract import *

from lib.tradingview import convert_timeframe_to_quant, get_tvfeed_instance
from lib.cache import cached
from lib.logging import set_loglevel, log
from lib.misc import create_directory, handle_download, get_requests_headers
from lib.retrieval import get_stock_listing
from lib.indices import download_historical_index_reports, NSE_INDEX_URLS, get_symbol_replacements

from custom_index import index_map, get_index_dataframe

#Libraries for the Plotting
from pandas.tseries.frequencies import to_offset
import holoviews as hv
from holoviews import opts
import panel as pn

hv.extension('bokeh')

index_data_dir = settings.PROJECT_DIRS.get('reports')
member_dir = os.path.join(index_data_dir, 'members')
plotpath = os.path.join(index_data_dir, 'plots')
cache_dir = settings.PROJECT_DIRS.get('cache')

rrg_dir = settings.PROJECT_DIRS.get('rrg')
progress_file = settings.RRG_PROGRESS_FILE

INDICES = [index for index in NSE_INDEX_URLS]

def download_index_constituents(name=None, overwrite=True):
    urlmap = NSE_INDEX_URLS

    if name is not None and name not in urlmap:
        log("Index not found in local map.", logtype='error')
        return
    
    session = requests.Session()
    # Set correct user agent
    session.headers.update(get_requests_headers())
    session.headers.update({"host": "niftyindices.com",
                            "referer": "https://niftyindices.com/"})
    if name is not None:
        session.get(urlmap[name]['base'])
        handle_download(session, url = urlmap[name]['url'], filename = f'{name}.csv'.format(name=name), path=member_dir, overwrite=overwrite)
    else:
        for name, mapping in urlmap.items():
            session.get(mapping['base'])
            handle_download(session, url = mapping['url'], filename = f'{name}.csv'.format(name=name), path=member_dir, overwrite=overwrite)

def load_progress():
    import json
    try:
        with open(progress_file, 'r') as fd:
            progress = json.load(fd)
            try:
                date = datetime.datetime.strptime(progress['date'], '%d-%m-%Y')
                if date.day == datetime.datetime.today().day and \
                    date.month == datetime.datetime.today().month and \
                    date.year == datetime.datetime.today().year:
                    log('Load saved progress', logtype='debug')
                    return progress['index']
            except:
                #Doesn't look like a proper date time
                pass
    except:
        pass
    
    log('No progress saved', logtype='debug')
    return []

def save_progress(index, state='success'):
    import json
    create_directory(rrg_dir)
    processed = load_progress()
    if len(processed) == 0:
        processed = [index]
    else:
        processed.append({index: state})
    with open(progress_file, 'w') as fd:
            fd.write(json.dumps({'date':datetime.datetime.today().strftime('%d-%m-%Y'),
                                 'index': processed}))
    return


def load_members(sector, members, date, sampling='w', entries=50, online=True, sector_df = None):
    print('========================')
    print(f'Loading for {sector}')
    print('========================')
    
    if (sector_df is None) or (sector_df is not None and sector not in list(sector_df.columns)):
        df = pd.read_csv(os.path.join(index_data_dir, '{sector}.csv'.format(sector=sector)))
        df.rename(columns={'Index Date': 'date',
                        'Closing Index Value': sector},
                inplace = True)
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')+ pd.Timedelta('9 hour') +  pd.Timedelta('15 minute')
        df.set_index('date', inplace = True)
        df = df.sort_index()
        df = df.reindex(columns = [sector])
        df = df[~df.index.duplicated(keep='first')]
    else:
        df = sector_df
    
    if date is not None:
        df = df[:date.strftime('%Y-%m-%d')]
    if sampling=='w':
        #Resample weekly
        logic = {}
        for cols in df.columns:
            if cols != 'date':
                logic[cols] = 'last'
        #Resample on weekly levels
        df = df.resample('W').apply(logic)
        #df = df.resample('W-FRI', closed='left').apply(logic)
        df.index -= to_offset("6D")
        df.index = df.index + pd.Timedelta('9 hour') +  pd.Timedelta('15 minute')
    if sampling=='M':
        #Resample weekly
        logic = {}
        for cols in df.columns:
            if cols != 'date':
                logic[cols] = 'last'
        #Resample on weekly levels
        df = df.resample('M').apply(logic)
        df.index = df.index + pd.Timedelta('9 hour') +  pd.Timedelta('15 minute')

    #Truncate to last n days
    df = df.iloc[-entries:]
    #print(df.head(10))
    #print(len(df.index))
    #print(date)
    start_date = df.index.values[0]
    end_date = df.index.values[-1]
    log(f'End date: {end_date}', logtype='debug')
    #print(start_date, type(start_date))

    #print(np.datetime64(date))
    duration = np.datetime64(datetime.datetime.today())-start_date
    if sampling=='w':
        duration = duration.astype('timedelta64[W]')/np.timedelta64(1, 'W')
    elif sampling=='M':
        duration = duration.astype('timedelta64[M]')/np.timedelta64(1, 'M')
    else:
        duration = duration.astype('timedelta64[D]')/np.timedelta64(1, 'D')
    
    duration = max(int(duration.astype(int))+1, entries)
    #print(duration)
    username = 'AnshulBot'
    password = '@nshulthakur123'
    tv = None
    interval = convert_timeframe_to_quant(sampling)
    log(f'Samlping interval: {interval}', logtype='debug')

    #print(duration, type(duration))
    df_arr = [df]
    for stock in members:
        try:
            if not online:
                market = Market.objects.get(name='NSE')
                stock_obj = Stock.objects.get(symbol=stock, market=market)
                s_df = get_stock_listing(stock_obj, duration=duration, last_date = date)
                s_df = s_df.drop(columns = ['open', 'high', 'low', 'volume', 'delivery', 'trades'])
                #print(s_df.head())
                if len(s_df)==0:
                    print('Skip {}'.format(stock_obj))
                    continue
                s_df.rename(columns={'close': stock},
                           inplace = True)
                s_df.reset_index(inplace = True)
                s_df['date'] = pd.to_datetime(s_df['date'], format='%d-%m-%Y')+ pd.Timedelta('9 hour') +  pd.Timedelta('15 minute')
                #s_df.drop_duplicates(inplace = True, subset='date')
                s_df.set_index('date', inplace = True)
                s_df = s_df.sort_index()
                s_df = s_df.reindex(columns = [stock])
                s_df = s_df[~s_df.index.duplicated(keep='first')]
                #print(s_df[s_df.index.duplicated(keep=False)])
                s_df = s_df.loc[pd.to_datetime(start_date).date():pd.to_datetime(end_date).date()]
                #df[stock] = s_df[stock]
                df_arr.append(s_df)
            else:
                log(f'Download {stock} data', logtype='debug')
                symbol = stock.strip().replace('&', '_')
                symbol = symbol.replace('-', '_')
                nse_map = get_symbol_replacements()
                if symbol in nse_map:
                    symbol = nse_map[symbol]
                
                s_df = cached(name=symbol, timeframe=interval)
                if s_df is None:
                    tv = get_tvfeed_instance(username, password)
                    s_df = tv.get_hist(
                                symbol,
                                'NSE',
                                interval=interval,
                                n_bars=duration,
                                extended_session=False,
                            )
                    if s_df is not None:
                        cached(name=symbol, df = s_df, timeframe=interval)
                if s_df is None:
                    print(f'Error fetching information on {symbol}')
                else:
                    s_df = s_df.drop(columns = ['open', 'high', 'low', 'volume'])
                    #print(s_df.tail())
                    if len(s_df)==0:
                        print('Skip {}'.format(symbol))
                        continue
                    s_df.reset_index(inplace = True)
                    s_df.rename(columns={'close': stock, 'datetime': 'date'},
                               inplace = True)
                    #print(s_df.columns)
                    #pd.to_datetime(df['DateTime']).dt.date
                    #s_df['date'] = pd.to_datetime(s_df['date'], format='%d-%m-%Y %H:%M:%S').dt.date
                    s_df['date'] = pd.to_datetime(s_df['date'], format='%d-%m-%Y %H:%M:%S')
                    if sampling=='w':
                        #Force all weekdays to start on Mondays
                        s_df['date'] = s_df['date'] - pd.to_timedelta(s_df['date'].dt.weekday, unit='D')
                        #s_df.index = s_df.index + pd.Timedelta('9 hour') +  pd.Timedelta('15 minute')
                    #s_df.drop_duplicates(inplace = True, subset='date')
                    s_df.set_index('date', inplace = True)
                    
                    s_df = s_df.sort_index()
                    s_df = s_df.reindex(columns = [stock])
                    s_df = s_df[~s_df.index.duplicated(keep='first')]
                    #print(s_df.index.values[0], type(s_df.index.values[0]))
                    #print(pd.to_datetime(start_date).date(), type(pd.to_datetime(start_date).date()))
                    #Add 1 timedelta to include the last date element as well
                    s_df = s_df.loc[pd.to_datetime(start_date).date():pd.to_datetime(end_date).date()+pd.Timedelta(days=1)]
                    #print(s_df.loc[start_date:end_date])
                    #print(s_df[s_df.index.duplicated(keep=False)])
                    if len(s_df) == 0:
                        log(f'{stock} does not have data in the given range', logtype='warning')
                        continue
                    if ((pd.to_datetime(s_df.index[0]) - df.index[0]).days > 0) and ((pd.to_datetime(s_df.index[0]) - df.index[0]).days <7):
                        #Handle the case of the start of the week being a holiday
                        data = {stock: s_df.iloc[0][stock]}
                        log('Handle holiday', logtype='debug')
                        s_df = pd.concat([s_df, pd.DataFrame(data, index=[pd.to_datetime(df.index[0])])])
                        #print(s_df.tail(10))
                        s_df.sort_index(inplace=True)
                        #print(s_df.head(10))
                        s_df.drop(s_df.index[1], inplace=True)
                    #print(s_df.head(10))
                    #df[stock] = s_df[stock]
                    #log(s_df.tail(), logtype='debug')
                    df_arr.append(s_df)
        except Stock.DoesNotExist:
            print(f'{stock} values do not exist')
    #print(df_arr)
    #Sleight of hand for now: 
    # The issue is that index df is in format DD-MM-YYYY and others are in DD-MM-YY HH-MM-SS. concat does not add them nicely.
    df = pd.concat(df_arr, axis=1)
    #s_df[sector] = df
    #print(df.tail(10))
    df = df[~df.index.duplicated(keep='first')]
    df.index.names = ['date']
    #log(df.head(10), logtype='debug')
    #log(df.tail(10), logtype='info')
    return df

def compute_jdk(benchmark = 'Nifty_50', base_df=None):
    rolling_avg_len = 10
    log(base_df.head(10), logtype='debug')
    df = base_df.copy(deep=True)
    
    df.sort_values(by='date', inplace=True, ascending=True)
    #Drop all columns which don't have a valid first row
    # for cols in df.columns:
    #     #print(f'{cols}: {df[cols].isnull().sum()}')
    #     if np.isnan(df[cols].iloc[0]):
    #         log('Drop {}. Contains NaN in the first row.'.format(cols), logtype='warning')
    #         df = df.drop(columns = cols)

    #Drop column if any row has NaN
    drops = []
    for col in df.columns:
        #print(f'{cols}: {df[cols].isnull().sum()}')
        if df[col].isna().any():
            try:
                df[col] = df[col].ffill()
                if df[col].isna().any():
                    log('Drop {}. Contains NaN after ffill.'.format(col), logtype='warning')
                    drops.append(col)
            except:
                log('Drop {}. Contains NaN'.format(col), logtype='warning')
                drops.append(col)
    if len(drops)>0:
        log(df.head(10), logtype='debug')
        df.drop(columns=drops, inplace=True)

    if len(df) == 0:
        return None
    #Calculate the 1-day Returns for the Indices
    df = df.pct_change(1)
    #print(df.tail())
    #Calculate the Indices' value on and Index-Base (100) considering the calculated returns
    df.iloc[0] = 100
    for ticker in df.columns:
        for i in range(1, len(df[ticker])):
            df[ticker].iloc[i] = df[ticker].iloc[i-1]*(1+df[ticker].iloc[i])

    #Define the Index for comparison (Benchamrk Index): Nifty50
    log(f'Benchmark: {benchmark}', logtype='debug')
    if benchmark not in list(df.columns):
        log(f'{benchmark} not present in dataframe', logtype='error')
        return None
    benchmark_values = df[benchmark]
    df = df.drop(columns = benchmark)


    #print(df.tail())
    log(f'Dataframe contains {len(df)} rows now.', logtype='debug')

    #Calculate the relative Performance of the Index in relation to the Benchmark
    for ticker in df.columns:   
        df[ticker] = (df[ticker]/benchmark_values) - 1
    
    #Normalize the values considering a 14-days Window (Note: 10 weekdays)
    for ticker in df.columns:
        df[ticker] = 100 + ((df[ticker] - df[ticker].rolling(rolling_avg_len).mean())/df[ticker].rolling(rolling_avg_len).std() + 1)

    # Rounding and Excluding NA's
    #print(df.head())
    #Drop column if any row has NaN after this operation
    #df = df.round(2).dropna()
    
    df = df.round(2)

    #log(df, logtype='info')
    #First 'rolling_avg_len' columns will be NaN
    if(len(df)<25):
        log('Length of dataframe less than 25. Stop computing', logtype='warning')
        return None
    #Compute on the last few dates only (last 5 weeks/days)
    JDK_RS_ratio = df.iloc[-25:]
    JDK_RS_ratio = JDK_RS_ratio.dropna()

    log(df.head(10), logtype='debug')
    log(df.tail(10), logtype='debug')
    
    #Calculate the Momentum of the RS-ratio
    #JDK_RS_momentum = JDK_RS_ratio.pct_change(10)
    JDK_RS_momentum = JDK_RS_ratio.pct_change(4)
    
    #Normalize the Values considering a 14-days Window (Note: 10 weekdays)
    for ticker in JDK_RS_momentum.columns: 
        JDK_RS_momentum[ticker] = 100 + ((JDK_RS_momentum[ticker] - JDK_RS_momentum[ticker].rolling(rolling_avg_len).mean())/JDK_RS_momentum[ticker].rolling(rolling_avg_len).std() + 1)
    
    #print(JDK_RS_momentum.tail())
    # Rounding and Excluding NA's
    JDK_RS_momentum = JDK_RS_momentum.round(2).dropna()
    
    #Adjust DataFrames to be shown in Monthly terms
    #JDK_RS_ratio = JDK_RS_ratio.reset_index()
    #JDK_RS_ratio['date'] = pd.to_datetime(JDK_RS_ratio['date'], format='%Y-%m-%d')
    #JDK_RS_ratio = JDK_RS_ratio.set_index('date')
    #JDK_RS_ratio = JDK_RS_ratio.resample('M').ffill()

    #... now for JDK_RS Momentum
    #JDK_RS_momentum = JDK_RS_momentum.reset_index()
    #JDK_RS_momentum['date'] = pd.to_datetime(JDK_RS_momentum['date'], format='%Y-%m-%d')
    #JDK_RS_momentum = JDK_RS_momentum.set_index('date')
    #JDK_RS_momentum = JDK_RS_momentum.resample('M').ffill()
    
    log('JDK', logtype='debug')
    log(JDK_RS_ratio.head(), logtype='debug')
    log('Momentum', logtype='debug')
    log(JDK_RS_momentum.head(), logtype='debug')
    
    return [JDK_RS_ratio, JDK_RS_momentum]
    

def load_file_list(directory="./indices/"):
    file_list = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f) and f.endswith('.csv'):
            file_list.append(f)
    return file_list


def load_sectoral_indices(date, sampling, entries=50):
    '''
    We use only the closing values of the sectoral indices right now
    '''
    log('Loading sectoral indices', logtype='debug')
    from pathlib import Path
    
    df = pd.read_csv(os.path.join(index_data_dir, 'Nifty_50.csv'))
    df.rename(columns={'Index Date': 'date', 'Closing Index Value': 'Nifty_50'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df.set_index('date', inplace=True)
    df.index = df.index + pd.Timedelta('9 hour') + pd.Timedelta('15 minute')
    df = df.sort_index()
    df = df.reindex(columns=['Nifty_50'])
    
    frames = [df]
    
    for index in INDICES:
        if index == "Nifty_50":
            continue
        log(f'Loading {index}', logtype='debug')
        s_df = pd.read_csv(os.path.join(index_data_dir, f'{index}.csv'))
        s_df.rename(columns={'Index Date': 'date', 'Closing Index Value': index}, inplace=True)
        s_df['date'] = pd.to_datetime(s_df['date'], format='%d-%m-%Y')
        s_df.set_index('date', inplace=True)
        s_df.index = s_df.index + pd.Timedelta('9 hour') + pd.Timedelta('15 minute')
        s_df = s_df.sort_index()
        s_df = s_df.reindex(columns=[index])
        s_df = s_df[~s_df.index.duplicated(keep='first')]
        
        frames.append(s_df)
    
    df = pd.concat(frames, axis=1)
    df = df[~df.index.duplicated(keep='first')]
    
    if date is not None:
        df = df[:date.strftime('%Y-%m-%d')]
    
    if sampling == 'w':
        df = df.resample('W').last()
        df.index -= to_offset("6D")
    elif sampling == 'M':
        df = df.resample('M').last()

    filemapping = None
    with open(index_map, 'r') as fd:
        filemapping = json.load(fd)
    
    for index, fname in filemapping.items():
        log(f'Loading {index}', logtype='debug')
        s_df = get_index_dataframe(name=index, path=fname, sampling=sampling, online=True, end_date=date)
        if len(s_df) == 0:
            continue
        if sampling == 'w':
            s_df.index = s_df.index.date
        elif sampling == 'M':
            s_df = s_df.resample('M').last()
        
        df = df.join(s_df, how='outer')
    df.index.name = 'date'
    
    return df.tail(entries)


def load_index_members(name):
    members = []
    print(name)
    filemapping = {}
    with open(index_map, 'r') as fd:
        filemapping = json.load(fd)
    if name not in INDICES and name not in filemapping:
        print(f'{name} not in list')
        return members
    with open(os.path.join(member_dir, '{name}.csv'.format(name=name)), 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            members.append(row['Symbol'].strip())
    return members


def save_scatter_plots(rrg_df, sector='unnamed', sampling = 'w', date=datetime.date.today()):
    log(rrg_df, logtype='info')
    JDK_RS_ratio = rrg_df[0]
    JDK_RS_momentum = rrg_df[1]

    create_directory(f'{plotpath}/{date.strftime("%d-%m-%Y")}/{sampling}/')
    # Create the DataFrames for Creating the ScaterPlots
    #Create a Sub-Header to the DataFrame: 'JDK_RS_ratio' -> As later both RS_ratio and RS_momentum will be joint
    JDK_RS_ratio_subheader = pd.DataFrame(np.zeros((1,JDK_RS_ratio.columns.shape[0])),columns=JDK_RS_ratio.columns, dtype=str)
    JDK_RS_ratio_subheader.iloc[0] = 'JDK_RS_ratio'

    JDK_RS_ratio_total = pd.concat([JDK_RS_ratio_subheader, JDK_RS_ratio], axis=0)

    #... same for JDK_RS Momentum
    JDK_RS_momentum_subheader = pd.DataFrame(np.zeros((1,JDK_RS_momentum.columns.shape[0])),columns=JDK_RS_momentum.columns, dtype=str)
    JDK_RS_momentum_subheader.iloc[0] = 'JDK_RS_momentum'

    JDK_RS_momentum_total = pd.concat([JDK_RS_momentum_subheader, JDK_RS_momentum], axis=0)

    #Join both DataFrames
    RRG_df = pd.concat([JDK_RS_ratio_total, JDK_RS_momentum_total], axis=1, sort=True)
    RRG_df = RRG_df.sort_index(axis=1)
    
    #Create a DataFrame Just with the Last Period Metrics for Plotting the Scatter plot
    ##Reduce JDK_RS_ratio to 1 (Last) Period
    JDK_RS_ratio_1P = pd.DataFrame(JDK_RS_ratio.iloc[-1].transpose())
    JDK_RS_ratio_1P = JDK_RS_ratio_1P.rename(columns= {JDK_RS_ratio_1P.columns[0]: 'JDK_RS_ratio'})
    
    ##Reduce JDK_RS_momentum to 1 (Last) Period
    JDK_RS_momentum_1P = pd.DataFrame(JDK_RS_momentum.iloc[-1].transpose())
    JDK_RS_momentum_1P = JDK_RS_momentum_1P.rename(columns= {JDK_RS_momentum_1P.columns[0]: 'JDK_RS_momentum'})
    
    #Joining the 2 Dataframes
    JDK_RS_1P = pd.concat([JDK_RS_ratio_1P,JDK_RS_momentum_1P], axis=1)
    
    ##Reset the Index so the Index's names are in the Scatter
    JDK_RS_1P = JDK_RS_1P.reset_index() 
    order = [1,2,0] # setting column's order
    JDK_RS_1P = JDK_RS_1P[[JDK_RS_1P.columns[i] for i in order]]
    
    ##Create a New Column with the Quadrants Indication
    JDK_RS_1P['Quadrant'] = JDK_RS_1P['index']
    for row in JDK_RS_1P['Quadrant'].index:
        if JDK_RS_1P['JDK_RS_ratio'][row] > 100 and JDK_RS_1P['JDK_RS_momentum'][row] > 100:
            JDK_RS_1P['Quadrant'][row] = 'Leading'
        elif JDK_RS_1P['JDK_RS_ratio'][row] > 100 and JDK_RS_1P['JDK_RS_momentum'][row] < 100:
            JDK_RS_1P['Quadrant'][row] = 'Lagging'
        elif JDK_RS_1P['JDK_RS_ratio'][row] < 100 and JDK_RS_1P['JDK_RS_momentum'][row] < 100:
            JDK_RS_1P['Quadrant'][row] = 'Weakening'
        elif JDK_RS_1P['JDK_RS_ratio'][row] < 100 and JDK_RS_1P['JDK_RS_momentum'][row] > 100:
            JDK_RS_1P['Quadrant'][row] = 'Improving'
    #Scatter Plot
    #scatter = hv.Scatter(JDK_RS_1P, kdims = ['JDK_RS_ratio', 'JDK_RS_momentum'])
    scatter = hv.Scatter(JDK_RS_1P, kdims = ['JDK_RS_momentum'])
    #scatter = JDK_RS_1P.plot.scatter('JDK_RS_ratio', 'JDK_RS_momentum')
    
    ##Colors
    explicit_mapping = {'Leading': 'green', 'Lagging': 'yellow', 'Weakening': 'red', 'Improving': 'blue'}
    
    ##Defining the Charts's Area
    x_max_distance = max(abs(int(JDK_RS_1P['JDK_RS_ratio'].min())-100), int(JDK_RS_1P['JDK_RS_ratio'].max())-100,
                        abs(int(JDK_RS_1P['JDK_RS_momentum'].min())-100), int(JDK_RS_1P['JDK_RS_momentum'].max())-100)
    x_y_range = (100 - 1 - x_max_distance, 100 + 1 + x_max_distance)
    
    ##Plot Joining all together
    scatter = scatter.opts(opts.Scatter(tools=['hover'], height = 500, width=500, size = 10, xlim = x_y_range, ylim = x_y_range,
                                       color = 'Quadrant', cmap=explicit_mapping, legend_position = 'top'))
    
    ##Vertical and Horizontal Lines
    vline = hv.VLine(100).opts(color = 'black', line_width = 1)
    hline = hv.HLine(100).opts(color = 'black', line_width = 1)
    
    #All Together
    
    full_scatter = scatter * vline * hline
    #Let's use the Panel library to be able to save the Table generated
    p = pn.panel(full_scatter)
    p.save(f'{plotpath}/{date.strftime("%d-%m-%Y")}/{sampling}/{sector}_ScatterPlot_1Period.html') 
    
    #For multiple period we need to create a DataFrame with 3-dimensions 
    #-> to do this we create a dictionary and include each DataFrame with the assigned dictionary key being the Index
    indices =  RRG_df.columns.unique()

    multi_df = dict()
    for index in indices:
        #For each of the Index will do the following procedure

        chosen_columns = []
        #This loop is to filter each variable's varlue in the big-dataframe and create a create a single Dataframe
        for column in RRG_df[index].columns:
            chosen_columns.append(RRG_df[index][column])
        joint_table = pd.concat(chosen_columns, axis=1)

        #Change the DataFrame's Header
        new_header = joint_table.iloc[0] 
        joint_table = joint_table[1:] 
        joint_table.columns = new_header
        joint_table = joint_table.loc[:,~joint_table.columns.duplicated()]

        #Remove the first 3 entries
        joint_table = joint_table[2:]

        #Create a column for the Index
        joint_table['index'] = index

        ##Reset the Index so the Datess are observable the Scatter
        joint_table = joint_table.reset_index()
        order = [1,2,3,0] # setting column's order
        joint_table = joint_table[[joint_table.columns[i] for i in order]]
        joint_table = joint_table.rename(columns={"level_0": "Date"})
        joint_table['Date'] = joint_table['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))

        ##Create a New Column with the Quadrants Indication
        joint_table['Quadrant'] = joint_table['index']
        for row in joint_table['Quadrant'].index:
            if joint_table['JDK_RS_ratio'][row] >= 100 and joint_table['JDK_RS_momentum'][row] >= 100:
                joint_table['Quadrant'][row] = 'Leading'
            elif joint_table['JDK_RS_ratio'][row] >= 100 and joint_table['JDK_RS_momentum'][row] <= 100:
                joint_table['Quadrant'][row] = 'Lagging'
            elif joint_table['JDK_RS_ratio'][row] <= 100 and joint_table['JDK_RS_momentum'][row] <= 100:
                joint_table['Quadrant'][row] = 'Weakening'
            elif joint_table['JDK_RS_ratio'][row] <= 100 and joint_table['JDK_RS_momentum'][row] >= 100:
                joint_table['Quadrant'][row] = 'Improving'

        #Joining the obtained Single Dataframes into the Dicitonary
        multi_df.update({index: joint_table})  
    #Defining the Charts's Area
    x_y_max = []
    for Index in multi_df.keys():
        x_y_max_ = max(abs(int(multi_df[Index]['JDK_RS_ratio'].min())-100), int(multi_df[Index]['JDK_RS_ratio'].max())-100,
                        abs(int(multi_df[Index]['JDK_RS_momentum'].min())-100), int(multi_df[Index]['JDK_RS_momentum'].max())-100)
        x_y_max.append(x_y_max_)

    x_range = (100 - 1 - max(x_y_max), 100 + 1 + max(x_y_max))
    y_range = (100 - 1 - max(x_y_max), 100 + 1.25 + max(x_y_max))
    #Note: y_range has .25 extra on top because legend stays on top and option "legend_position" doesn't exist for Overlay graphs

    indices_name = RRG_df.columns.drop_duplicates().tolist()

    #Include Dropdown List
    def load_indices(Index): 
        #scatter = hv.Scatter(multi_df[Index], kdims = ['JDK_RS_ratio', 'JDK_RS_momentum'])
        scatter = hv.Scatter(multi_df[Index], kdims = ['JDK_RS_momentum'])
    
        ##Colors
        explicit_mapping = {'Leading': 'green', 'Lagging': 'yellow', 'Weakening': 'red', 'Improving': 'blue'}
        ##Plot Joining all together
        scatter = scatter.opts(opts.Scatter(tools=['hover'], height = 500, width=500, size = 10, xlim = x_range, ylim = y_range,
                                            color = 'Quadrant', cmap=explicit_mapping,
                                           ))
    
        ##Line connecting the dots
        #curve = hv.Curve(multi_df[Index], kdims = ['JDK_RS_ratio', 'JDK_RS_momentum'])
        curve = hv.Curve(multi_df[Index], kdims = [ 'JDK_RS_momentum'])
        curve = curve.opts(opts.Curve(color = 'black', line_width = 1))
    
        ##Vertical and Horizontal Lines
        vline = hv.VLine(100).opts(color = 'black', line_width = 1)
        hline = hv.HLine(100).opts(color = 'black', line_width = 1)    
    
    
        #All Together
    
        full_scatter = scatter * vline * hline * curve
        full_scatter = full_scatter.opts(legend_cols= False)
    
        return full_scatter
    #Instantiation the Dynamic Map object
    dmap = hv.DynamicMap(load_indices, kdims='Index').redim.values(Index=indices_name)
    
    #Let's use the Panel library to be able to save the Table generated
    p = pn.panel(dmap)
    p.save(f'{plotpath}/{date.strftime("%d-%m-%Y")}/{sampling}/{sector}_ScatterPlot_Multiple_Period.html', embed = True) 
    
def generate_report(sector, rrg_df, verbose=False):
    rstrength = rrg_df[0]
    rmomentum = rrg_df[1]
    origin = [100,100]
    if verbose:
        if len(rstrength) >0:
            for col in rstrength:
                if rstrength.iloc[-1][col] > 100 and len(rmomentum) >0 and rmomentum.iloc[-1][col] > 100:
                    print(f'{col} is leading [RS:{rstrength.iloc[-1][col]} MOM:{rmomentum.iloc[-1][col]}]')
                elif rstrength.iloc[-1][col] < 100 and len(rmomentum) >0 and rmomentum.iloc[-1][col] > 100:
                    print(f'{col} is improving [RS:{rstrength.iloc[-1][col]} MOM:{rmomentum.iloc[-1][col]}]')
                elif rstrength.iloc[-1][col] < 100 and len(rmomentum) >0 and rmomentum.iloc[-1][col] < 100:
                    print(f'{col} is weakening [RS:{rstrength.iloc[-1][col]} MOM:{rmomentum.iloc[-1][col]}]')
                elif rstrength.iloc[-1][col] > 100 and len(rmomentum) >0 and rmomentum.iloc[-1][col] < 100:
                    print(f'{col} is lagging [RS:{rstrength.iloc[-1][col]} MOM:{rmomentum.iloc[-1][col]}]')
                elif len(rmomentum)==0:
                    print(f'{sector} has NaN values')
                else:
                    print(f'{col}')
        else:
            print(f'{sector} has NaN values in ratio')

    #Create a leaderboard: Sort according to the distance from 0 in the first quadrant. We want the entries
    # with the greatest momentum and strength to be rated higher than the ones with greater momentum but lesser strength
    
    #First, get the last values of all members as the first column of a dataframe
    r_df = rstrength.iloc[[-1]].transpose()
    m_df = rmomentum.iloc[[-1]].transpose()

    r_df.rename(columns={list(r_df.columns)[0]: 'strength'}, inplace=True)
    r_df.index.names = ['member']
    m_df.rename(columns={list(m_df.columns)[0]: 'momentum'}, inplace=True)
    m_df.index.names = ['member']
    df = pd.concat([r_df, m_df], axis='columns', join='inner')
    # Convert to polar coordinates
    df['radius'] = np.sqrt((df['strength']-origin[0])**2 + (df['momentum']-origin[1])**2)
    df['angle'] = np.arctan2(df['strength']-origin[1], df['momentum']-origin[0])
    # Adjust negative angles to be positive
    df['angle'] = np.where(df['angle'] < 0, 2*np.pi + df['angle'], df['angle'])
    # Find the leaders and sort
    first_quadrant = df[(df['angle'] >= 0) & (df['angle'] <= np.pi/2) & (df['radius'] >= 0)]
    sorted_first_quadrant = first_quadrant.sort_values(by='radius', ascending=False)

    # Display the sorted DataFrame
    if len(sorted_first_quadrant)>0:
        print('====================\n| Leaders\n====================')
        print(sorted_first_quadrant)

    #Find the ones improving and sort
    fourth_quadrant = df[(df['angle'] >= (3/2)*np.pi) & (df['angle'] <= 2*np.pi) & (df['radius'] >= 0)]

    # Sort by distance from the origin
    sorted_fourth_quadrant = fourth_quadrant.sort_values(by='radius', ascending=False)

    # Display the sorted DataFrame for the fourth quadrant
    if len(sorted_fourth_quadrant)>0:
        print('====================\n| Improving\n====================')
        print(sorted_fourth_quadrant)

    #Now, we want to report the relative rotations of various stocks. This is in terms of both change 
    # in radius as well as angle.
    # r_df = rstrength.diff(periods=1).iloc[[-1]].transpose()
    # m_df = rmomentum.diff(periods=1).iloc[[-1]].transpose()
    # r_df.rename(columns={list(r_df.columns)[0]: 'strength'}, inplace=True)
    # m_df.rename(columns={list(m_df.columns)[0]: 'momentum'}, inplace=True)
    # df = pd.concat([r_df, m_df], axis='columns', join='inner')
    
def main(date=datetime.date.today(), sampling = 'w', online=True):
    try:
        os.mkdir(cache_dir)
    except FileExistsError:
        pass
    except:
        print('Error creating folder')

    processed = load_progress()

    df = load_sectoral_indices(date, sampling, entries=33)
    print(df.head())
    df = df.copy()
    benchmark = 'Nifty_50'
    jdf_df = compute_jdk(benchmark=benchmark, base_df = df)
    if 'Nifty_50' not in processed:
        save_scatter_plots(jdf_df, benchmark, sampling, date)
        generate_report(benchmark, jdf_df)
        save_progress('Nifty_50', state='success')
    #Whichever sectors are leading, find the strongest stock in those
    for column in jdf_df[0].columns:
        #if JDK_RS_ratio.iloc[-1][column] > 100 and JDK_RS_momentum.iloc[-1][column] > 100:
        if column in processed:
            print(f'Skip {column}. Already processed for the day')
            continue
        members = load_index_members(column)
        if len(members) < 2:
            save_progress(column, state='skipped')
            continue
        w_df = load_members(sector=column, sector_df= df[column].to_frame(), members=members, date=date, sampling=sampling, entries=33, online=online)
        try:
            result = compute_jdk(benchmark=column, base_df = w_df)
            if result is None:
                log(f'Error computing JDK for {column} sector', logtype='error')
                save_progress(column, state='failed')
                continue
            try:
                save_scatter_plots(result, column, sampling, date)
            except:
                log(f'Error saving plots for {column}', logtype='error')
                print(traceback.format_exc())
            try:
                generate_report(column, result)
            except:
                log(f'Error saving reports for {column}', logtype='error')
                print(traceback.format_exc())
            save_progress(column, state='success')
        except:
            log(f'Error computing JDK for {column} sector', logtype='error')
            save_progress(column, state='failed')
            print(traceback.format_exc())

if __name__ == "__main__":
    day = datetime.date.today()
    loglevel = 'info'
    set_loglevel(loglevel)
    import argparse
    parser = argparse.ArgumentParser(description='Compute RRG data for indices')
    parser.add_argument('-d', '--daily', action='store_true', default = False, help="Compute RRG on daily TF")
    parser.add_argument('-w', '--weekly', action='store_true', default = True, help="Compute RRG on weekly TF")
    parser.add_argument('-m', '--monthly', action='store_true', default = False, help="Compute RRG on monthly TF")
    parser.add_argument('-o', '--online', action='store_true', default = False, help="Fetch data from TradingView (Online)")
    parser.add_argument('-f', '--for', dest='date', help="Compute RRG for date")
    parser.add_argument('-n', '--nodownload', dest='download', action="store_false", default=True, help="Do not attempt download of indices")
    parser.add_argument('-r', '--refresh', dest='refresh', action="store_true", default=False, help="Refresh index constituents files")
    #Can add options for weekly sampling and monthly sampling later
    args = parser.parse_args()
    stock_code = None
    sampling = 'w'
    if args.daily:
        sampling='d'
        log('Daily sampling')
    elif args.monthly:
        sampling='M'
        log('Monthly sampling')
    if args.date is not None and len(args.date)>0:
        log(logtype='info', args = 'Get data for date: {}'.format(args.date))
        day = datetime.datetime.strptime(args.date, "%d/%m/%y")
    if args.online:
        log(logtype='info', args = 'Online mode: will try to download data when required')
    else:
        log(logtype='info', args = 'Offline mode: will use stored data')

    pd.set_option("display.precision", 8)
    pd.options.mode.chained_assignment = None  # default='warn'
    if args.refresh:
        log('Refreshing index constituents', logtype='info')
        download_index_constituents(overwrite=True)

    if args.download is True:
        log('Download index reports', logtype='debug')
        silent = True if loglevel != 'debug' else False
        download_historical_index_reports(day, silent=silent)
    
    main(date=day, sampling=sampling, online=args.online)
    
