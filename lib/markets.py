import os
import requests
import csv
from datetime import datetime, timedelta
from zipfile import ZipFile

from .misc import get_requests_headers, handle_download

months = ['', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

class Market(object):

    def clean_delivery_data(self, filename):
        pass

    def download_for_day(self, session, date):
        pass

    def download_archive(self, date = datetime.strptime('01-01-2010', "%d-%m-%Y").date(), bulk=False):
        pass

    def parse_bhavcopy(self):
        pass

    def parse_delivery_data(self):
        pass

    def get_scrip_list(self):
        pass

class BSE(Market):
    def __init__(self):
        self.raw_data_dir = './bseData/'
        self.base_url = "https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx"        
        self.delivery_data_dir = self.raw_data_dir+'delivery/'

    def clean_delivery_data(self, filename):
        newfile = filename.replace('txt', 'csv').replace('TXT', 'csv')
        try:
            with open(newfile, 'w') as d_fd:
                with open(filename, 'r') as fd:
                    for row in fd:
                        d_fd.write(row.replace('|', ','))
            os.remove(filename)
        except FileNotFoundError:
            with open(newfile, 'w') as d_fd:
                with open(filename.replace('txt', 'TXT'), 'r') as fd:
                    for row in fd:
                        d_fd.write(row.replace('|', ','))
            os.remove(filename.replace('txt', 'TXT'))

    def download_for_day(self, session, date):
        base_bhav_file_csv = 'BhavCopy_BSE_CM_0_0_0_{year:04}{month:02}{day:02}_F_0000.CSV'
        base_bhav_file = 'EQ{day:02}{month:02}{year}_CSV.zip'
        base_url_bhav = 'https://www.bseindia.com/download/BhavCopy/Equity/'+base_bhav_file_csv

        base_delivery_file = 'SCBSEALL{day:02}{month:02}.zip'
        base_delivery_url = 'https://www.bseindia.com/BSEDATA/gross/{year}/'+base_delivery_file
        #Download bhavcopy
        if os.path.exists(self.raw_data_dir+base_bhav_file_csv.format(day=date.day, month=date.month, year=str(date.year))):
            print('Skip bhav')
            pass
        elif os.path.exists(self.raw_data_dir+base_bhav_file_csv.replace('csv', 'CSV').format(day=date.day, month=date.month, year=str(date.year)[-2:])):
            print('Skip bhav')
            pass
        else:
            handle_download(session=session,
                            url = base_url_bhav.format(day=date.day, month=date.month, year=str(date.year)),
                            filename = base_bhav_file_csv.format(day=date.day, month=date.month, year=str(date.year)),
                            path=self.raw_data_dir)
            # #Bhavcopy is zip file, so handle that
            # if os.path.isfile(self.raw_data_dir+base_bhav_file.format(day=date.day, month=date.month, year=str(date.year)[-2:])):
            #     with ZipFile(self.raw_data_dir+base_bhav_file.format(day=date.day, month=date.month, year=str(date.year)[-2:]), 'r') as zipf:
            #         zipf.extractall(self.raw_data_dir)
            #     os.remove(self.raw_data_dir+base_bhav_file.format(day=date.day, month=date.month, year=str(date.year)[-2:]))
        #Download delivery data
        if (os.path.exists(self.delivery_data_dir+str(date.year)+'/'+base_delivery_file.replace('zip', 'csv').format(day=date.day, month=date.month, year=date.year))) or \
            (os.path.exists(self.delivery_data_dir+str(date.year)+'/'+base_delivery_file.replace('zip', 'CSV').format(day=date.day, month=date.month, year=date.year))):
            print('Skip delivery data')
        else:
            handle_download(session, url = base_delivery_url.format(day=date.day, month=date.month, year=date.year), 
                                filename = base_delivery_file.format(day=date.day, month=date.month, year=date.year),
                                path=self.delivery_data_dir+str(date.year)+'/')
            #Delivery file is zip file, so handle that
            if os.path.isfile(self.delivery_data_dir+str(date.year)+'/'+base_delivery_file.format(day=date.day, month=date.month, year=date.year)):
                with ZipFile(self.delivery_data_dir+str(date.year)+'/'+base_delivery_file.format(day=date.day, month=date.month, year=date.year), 'r') as zipf:
                    zipf.extractall(self.delivery_data_dir+str(date.year))
                os.remove(self.delivery_data_dir+str(date.year)+'/'+base_delivery_file.format(day=date.day, month=date.month, year=date.year))
                self.clean_delivery_data(self.delivery_data_dir+str(date.year)+'/'+base_delivery_file.replace('zip','txt').format(day=date.day, month=date.month, year=date.year))

    def download_archive(self, date = datetime.strptime('01-01-2010', "%d-%m-%Y").date(), bulk=False):
        session = requests.Session()
        session.headers.update(get_requests_headers())
        session.headers.update({"authority": "www.bseindia.com"})
        if bulk:
            while date <= datetime.today().date():
                if date.weekday()<=4:
                    print(f'Downloading for {date}')
                    self.download_for_day(session, date)
                date = date + timedelta(days=1)
        else:
            print(f'Downloading for {date}')
            self.download_for_day(session, date)

    def get_scrip_list(self, offline=False):
        url = 'https://www.bseindia.com/corporates/List_Scrips.html'
        filename = 'BSE_list.csv'
        if os.path.exists('./'+filename):
            print(f'File may be outdated. Download latest copy from: {url}')
            members = []
            with open(filename,'r') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    members.append({'symbol': row['Security Id'].upper().strip(),
                                    'name':row['Issuer Name'].upper().strip(),
                                    'isin': row['ISIN No'].upper().strip(),
                                    'facevalue': row['Face Value'].upper().strip(),
                                    'security': row['Security Code'].upper().strip()
                                    })
        else:
            print(f'BSE list of scrips does not exist in location. Download from: {url}')
        return members

class NSE(Market):
    def __init__(self):
        self.raw_data_dir = './nseData/'
        self.delivery_data_dir = self.raw_data_dir+'delivery/'
        self.base_url = 'https://www.nseindia.com/all-reports'
        

    def clean_delivery_data(self, filename):
        skip = 4
        newfile = filename.replace('DAT', 'csv')
        with open(newfile, 'w') as d_fd:
            d_fd.write("Record Type,Sr No,Name of Security,Type,Quantity Traded,Deliverable Quantity,Percentage\n")
            with open(filename, 'r') as fd:
                for row in fd:
                    if skip >0:
                        skip -= 1
                        continue
                    d_fd.write(row)
        os.remove(filename)

    def clean_bhav_file(self, filename):
        bhav = []
        with open(filename, 'r') as fd:
            for row in fd:
                bhav.append(','.join(row.split(', ')))
        with open(filename, 'w') as fd:
            for row in bhav:
                fd.write(row+'\n')

    def download_for_day(self, session, date):
        #https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_08072024.csv
        #https://nsearchives.nseindia.com/archives/equities/bhavcopy/pr/PR080724.zip
        base_bhav_file_csv = 'sec_bhavdata_full_{day:02}{month:02}{year:04}.csv'
        base_bhav_file = base_bhav_file_csv+'.zip'
        base_url_bhav = 'https://nsearchives.nseindia.com/products/content/'+base_bhav_file_csv
        base_delivery_file = 'MTO_{day:02}{month:02}{year:04}.DAT'
        #https://nsearchives.nseindia.com/archives/equities/mto/MTO_08072024.DAT
        base_delivery_url = 'https://archives.nseindia.com/archives/equities/mto/'+base_delivery_file

        #Download bhavcopy
        if os.path.exists(self.raw_data_dir+base_bhav_file_csv.format(day=date.day, month=date.month, year=date.year)): #and \
            #os.path.exists(self.delivery_data_dir+base_delivery_file.replace('DAT', 'csv').format(day=date.day, month=date.month, year=date.year)):
            pass
        else:
            session.headers.update({"host": "www.nseindia.com"})
            session.get(self.base_url)
            session.headers.update({"host": "nsearchives.nseindia.com"})
        if os.path.exists(self.raw_data_dir+base_bhav_file_csv.format(day=date.day, month=date.month, year=date.year)):
            pass
        else:
            handle_download(session, url = base_url_bhav.format(day=date.day, month=date.month, year=date.year),
                                filename = base_bhav_file_csv.format(day=date.day, month=date.month, year=date.year),
                                path=self.raw_data_dir)
            self.clean_bhav_file(os.path.join(self.raw_data_dir, base_bhav_file_csv.format(day=date.day, month=date.month, year=date.year)))
            #Bhavcopy is zip file, so handle that
            # if os.path.isfile(self.raw_data_dir+base_bhav_file.format(day=date.day, month=months[date.month], year=date.year)):
            #     with ZipFile(self.raw_data_dir+base_bhav_file.format(day=date.day, month=months[date.month], year=date.year), 'r') as zipf:
            #         zipf.extractall(self.raw_data_dir)
            #         #print('Done!')
            #     os.remove(self.raw_data_dir+base_bhav_file.format(day=date.day, month=months[date.month], year=date.year))

        #Download delivery data
        # if os.path.exists(self.delivery_data_dir+base_delivery_file.format(day=date.day, month=date.month, year=date.year)):
        #     self.clean_delivery_data(self.delivery_data_dir+base_delivery_file.format(day=date.day, month=date.month, year=date.year))
        # elif os.path.exists(self.delivery_data_dir+base_delivery_file.replace('DAT', 'csv').format(day=date.day, month=date.month, year=date.year)):
        #     pass
        # else:
        #     handle_download(session, url = base_delivery_url.format(day=date.day, month=date.month, year=date.year), 
        #                         filename = base_delivery_file.format(day=date.day, month=date.month, year=date.year),
        #                         path=self.delivery_data_dir)
        #     if os.path.exists(self.delivery_data_dir+base_delivery_file.format(day=date.day, month=date.month, year=date.year)):
        #         self.clean_delivery_data(self.delivery_data_dir+base_delivery_file.format(day=date.day, month=date.month, year=date.year))

    def download_archive(self, date = datetime.strptime('01-01-2010', "%d-%m-%Y").date(), bulk=False):
        session = requests.Session()
        session.headers.update(get_requests_headers())
        session.headers.update({"host": "www.nseindia.com",
                                "referer": "https://www.nseindia.com"})
        if bulk:
            while date <= datetime.today().date():
                if date.weekday()<=4:
                    print(f'Downloading for {date}')
                    self.download_for_day(session, date)
                date = date + timedelta(days=1)
        else:
            print(f'Downloading for {date}')
            self.download_for_day(session, date)

    def get_scrip_list(self, offline=False):
        url = 'https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv'
        filename = 'NSE_list.csv'
        session = requests.Session()
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        session.headers.update(get_requests_headers())
        session.headers.update({"authority": "www.nseindia.com",
                                "referrer": "www.nseindia.com"})
        if not offline:
            try:
                session.get('https://www.nseindia.com/market-data/securities-available-for-trading')
                handle_download(session,
                                url = url,
                                filename = filename,
                                path='./')
            except:
                print("Could not download latest ")
                pass
        
        if os.path.exists('./'+filename):
            print(f'File may be outdated. Download latest copy from: {url}')
        else:
            print(f'NSE list of scrips does not exist in location. Download from: {url}')

        members = []
        if os.path.exists('./'+filename):
            with open(filename,'r') as fd:
                reader = csv.DictReader(fd)
                for row in reader:
                    members.append({'symbol': row['SYMBOL'].upper().strip(),
                                    'name':row['NAME OF COMPANY'].upper().strip(),
                                    'isin': row[' ISIN NUMBER'].upper().strip(),
                                    'facevalue': row[' FACE VALUE'].upper().strip()
                                    })
        return members