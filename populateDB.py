import os
import sys
import init
import csv
from datetime import datetime, timedelta
import dateparser
import signal

from stocks.models import Listing, Stock, Market, Company

from lib.markets import BSE, NSE

error_dates = []
MARKET_DATA = {
                'NSE': {'bhav': './nseData/',
                       'delivery': './nseData/delivery/',
                        },
                'BSE': {'bhav': './bseData/',
                       'delivery': './bseData/delivery/',
                        }
               }

def write_error_file():
    global error_dates
    with open("error_dates.txt", 'a') as fd:
        for e in error_dates:
            fd.write(e+'\n')

def handler(signum, frame):
    write_error_file()
    print('Error dates appended to error_dates.txt')
    exit(0)

def parse_bse_delivery(dateval):
    global error_dates
    data = {}
    filename = 'SCBSEALL{}.csv'.format(dateval.strftime('%d%m'))
    path = MARKET_DATA['BSE']['delivery']+'{year}/'.format(year=dateval.date().year)+filename
    print('Parsing '+path)

    try:
        try:
            with open(path,'r') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    data[row['SCRIP CODE'].strip()]= row['DELIVERY QTY']
        except FileNotFoundError:
            filename = 'scbseall{}.csv'.format(dateval.strftime('%d%m'))
            path = MARKET_DATA['BSE']['delivery']+'{year}/'.format(year=dateval.date().year)+filename
            with open(path,'r') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    data[row['SCRIP CODE'].strip()]= row['DELIVERY QTY']
    except:
        print('Error parsing delivery file {}'.format(filename))
    return data

def parse_bse_bhav(reader, symbols, fname):
    global error_dates
    deliveries = None
    dateval = datetime.strptime(fname.upper().replace('BHAVCOPY_BSE_CM_0_0_0_','').replace('_F_0000.CSV',''), '%Y%m%d')
    market = Market.objects.get(name='BSE')
    #print(symbols)
    for row in reader:
        if row.get('FinInstrmId', None) is not None:
            if row.get('FinInstrmId').strip() not in symbols:
                #print(f"{row.get('SC_CODE')}({row.get('SC_NAME')}) has not been added to DB yet. Skip.")
                continue
            if deliveries is None:
                deliveries = parse_bse_delivery(dateval)
            try:
                stock = Stock.objects.get(sid=row.get('FinInstrmId'),
                                        market=market)
            except Stock.MultipleObjectsReturned:
                print(f"Trying to handle multiple entries for SID: {row.get('FinInstrmId')}")
                s = Stock.objects.filter(sid=row.get('FinInstrmId'),
                                        market=market)
                if len(s)>2:
                    raise Exception(f"Can't handle conflict of more than 2 values for SID {row.get('FinInstrmId')}")
                stock = s[1]
                try:
                    l = Listing.objects.get(stock=stock)
                except:
                    #Found the culprit
                    symbol = stock.symbol
                    stock.delete()
                    stock = s[0]
                    stock.symbol= symbol
                    stock.save()
                    #Though we don't need to redo it, but raise again if issues found
                    stock = Stock.objects.get(sid=row.get('FinInstrmId'),
                                                market=market)
            try:
                #listing = Listing.objects.filter(stock=stock, date__contains = dateval)
                #if len(listing) == 0:
                listing = Listing.objects.get(stock=stock, date = dateval)
                if listing.deliverable is None and row.get('FinInstrmId') in deliveries:
                    listing.deliverable = deliveries.get(row.get('FinInstrmId'))
                    print('Update delivery data')
                    listing.save()
            except Listing.DoesNotExist:
                print('Create entry for {}'.format(stock.symbol))
                listing = Listing(date=dateval,
                                  open=row.get('OpnPric'),
                                  high=row.get('HghPric'),
                                  low=row.get('LwPric'),
                                  close=row.get('ClsPric'),
                                  traded=row.get('TtlTradgVol'),
                                  trades=row.get('TtlNbOfTxsExctd'),
                                  stock = stock)
                if row.get('FinInstrmId') in deliveries:
                    listing.deliverable = deliveries.get(row.get('FinInstrmId'))
                listing.save()
            except Exception as e:
                print(e)
                print(("Unexpected error:", sys.exc_info()[0]))
                listing = Listing.objects.filter(stock=stock, date__contains = dateval)
                for l in listing:
                    print(l)
                continue
            

