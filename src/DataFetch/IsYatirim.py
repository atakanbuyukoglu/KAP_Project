# Request related imports
from .Helpers.RequestWrapper import Request
from .Helpers.utils import standardize_ticker

# Miscellaneous imports
from pathlib import Path
import json

SLEEP_TIME = 2.01

'''
Sample URLs:

https://www.isyatirim.com.tr/_layouts/15/Isyatirim.Website/Common/Data.aspx/HisseTekil?hisse=MEGAP&startdate=22-06-2024&enddate=30-06-2024.json

'''

INFO_PATH = Path(__file__).parents[2] / 'Data' / 'SirketBilgileri.json'
INFO_URL = 'https://www.isyatirim.com.tr/_layouts/15/Isyatirim.Website/Common/Data.aspx/SirketBilgileri'

class IsYatirim:

    def __init__(self) -> None:
        self.info_path = INFO_PATH
        self.r = Request(sleep_time=SLEEP_TIME)
        with open(INFO_PATH, 'r', encoding='utf-8') as f:
            self.info = json.load(f)['value']

    def get_info(self):
        return self.info
    
    def get_sector(self, ticker):
        ticker = standardize_ticker(ticker)
        # Handle exceptions
        if ticker == 'KRDMA':
            ticker = 'KRDMD'
        if ticker == 'ISATR':
            ticker = 'ISCTR'            
        sector = [s['AS_ALT_SEKTOR_TANIMI'] for s in self.info if s['Title'] == ticker]
        if len(sector) > 0:
            sector = sector[0]
        else:
            sector = 'Bilinmeyen'
        return sector
    
    def update_companies(self):
        resp = self.r.get(INFO_URL)
        with open(INFO_PATH, 'w', encoding='utf-8') as f:
            f.write(resp.text)

    

