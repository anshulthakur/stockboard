import urllib3
from bs4 import BeautifulSoup
import json
import re
import time

from lib.misc import get_requests_headers
# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize urllib3 PoolManager
http = urllib3.PoolManager()

# Base URLs
BASE_URL = "https://www.screener.in"
BONUS_URL = f"{BASE_URL}/actions/bonus/"

# Headers to mimic a browser request
HEADERS = get_requests_headers()

def extract_stock_details(stock_url):
    """
    Extract NSE symbol and BSE SID from the stock's detail page.
    """
    if not stock_url:
        return {'nse_symbol': None, 'bse_sid': None}

    try:
        time.sleep(1)
        response = http.request('GET', stock_url, headers=HEADERS, timeout=10, retries=False)
        if response.status != 200:
            print(f"Failed to fetch {stock_url}: Status {response.status}")
            return {'nse_symbol': None, 'bse_sid': None}

        soup = BeautifulSoup(response.data, 'html.parser')
        company_links = soup.find('div', class_='company-links')

        nse_symbol = None
        bse_sid = None

        if company_links:
            links = company_links.find_all('a', href=True)
            for link in links:
                span = link.find('span')
                if span:
                    text = span.get_text(strip=True)
                    if text.startswith('NSE:'):
                        nse_symbol = text.replace('NSE:', '').strip()
                    elif text.startswith('BSE:'):
                        bse_sid = text.replace('BSE:', '').strip()

        return {'nse_symbol': nse_symbol, 'bse_sid': bse_sid}

    except Exception as e:
        print(f"Error fetching {stock_url}: {e}")
        return {'nse_symbol': None, 'bse_sid': None}


# Function to fetch and parse a single page of stock splits
def fetch_bonuses_page(page_url):
    response = http.request('GET', page_url)
    soup = BeautifulSoup(response.data, 'html.parser')

    # Parse the table rows containing stock splits
    table_rows = soup.select('#result_list tbody tr')

    splits = []
    for row in table_rows:
        stock_data = {}
        columns = row.find_all('td')
        
        # Extract the stock name and its URL for further details
        stock_link = row.select_one('.field-company_display a.font-weight-500')
        stock_data['stock'] = stock_link.select_one('span').text.strip()
        stock_data['details_url'] = f"https://www.screener.in{stock_link['href']}"
        
        # Extract other details
        stock_data['ex-date'] = columns[0].text.strip()
        stock_data['ratio'] = columns[1].text.strip()
        stock_data['nse'] = None
        stock_data['bse'] = None
        try:
            symbols = extract_stock_details(stock_data['details_url'])
            stock_data['nse'] = symbols.get('nse_symbol')
            stock_data['bse'] = symbols.get('bse_sid')
        except:
            pass
        splits.append(stock_data)

    return splits

# Function to get the total number of pages
def get_max_pages(page_url):
    response = http.request('GET', page_url)
    soup = BeautifulSoup(response.data, 'html.parser')

    paginator = soup.select_one('.paginator')
    last_page_link = paginator.find_all('a')[-1] if paginator else None
    
    return int(last_page_link.text) if last_page_link else 1


def main():
    all_bonuses = []

    # Determine the total number of pages
    max_pages = get_max_pages(BONUS_URL)
    
    # Fetch bonuses from each page
    for page_num in range(1, max_pages + 1):
        time.sleep(1)
        page_url = f"{BONUS_URL}?p={page_num}"
        print(f"Fetching page {page_num}...")
        bonuses = fetch_bonuses_page(page_url)
        all_bonuses.extend(bonuses)

    # Output the data as JSON
    with open('stock_bonuses.json', 'w', encoding='utf-8') as f:
        json.dump(all_bonuses, f, ensure_ascii=False, indent=4)

    print(f"Scraping completed. Total bonus entries: {len(all_bonuses)}")
    print("Data saved to stock_bonuses.json")

if __name__ == "__main__":
    main()