def parse_nse_delivery(dateval):
    data = {}
    filename = 'MTO_{}.csv'.format(dateval.strftime('%d%m%Y'))
    path = MARKET_DATA['NSE']['delivery']+filename
    print('Parsing '+path)
    try:
        with open(path,'r') as fd:
            reader = csv.DictReader(fd, skipinitialspace=True)
            for row in reader:
                data[row['Name of Security']]= row['Deliverable Quantity']
    except:
        print('Error parsing {}'.format(filename))
    return data

def parse_nse_bhav(reader, symbols, fname):
    #deliveries = None
    #print(symbols)
    market = Market.objects.get(name='NSE')
    dateval = None
    for row in reader:
        if row.get('SYMBOL', None) is not None:
            #print(row)
            if row.get('SYMBOL') not in symbols and row.get('SERIES') in ['EQ', 'BE']:
                print(f"{row.get('SYMBOL')} has not been added to DB yet. Skip.")
                continue
            if dateval is None:
                dateval = dateparser.parse(row.get('DATE1').strip())
            # if deliveries is None:
            #     deliveries = parse_nse_delivery(dateval)
            stock = None
            try:
                stock = Stock.objects.get(symbol=row.get('SYMBOL'),
                                        market=market)
            except Stock.DoesNotExist:
                print(f"{row.get('SYMBOL')} does not exist for market {market.name}")
                continue
            try:
                #listing = Listing.objects.filter(stock=stock, date__contains = dateval)
                #if len(listing) == 0:
                listing = Listing.objects.get(stock=stock, date = dateval)
                if listing.deliverable is None:
                    if row.get('DELIV_QTY') == '-':
                        listing.deliverable = row.get('TTL_TRD_QNTY')
                    else:
                        listing.deliverable = row.get('DELIV_QTY')
                    print('Update delivery data')
                    listing.save()
            except Listing.DoesNotExist:
                print('Create entry for {}'.format(stock.symbol))
                listing = Listing(date=dateval,
                                open=row.get('OPEN_PRICE'),
                                high=row.get('HIGH_PRICE'),
                                low=row.get('LOW_PRICE'),
                                close=row.get('CLOSE_PRICE'),
                                traded=row.get('TTL_TRD_QNTY'),
                                deliverable=row.get('DELIV_QTY') if row.get('DELIV_QTY') != '-' else row.get('TTL_TRD_QNTY'),
                                stock = stock)
                #if row.get('SYMBOL') in deliveries:
                #    listing.deliverable = deliveries.get(row.get('SYMBOL'))
                listing.save()
            except Exception as e:
                print(e)
                print(("Unexpected error:", sys.exc_info()[0]))
                listing = Listing.objects.filter(stock=stock, date__contains = dateval)
                for l in listing:
                    print(l)
                continue
            

def get_active_scrips(market):
    symbols = {}
    if market.name=='NSE':
        members = NSE().get_scrip_list(offline=True)
    elif market.name=='BSE':
        members = BSE().get_scrip_list(offline=True)
    for member in members:
        try:
            company = Company.objects.get(isin=member.get('isin'))
        except Company.DoesNotExist:
            company = Company(isin=member.get('isin'),
                                name=member.get('name'))
            company.save()
        try:
            stock = Stock.objects.get(symbol=member.get('symbol').replace('*',''), market=market)
        except Stock.DoesNotExist:
            stock = Stock(face_value=int(float(member.get('facevalue'))),
                          market = market,
                          symbol=member.get('symbol').replace('*',''),
                          content_object=company
                         )
            if market.name=='BSE':
                stock.sid = member.get('security')
            stock.save()
        if market.name=='NSE':
            symbols[member.get('symbol').replace('*','')] = stock
        elif market.name=='BSE':
            symbols[member.get('security')] = stock
    return symbols

