
import os
import csv
import pandas as pd
import numpy as np
from pandas.tseries.frequencies import to_offset
import datetime

from stocks.models import Stock, Market
from lib.tradingview import Interval, get_tvfeed_instance
from lib.retrieval import get_stock_listing
import init
from django.conf import settings
from lib.cache import cached
from lib.logging import log
from lib.misc import get_requests_headers
import requests
import pytz

index_data_dir = settings.PROJECT_DIRS['reports']
member_dir = index_data_dir+'/members/'
plotpath = index_data_dir+'/plots/'
download_path = os.path.join(index_data_dir, "daily")

url_base_path = "https://archives.nseindia.com/content/indices/ind_close_all_{date}.csv"

fields = ['Index Name', 'Index Date', 'Open Index Value', 
              'High Index Value', 'Low Index Value', 'Closing Index Value',
              'Points Change', 'Change(%)', 'Volume', 'Turnover (Rs. Cr.)',
              'P/E', 'P/B', 'Div Yield']
replacement_symbols = ['-', '/', ' ', ':', '(', ')', '%']


NSE_INDEX_URLS = {
        "Nifty_50": {'url':"https://niftyindices.com/IndexConstituent/ind_nifty50list.csv",
                     'base': "https://niftyindices.com/indices/equity/broad-based-indices/NIFTY-50"},
        "Nifty_Auto": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyautolist.csv",
                       'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-auto"},
        "Nifty_Bank": {'url':"https://niftyindices.com/IndexConstituent/ind_niftybanklist.csv",
                       'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-bank"},
        "Nifty_Energy": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyenergylist.csv",
                         'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-energy"},
        "Nifty_Financial_Services": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyfinancelist.csv",
                                     'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-financial-services"},
        "Nifty_FMCG": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyfmcglist.csv",
                       'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-fmcg"},
        "Nifty_IT": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyitlist.csv",
                     'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-it"},
        "Nifty_Media": {'url':"https://niftyindices.com/IndexConstituent/ind_niftymedialist.csv",
                        'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-media"},
        "Nifty_Metal": {'url':"https://niftyindices.com/IndexConstituent/ind_niftymetallist.csv",
                        'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-metal"},
        "Nifty_MNC": {'url':"https://niftyindices.com/IndexConstituent/ind_niftymnclist.csv",
                      'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-mnc"},
        "Nifty_Pharma": {'url':"https://niftyindices.com/IndexConstituent/ind_niftypharmalist.csv",
                         'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-pharma"},
        "Nifty_PSU_Bank": {'url':"https://niftyindices.com/IndexConstituent/ind_niftypsubanklist.csv",
                           'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-psu-bank"},
        "Nifty_Realty": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyrealtylist.csv",
                         'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-realty"},
        "Nifty_India_Consumption": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyconsumptionlist.csv",
                                    'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-india-consumption"},
        "Nifty_Commodities": {'url':"https://niftyindices.com/IndexConstituent/ind_niftycommoditieslist.csv",
                              'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-commodities"},
        "Nifty_Infrastructure": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyinfralist.csv",
                                 'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-infrastructure"},
        "Nifty_PSE": {'url':"https://niftyindices.com/IndexConstituent/ind_niftypselist.csv",
                      'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-pse"},
        "Nifty_Services_Sector": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyservicelist.csv",
                                  'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-services-sector"},
        "Nifty_REITs_&_InvITs": {"url":"https://niftyindices.com/IndexConstituent/ind_niftyREITs_InvITs_list.csv",
                               "base":"https://niftyindices.com/indices/equity/thematic-indices/nifty-reits-invits"},
        "Nifty_Growth_Sectors_15": {'url':"https://niftyindices.com/IndexConstituent/ind_NiftyGrowth_Sectors15_Index.csv",
                                    'base': "https://niftyindices.com/indices/equity/strategy-indices/nifty-growth-sectors-15"},
        # "NIFTY_SME_EMERGE": {'url':"https://niftyindices.com/IndexConstituent/ind_niftysmelist.csv",
        #                      'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-sme-emerge"},
        "Nifty_Oil_&_Gas": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyoilgaslist.csv",
                            'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-oil-and-gas-index"},
        "Nifty_Healthcare_Index": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyhealthcarelist.csv",
                                   'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-healthcare-index"},
        "Nifty_Total_Market": {'url':"https://niftyindices.com/IndexConstituent/ind_niftytotalmarket_list.csv",
                               'base': "https://niftyindices.com/indices/equity/broad-based-indices/nifty-total-market"},
        "Nifty_India_Digital": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyindiadigital_list.csv",
                                'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-india-digital"},
        "Nifty_Mobility": {'url':"https://niftyindices.com/IndexConstituent/ind_niftymobility_list.csv",
                           'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-mobility"},
        "Nifty_India_Defence": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyindiadefence_list.csv",
                                'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-india-defence"},
        "Nifty_Financial_Services_Ex_Bank": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyfinancialservicesexbank_list.xlsx",
                                             'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-financial-services-ex-bank"},
        "Nifty_Core_Housing": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyCoreHousing_list.csv",
                               'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-core-housing"},
        "Nifty_Housing": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyhousing_list.csv",
                          'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-housing"},
        "Nifty_Transportation_&_Logistics": {'url':"https://niftyindices.com/IndexConstituent/ind_niftytransportationandlogistics%20_list.csv",
                                             'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-transportation-logistics"},
        "Nifty_MidSmall_Financial_Services": {'url':"https://niftyindices.com/IndexConstituent/ind_niftymidsmallfinancailservice_list.csv",
                                              'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-midsmall-financial-services"},
        "Nifty_MidSmall_Healthcare": {'url':"https://niftyindices.com/IndexConstituent/ind_niftymidsmallhealthcare_list.csv",
                                      'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-midsmall-healthcare"},
        "Nifty_MidSmall_IT_&_Telecom": {'url':"https://niftyindices.com/IndexConstituent/ind_niftymidsmallitAndtelecom_list.csv",
                                        'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-midsmall-it-telecom"},
        "Nifty_Consumer_Durables": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyconsumerdurableslist.csv",
                                    'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-consumer-durables-index"},
        "Nifty_Non_Cyclical_Consumer": {'url':"https://niftyindices.com/IndexConstituent/ind_niftynon-cyclicalconsumer_list.csv",
                                        'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-non-cyclical-consumer"},
        "Nifty_India_Manufacturing": {'url':"https://niftyindices.com/IndexConstituent/ind_niftyindiamanufacturing_list.csv",
                                      'base': "https://niftyindices.com/indices/equity/thematic-indices/nifty-india-manufacturing"},
        #"Nifty_Next_50": "",
        #"Nifty_100": "",
        #"Nifty_200": "",
        #"Nifty_500": "",
        #"Nifty_Midcap_50": "",
        #"NIFTY_Midcap_100": "",
        #"NIFTY_Smallcap_100": "",
        "Nifty_Dividend_Opportunities_50": {'url':"https://niftyindices.com/IndexConstituent/ind_niftydivopp50list.csv",
                                            'base': "https://niftyindices.com/indices/equity/strategy-indices/nifty-dividend-opportunities-50"},
        #"Nifty_Low_Volatility_50": "",
        #"Nifty_Alpha_50": "",
        #"Nifty_High_Beta_50": "",
        #"Nifty100_Equal_Weight": "",
        #"Nifty100_Liquid_15": "",
        #"Nifty_CPSE": "",
        #"Nifty50_Value_20": "",
        #"Nifty_Midcap_Liquid_15": "",
        #"NIFTY100_Quality_30": "",
        "Nifty_Private_Bank": {'url':"https://niftyindices.com/IndexConstituent/ind_nifty_privatebanklist.csv",
                               'base': "https://niftyindices.com/indices/equity/sectoral-indices/nifty-private-bank"},
        "Nifty_Smallcap_250": {'url':"https://niftyindices.com/IndexConstituent/ind_niftysmallcap250list.csv",
                               'base': "https://niftyindices.com/indices/equity/broad-based-indices/nifty-smallcap-250"},
        "Nifty_Smallcap_50": {'url':"https://niftyindices.com/IndexConstituent/ind_niftysmallcap50list.csv",
                              'base': "https://niftyindices.com/indices/equity/broad-based-indices/niftysmallcap50"},
        "Nifty_MidSmallcap_400": {'url':"https://niftyindices.com/IndexConstituent/ind_niftymidsmallcap400list.csv",
                                  'base': "https://niftyindices.com/indices/equity/broad-based-indices/nifty-midsmallcap-400"},
        "Nifty_Midcap_150": {'url':"https://niftyindices.com/IndexConstituent/ind_niftymidcap150list.csv",
                             'base': "https://niftyindices.com/indices/equity/broad-based-indices/nifty-midcap-150"},
        "Nifty_Midcap_Select": {'url':"https://niftyindices.com/IndexConstituent/ind_niftymidcapselect_list.csv",
                                'base': "https://niftyindices.com/indices/equity/broad-based-indices/nifty-midcap-select-index"},
        "NIFTY_LargeMidcap_250": {'url':"https://niftyindices.com/IndexConstituent/ind_niftylargemidcap250list.csv",
                                  'base': "https://niftyindices.com/indices/equity/broad-based-indices/nifty-largemidcap-250"},
        #"Nifty_Financial_Services_25_50": "",
        #"Nifty500_Multicap_50_25_25": "",
        "Nifty_Microcap_250": {'url':"https://niftyindices.com/IndexConstituent/ind_niftymicrocap250_list.csv",
                               'base': "https://niftyindices.com/indices/equity/broad-based-indices/nifty-microcap-250"},
        #"Nifty200_Momentum_30": "",
        #"NIFTY100_Alpha_30": "",
        #"NIFTY500_Value_50": "",
        #"Nifty100_Low_Volatility_30": "",
        #"NIFTY_Alpha_Low_Volatility_30": "",
        #"NIFTY_Quality_Low_Volatility_30": "",
        #"NIFTY_Alpha_Quality_Low_Volatility_30": "",
        #"NIFTY_Alpha_Quality_Value_Low_Volatility_30": "",
        #"NIFTY200_Quality_30": "",
        #"NIFTY_Midcap150_Quality_50": "",
        #"Nifty200_Alpha_30": "",
        #"Nifty_Midcap150_Momentum_50": "",
        #"NIFTY50_Equal_Weight": "",
    }

INDICES = {"NIFTY 50":"Nifty_50",
           "NIFTY AUTO":"Nifty_Auto",
           "NIFTY BANK":"Nifty_Bank",
           "NIFTY ENERGY": "Nifty_Energy",
           "NIFTY FINANCIAL SERVICES": "Nifty_Financial_Services",
           "NIFTY FMCG": "Nifty_FMCG",
           "NIFTY IT": "Nifty_IT",
           "NIFTY MEDIA": "Nifty_Media",
           "NIFTY METAL": "Nifty_Metal",
           "NIFTY MNC": "Nifty_MNC",
           "NIFTY PHARMA": "Nifty_Pharma",
           "NIFTY PSU BANK": "Nifty_PSU_Bank",
           "NIFTY REALTY": "Nifty_Realty",
           "NIFTY INDIA CONSUMPTION": "Nifty_India_Consumption",
           "NIFTY COMMODITIES": "Nifty_Commodities",
           "NIFTY INFRASTRUCTURE": "Nifty_Infrastructure",
           "NIFTY PSE": "Nifty_PSE",
           "NIFTY SERVICES SECTOR": "Nifty_Services_Sector",
           "NIFTY GROWTH SECTORS 15": "Nifty_Growth_Sectors_15",
           #"NIFTY SME EMERGE": "NIFTY_SME_EMERGE",
           "NIFTY OIL & GAS": "Nifty_Oil_&_Gas",
           "NIFTY HEALTHCARE INDEX": "Nifty_Healthcare_Index",
           "NIFTY TOTAL MARKET": "Nifty_Total_Market",
           "NIFTY INDIA DIGITAL": "Nifty_India_Digital",
           "NIFTY MOBILITY": "Nifty_Mobility",
           "NIFTY INDIA DEFENCE": "Nifty_India_Defence",
           "NIFTY FINANCIAL SERVICES EX BANK": "Nifty_Financial_Services_Ex_Bank",
           "NIFTY HOUSING": "Nifty_Housing",
           "NIFTY TRANSPORTATION & LOGISTICS": "Nifty_Transportation_&_Logistics",
           "NIFTY MIDSMALL FINANCIAL SERVICES": "Nifty_MidSmall_Financial_Services",
           "NIFTY MIDSMALL HEALTHCARE": "Nifty_MidSmall_Healthcare",
           "NIFTY MIDSMALL IT & TELECOM": "Nifty_MidSmall_IT_&_Telecom",
           "NIFTY CONSUMER DURABLES": "Nifty_Consumer_Durables",
           "NIFTY NON CYCLICAL CONSUMER": "Nifty_Non_Cyclical_Consumer",
           "NIFTY INDIA MANUFACTURING": "Nifty_India_Manufacturing",
           "NIFTY NEXT 50": "Nifty_Next_50",
           "NIFTY 100": "Nifty_100",
           "NIFTY 200": "Nifty_200",
           "NIFTY 500": "Nifty_500",
           "NIFTY MIDCAP 50": "Nifty_Midcap_50",
           "NIFTY MIDCAP 100": "NIFTY_Midcap_100",
           "NIFTY SMALLCAP 100": "NIFTY_Smallcap_100",
           "NIFTY100 EQUAL WEIGHT": "Nifty100_Equal_Weight",
           "NIFTY100 LIQUID 15": "Nifty100_Liquid_15",
           "NIFTY CPSE": "Nifty_CPSE",
           "NIFTY50 VALUE 20": "Nifty50_Value_20",
           "NIFTY MIDCAP LIQUID 15": "Nifty_Midcap_Liquid_15",
           "NIFTY100 QUALITY 30": "NIFTY100_Quality_30",
           "NIFTY PRIVATE BANK": "Nifty_Private_Bank",
           "NIFTY SMALLCAP 250": "Nifty_Smallcap_250",
           "NIFTY SMALLCAP 50": "Nifty_Smallcap_50",
           "NIFTY MIDSMALLCAP 400": "Nifty_MidSmallcap_400",
           "NIFTY MIDCAP 150": "Nifty_Midcap_150",
           "NIFTY MIDCAP SELECT": "Nifty_Midcap_Select",
           "NIFTY LARGEMIDCAP 250": "NIFTY_LargeMidcap_250",
           "NIFTY FINANCIAL SERVICES 25 50": "Nifty_Financial_Services_25_50",
           "NIFTY500 MULTICAP 50 25 25": "Nifty500_Multicap_50_25_25",
           "NIFTY MICROCAP 250": "Nifty_Microcap_250",
           "NIFTY200 MOMENTUM 30": "Nifty200_Momentum_30",
           "NIFTY100 ALPHA 30": "NIFTY100_Alpha_30",
           "NIFTY500 VALUE 50": "NIFTY500_Value_50",
           "NIFTY100 LOW VOLATILITY 30": "Nifty100_Low_Volatility_30",
           "NIFTY ALPHA LOW VOLATILITY 30": "NIFTY_Alpha_Low_Volatility_30",
           "NIFTY QUALITY LOW VOLATILITY 30": "NIFTY_Quality_Low_Volatility_30",
           "NIFTY ALPHA QUALITY LOW VOLATILITY 30": "NIFTY_Alpha_Quality_Low_Volatility_30",
           "NIFTY ALPHA QUALITY VALUE LOW VOLATILITY 30": "NIFTY_Alpha_Quality_Value_Low_Volatility_30",
           "NIFTY200 QUALITY 30": "NIFTY200_Quality_30",
           "NIFTY MIDCAP150 QUALITY 50": "NIFTY_Midcap150_Quality_50",
           "NIFTY200 ALPHA 30": "Nifty200_Alpha_30",
           "NIFTY MIDCAP150 MOMENTUM 50": "Nifty_Midcap150_Momentum_50",
           "NIFTY50 EQUAL WEIGHT": "NIFTY50_Equal_Weight"
        }


def download_index_report(day, silent=False):
    filepath = os.path.join(download_path,'ind_close_all_{date}.csv'.format(date=day.strftime("%d%m%Y")))
    if os.path.isfile(filepath):
        if not silent:
            print(f'File: {filepath} exists. Skip download')
        return filepath
    url = url_base_path.format(date=day.strftime("%d%m%Y"))
    headers = get_requests_headers()
    headers.update({
            "host": "www.nseindia.com",
            "referer": "https://www.nseindia.com/all-reports",
            "authority": "www.nseindia.com",
            })

    try:
        session = requests.Session()
        session.headers.update(headers)
        response = session.get('https://www.nseindia.com/all-reports')
        session.headers.update({'host': "archives.nseindia.com"})
        response = session.get(url)
        response.raise_for_status()
        open(filepath, 'wb').write(response.content)
    except Exception as e:
        print (f'ERR:: Exception occurred while fetching data for day: {day}')
        if not silent:
            print(e)
        return False
    
    return filepath

def download_historical_index_reports(day, silent=False):
    '''
    Will download past 52 weeks data. That's 52*5 calls
    '''
    
    files = []
    
    for delta in range(0, 365):
        download_date = day - datetime.timedelta(days=delta)
        if download_date.weekday() in [5,6]:
            continue
        f = download_index_report(download_date, silent)
        if f is not False:
            files.append(f)
    reports = {}
    for report in files:
        with open(report) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                index = row['Index Name'].strip()
                for s in replacement_symbols:
                    index = index.replace(s, '_')
                if index not in reports:
                    reports[index] = []
                reports[index].append(row)
    for index in reports:
        with open(os.path.join(index_data_dir,index+'.csv'), 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            for r in reports[index]:
                writer.writerow(r)

def update_index_report(day, silent=False):
    filepath = download_path+'ind_close_all_{date}.csv'.format(date=day.strftime("%d%m%Y"))
    reports = {}
    
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            index = row['Index Name'].strip()
            for s in replacement_symbols:
                index = index.replace(s, '_')
            if index not in reports:
                reports[index] = []
            reports[index].append(row)
    for index in reports:
        with open(index_data_dir+index+'.csv', 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            for r in reports[index]:
                writer.writerow(r)


def load_index_members(sector, members, date=datetime.datetime.now(), interval=Interval.in_weekly, 
                        entries=50, online=True, start_date=None, end_date=None, market='NSE', drop_columns=['open', 'high', 'low', 'volume']):
    
    def resample(df, interval):
        #df_offset_str = '09h15min'
        logic = {'open'  : 'first',
                 'high'  : 'max',
                 'low'   : 'min',
                 'close' : 'last',
                 'volume': 'sum',
                 'delivery': 'sum',
                 'trades': 'sum'}
        int_val = None
        try:
            int_val = int(interval)
            int_val = f'{interval}min'
        except:
            int_val = interval

        #df = df.resample(interval.value, offset=df_offset_str).apply(logic).dropna()
        df = df.resample(interval.value).apply(logic).dropna()
        return df
    
    log('========================', 'debug')
    log(f'Loading for {sector}', 'debug')
    log('========================', 'debug')

    username = 'AnshulBot'
    password = '@nshulthakur123'
    tv = None
    if not online:
        if interval.to_days()<1.0:
            online = True
    if online:
        tv = get_tvfeed_instance(username, password)
        #print(duration, type(duration))
    df = None 

    pacific = pytz.timezone('US/Pacific')
    india = pytz.timezone('Asia/Calcutta')
    s_list = []
    skipped = []

    duration = entries * interval.to_days()
    for stock in members:
        try:
            if not online:
                if ':' in stock:
                    market = stock.split(':')[0]
                    stock = stock.split(':')[1]
                stock_obj = Stock.objects.get(symbol=stock, market=Market.objects.get(name=market))
                s_df = get_stock_listing(stock_obj, duration=duration, last_date = date)
                s_df = resample(s_df, interval)
                drop_columns = drop_columns + ['delivery', 'trades']
                s_df = s_df.drop(columns = drop_columns)
                #print(s_df.head())
                if len(s_df)==0:
                    skipped.append(stock_obj.symbol)
                    continue
                s_df.reset_index(inplace = True)
                s_df.rename(columns={'close': stock,
                                     'date': 'datetime'},
                            inplace = True)
                s_df['datetime'] = pd.to_datetime(s_df['datetime'], format='%d-%m-%Y %H:%M:%S')
                s_df.set_index('datetime', inplace = True)
                s_df = s_df.sort_index()
                s_df = s_df.reindex(columns = [stock])
                s_df = s_df[~s_df.index.duplicated(keep='first')]
                if start_date is not None and end_date is not None:
                    s_df = s_df.loc[pd.to_datetime(start_date).date():pd.to_datetime(end_date).date()]
                s_list.append(s_df)
            else:
                symbol = stock.strip().replace('&', '_')
                symbol = symbol.replace('-', '_')
                symbol = symbol.split(':')[-1]
                nse_map = {'UNITDSPR': 'MCDOWELL_N',
                           'MOTHERSUMI': 'MSUMI'}
                if symbol in nse_map:
                    symbol = nse_map[symbol]
                
                s_df = cached(name=symbol, timeframe=interval)
                if s_df is not None:
                    pass
                else:
                    s_df = tv.get_hist(
                                symbol,
                                market,
                                interval=interval,
                                n_bars=entries,
                                extended_session=False,
                            )
                    if s_df is not None:
                        cached(name=symbol, df=s_df, timeframe=interval)
                if s_df is None:
                    log(f'Error fetching information on {symbol}', 'warning')
                else:
                    s_df = s_df.drop(columns = drop_columns)
                    #print(s_df.head())
                    if len(s_df)==0:
                        log('Skip {}'.format(symbol), 'info')
                        continue
                    s_df.reset_index(inplace = True)
                    s_df.rename(columns={'close': stock},
                               inplace = True)
                    #print(s_df.columns)
                    #pd.to_datetime(df['DateTime']).dt.date
                    s_df['datetime'] = pd.to_datetime(s_df['datetime'], format='%d-%m-%Y %H:%M:%S')
                    #s_df.drop_duplicates(inplace = True, subset='date')
                    s_df.set_index('datetime', inplace = True)
                    s_df.index = s_df.index.tz_localize(pacific).tz_convert(india).tz_convert(None)
                    s_df = s_df.sort_index()
                    s_df = s_df.reindex(columns = [stock])
                    s_df = s_df[~s_df.index.duplicated(keep='first')]
                    #print(s_df.index.values[0], type(s_df.index.values[0]))
                    if start_date is not None and end_date is not None:
                        #print(pd.to_datetime(start_date).date(), type(pd.to_datetime(start_date).date()))
                        s_df = s_df.loc[pd.to_datetime(start_date).date():pd.to_datetime(end_date).date()]
                    #print(s_df.loc[start_date:end_date])
                    #print(s_df.head(10))
                    #print(s_df[s_df.index.duplicated(keep=False)])
                    s_list.append(s_df)
                    #df[stock] = s_df[stock]
        except Stock.DoesNotExist:
            log(f'{stock} values do not exist', 'error')
        except Market.DoesNotExist:
            log(f'{market} does not exist as Market', 'error')
    df = pd.concat(s_list, axis='columns')
    df = df[~df.index.duplicated(keep='first')]
    df.sort_index(inplace=True)
    #print(df.head(10))
    log(f'Skiped {skipped}', 'info')
    return df

def load_members(sector, members, date, sampling=Interval.in_weekly, entries=50, online=True):
    print('========================')
    print(f'Loading for {sector}')
    print('========================')
    
    df = pd.read_csv(f'{index_data_dir}{INDICES[sector]}.csv')
    df.rename(columns={'Index Date': 'date',
                    'Closing Index Value': INDICES[sector]},
            inplace = True)
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
    df.set_index('date', inplace = True)
    df = df.sort_index()
    df = df.reindex(columns = [INDICES[sector]])
    df = df[~df.index.duplicated(keep='first')]
    
    if date is not None:
        df = df[:date.strftime('%Y-%m-%d')]
    if sampling.value =='1W':
        #Resample weekly
        logic = {}
        for cols in df.columns:
            if cols != 'date':
                logic[cols] = 'last'
        #Resample on weekly levels
        df = df.resample('W').apply(logic)
        #df = df.resample('W-FRI', closed='left').apply(logic)
        df.index -= to_offset("6D")
    #Truncate to last n days
    df = df.iloc[-entries:]
    #print(df.head(10))
    #print(date)
    start_date = df.index.values[0]
    end_date = df.index.values[-1]
    #print(start_date, type(start_date))

    #print(np.datetime64(date))
    duration = np.datetime64(datetime.datetime.today())-start_date
    if sampling.value=='1W':
        duration = duration.astype('timedelta64[W]')/np.timedelta64(1, 'W')
    else:
        duration = duration.astype('timedelta64[D]')/np.timedelta64(1, 'D')
    
    duration = max(int(duration.astype(int))+1, entries)

    username = 'AnshulBot'
    password = '@nshulthakur123'
    tv = None
    interval = sampling
    if online:
        tv = get_tvfeed_instance(username, password)
    #print(duration, type(duration))
    for stock in members:
        try:
            if not online:
                stock_obj = Stock.objects.get(sid=stock)
                s_df = get_stock_listing(stock_obj, duration=duration, last_date = date)
                s_df = s_df.drop(columns = ['open', 'high', 'low', 'volume', 'delivery', 'trades'])
                #print(s_df.head())
                if len(s_df)==0:
                    print('Skip {}'.format(stock_obj))
                    continue
                s_df.rename(columns={'close': stock},
                           inplace = True)
                s_df.reset_index(inplace = True)
                s_df['date'] = pd.to_datetime(s_df['date'], format='%d-%m-%Y')
                #s_df.drop_duplicates(inplace = True, subset='date')
                s_df.set_index('date', inplace = True)
                s_df = s_df.sort_index()
                s_df = s_df.reindex(columns = [stock])
                s_df = s_df[~s_df.index.duplicated(keep='first')]
                #print(s_df[s_df.index.duplicated(keep=False)])
                s_df = s_df.loc[pd.to_datetime(start_date).date():pd.to_datetime(end_date).date()]
                df[stock] = s_df[stock]
            else:
                print(stock)
                symbol = stock.strip().replace('&', '_')
                symbol = symbol.replace('-', '_')
                nse_map = {'UNITDSPR': 'MCDOWELL_N',
                           'MOTHERSUMI': 'MSUMI'}
                if symbol in nse_map:
                    symbol = nse_map[symbol]
                
                s_df = cached(symbol)
                if s_df is not None:
                    pass
                else:
                    s_df = tv.get_hist(
                                symbol,
                                'NSE',
                                interval=interval,
                                n_bars=duration,
                                extended_session=False,
                            )
                    if s_df is not None:
                        cached(symbol, s_df)
                if s_df is None:
                    print(f'Error fetching information on {symbol}')
                else:
                    s_df = s_df.drop(columns = ['open', 'high', 'low', 'volume'])
                    #print(s_df.head())
                    if len(s_df)==0:
                        print('Skip {}'.format(symbol))
                        continue
                    s_df.reset_index(inplace = True)
                    s_df.rename(columns={'close': stock, 'datetime': 'date'},
                               inplace = True)
                    #print(s_df.columns)
                    #pd.to_datetime(df['DateTime']).dt.date
                    s_df['date'] = pd.to_datetime(s_df['date'], format='%d-%m-%Y').dt.date
                    #s_df.drop_duplicates(inplace = True, subset='date')
                    s_df.set_index('date', inplace = True)
                    s_df = s_df.sort_index()
                    s_df = s_df.reindex(columns = [stock])
                    s_df = s_df[~s_df.index.duplicated(keep='first')]
                    #print(s_df.index.values[0], type(s_df.index.values[0]))
                    #print(pd.to_datetime(start_date).date(), type(pd.to_datetime(start_date).date()))
                    s_df = s_df.loc[pd.to_datetime(start_date).date():pd.to_datetime(end_date).date()]
                    #print(s_df.loc[start_date:end_date])
                    #print(s_df.head(10))
                    #print(s_df[s_df.index.duplicated(keep=False)])
                    df[stock] = s_df[stock]
        except Stock.DoesNotExist:
            print(f'{stock} values do not exist')
    df = df[~df.index.duplicated(keep='first')]
    #print(df.head(10))
    return df

def get_index_members(name):
    members = []
    if name not in INDICES:#MEMBER_MAP:
        log(f'{name} not in list', 'error')
        return members
    #with open('./indices/members/'+MEMBER_MAP[name], 'r', newline='') as csvfile:
    with open(f'{member_dir}{INDICES[name]}.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            members.append(row['Symbol'].strip())
    return members

def load_blacklist(name):
    blacklist = []
    try:
        with open(name, 'r') as fd:
            for symbol in fd:
                if symbol.strip().upper() not in blacklist:
                    blacklist.append(symbol.strip().upper())
    except:
        log(f'Exception opening {name}. Make sure the path is correct', 'warning')
    return blacklist


def get_symbol_replacements():
    r_map = {'UNITDSPR': 'MCDOWELL_N',
            'MOTHERSUMI': 'MSUMI',
            'AMARAJABAT': 'ARE_M'}
    return r_map