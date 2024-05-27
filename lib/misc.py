'''
Created on 30-Jul-2022

@author: anshul
'''

import socket
import os
import datetime
from dateutil.relativedelta import relativedelta
from lib.logging import log 
import requests
import brotli
import gzip
from io import BytesIO
import time

REMOTE_SERVER = "one.one.one.one"
def is_connected(hostname):
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(hostname)
        # connect to the host -- tells us if the host is actually reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except Exception:
        pass # we ignore any errors, returning False
    return False

def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
    except FileExistsError:
        pass

def get_filelist(folder, recursive=False):
    if not recursive:
        files = os.listdir(folder)
        files = [f for f in files if os.path.isfile(folder+'/'+f) and f[-3:].strip().lower()=='csv'] #Filtering only the files.
        return files
    else:
        from os.path import join, getsize
        file_list = []
        for root, dirs, files in os.walk(folder):
            for name in files:
                file_list.append(join(root, name)) 
        return file_list


def create_intraday_folders(base_folder='./'):
    '''
    Need a good way of sorting out intraday data. So, proposed folder and file heirarchy is:

    intraday
    |_ <year>
        |_ <month>
            |_ <day>
                |_ <scrip.csv>
    '''
    date = datetime.datetime.strptime('2012/01', "%Y/%m")
    today = datetime.datetime.today()
    while date.year < today.year or date.month <= today.month:
        create_directory(path = os.path.join(os.path.abspath(base_folder), f'{date.year}/{date.month:02d}'))
        date += relativedelta(months=+1)



def handle_download(session, url, filename, path, overwrite=False):
    '''
    Handle downloading files when provided with a URL

    @param session Session object
    @url    URL to fetch and download from
    @filename Name of the file as saved on disk
    @path   Path do downloads directory
    @overwrite Flag indicating whether existing file should be overwritten
    '''
    try:
        create_directory(path)
    except FileExistsError:
        pass
    except:
        print('Error creating raw data folder')
        exit(0)
    print(url)
    if not overwrite and os.path.isfile(path+filename):
        #Skip file download
        return
    time.sleep(1)
    try:
        response = session.get(url, timeout=10)
    except requests.exceptions.TooManyRedirects:
        print('Data may not be available')
        return
    except requests.exceptions.Timeout:
        #Skip file download
        print('Timeout')
        return
    #print(response.headers)
    text = False
    if response.status_code==200:
        try:
            result = brotli.decompress(response.content).decode('utf-8')
        except:
            try:
                buf = BytesIO(response.content)
                result = gzip.GzipFile(fileobj=buf).read().decode('utf-8')
            except:
                try:
                    result = response.content.decode('utf-8')
                    text=True
                except:
                    result = response.content
        if text:
            with open(os.path.join(path,filename), 'w') as fd:
                fd.write(result)
        else:
            with open(os.path.join(path,filename), 'wb') as fd:
                fd.write(result)
            
    else:
        print(response.content.decode('utf-8'))
        print('Received textual data')
        pass


def get_requests_headers():
    """
    Return a correct and generic browser request header which will not be rejected by the servers. 
    Additional headers specific to the site can be appended at the callers end by using `.update()` method.
    """
    headers = {
            "accept-encoding": "gzip, deflate, br",
            "accept":
            """text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7""",
            "accept-language": "en-US,en;q=0.9,hi;q=0.8",
            'Connection': 'keep-alive',
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
            "upgrade-insecure-requests": "1",
            }
    return headers