def get_bhav_filename(day, market):
    months = ['', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                  'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    fname = None
    if market=='BSE':
        fname= 'BhavCopy_BSE_CM_0_0_0_{year:04}{month:02}{day:02}_F_0000.CSV'.format(day = day.day, 
                                                        month = day.month, 
                                                        year = str(day.year))
    elif market=='NSE':
        fname='sec_bhavdata_full_{day:02}{month:02}{year:04}.csv'.format(day = day.day, 
                                                                        month = day.month, 
                                                                        year = day.year)
    return fname


def populate_for_date(market, symbols, date=datetime.today()):
    global error_dates
    f = get_bhav_filename(day=date, market = market.name)
    print('Parsing '+MARKET_DATA[market.name]['bhav']+f)
    try:
        with open(MARKET_DATA[market.name]['bhav']+f,'r') as fd:
            reader = csv.DictReader(fd)
            if market.name=='NSE':
                parse_nse_bhav(reader, symbols, f)
            elif market.name=='BSE':
                parse_bse_bhav(reader, symbols, f)
    except FileNotFoundError:
        if date.weekday()<=4: #Weekends won't have a file
            error_dates.append(date.strftime('%d-%m-%y'))
            print('Error')
        pass

def populate_db(market, date = None, bulk=False):
    #Create Market object
    if date is None and bulk is False:
        date = datetime.today()
    elif date is None and bulk is True:
        date = datetime.strptime('01-01-2010', "%d-%m-%Y").date()
    
    market_obj = None
    try:
        market_obj = Market.objects.get(name=market)
    except Market.DoesNotExist:
        print(f'Create for {market}')
        market_obj = Market(name=market)
        market_obj.save()
    except Exception as e:
        print(e)
        print(("Unexpected error:", sys.exc_info()[0]))
        return
    #Create scrip members (and Company if applicable)
    print(market_obj)
    symbols = get_active_scrips(market_obj)

    #Handle bhav data
    if bulk:
        while date <= datetime.today().date():
            populate_for_date(market = market_obj, symbols=symbols, date=date)
            date = date + timedelta(days=1)
    else:
        populate_for_date(market = market_obj, symbols=symbols, date=date)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    import argparse
    parser = argparse.ArgumentParser(description='Download stock data for stock/date')
    parser.add_argument('-m', '--market', help="Market (NSE/BSE/MCX/...)")
    parser.add_argument('-d', '--date', help="Date")
    parser.add_argument('-b', '--bulk', help="Get bulk data for stock(s)", action="store_true", default=False)

    args = parser.parse_args()
    market = None
    day = None

    if args.date is not None and len(args.date)>0:
        print('Get data for date: {}'.format(args.date))
        day = datetime.strptime(args.date, "%d/%m/%y").date()

    if args.market is not None and len(args.market)>0:
        market = args.market

    if market is not None:
        if market not in ['BSE', 'NSE']:
            print(f'{market} not supported currently')
            exit(0)
        elif market=='NSE':
            mkt = NSE()
            mkt.download_archive(day, args.bulk)
        elif market=='BSE':
            mkt = BSE()
            mkt.download_archive(day, args.bulk)
        populate_db(market, date=day, bulk=args.bulk)
    else:
        mkt = NSE()
        mkt.download_archive(day, args.bulk)

        mkt = BSE()
        mkt.download_archive(day, args.bulk)

        populate_db(market='NSE', date=day, bulk=args.bulk)
        populate_db(market='BSE', date=day, bulk=args.bulk)
    write_error_file()
