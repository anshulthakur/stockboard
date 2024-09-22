import os
import sys
import init
import csv
from datetime import datetime, timedelta
import dateparser
import signal
from lib.logging import set_loglevel, getLogger

from stocks.models import Listing, Stock, Market, Company

from lib.markets import BSE, NSE


MARKET_DATA = {
                'NSE': {'bhav': './nseData/',
                       'delivery': './nseData/delivery/',
                       'members': './nseData/scrips.csv'
                        },
                'BSE': {'bhav': './bseData/',
                       'delivery': './bseData/delivery/',
                       'members': './bseData/scrips.csv'
                        }
               }


def handler(signum, frame):
    print('Operation aborted.')
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    logger = getLogger()

    import argparse
    parser = argparse.ArgumentParser(description='Refresh stock member data for exchanges')
    parser.add_argument('-m', '--market', help="Market (NSE/BSE)")
    parser.add_argument('-d', '--debug', action='store_true', default=False, help="Debug")

    args = parser.parse_args()
    market = None

    if args.debug == True:
        set_loglevel('debug')

    if args.market is not None and len(args.market)>0:
        market = args.market

    if market is not None:
        if market not in ['BSE', 'NSE']:
            print(f'{market} not supported currently')
            exit(0)
        elif market=='NSE':
            mkt = NSE()
            mkt.refresh_companies_data(MARKET_DATA['NSE']['members'])
        elif market=='BSE':
            mkt = BSE()
            mkt.refresh_companies_data(MARKET_DATA['BSE']['members'])
    else:
        mkt = NSE()
        mkt.refresh_companies_data(MARKET_DATA['NSE']['members'])

        mkt = BSE()
        mkt.refresh_companies_data(MARKET_DATA['BSE']['members'])
