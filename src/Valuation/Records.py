from pathlib import Path
from openpyxl import Workbook, load_workbook
from itertools import islice
from .Metrics import Company
from ..DataFetch.RequestWrapper import Request
from ..DataFetch.utils import standardize_ticker
from yfinance import Ticker
import numpy as np

# TODO: Create an Excel file and update it given the company names with the valuations and prices
class Records():
    
    def __init__(self, file_path, initial_tickers=None, add_tickers=False, online=True) -> None:
        self.file_path = Path(file_path)
        if self.file_path.is_file():
            self.file = load_workbook(filename=self.file_path)
        else:
            self.file = Workbook()
            self.file.save(self.file_path)
        self.tickers = initial_tickers

        # Initialize the file if initial tickers are given
        if add_tickers:
            self.__set_values('Hisse', self.tickers, save=True)

        self.online = online
        self.yahoo_session = Request(sleep_time=1.0)

    def update(self, all=True):
        online = self.online
        self.update_prices(all=all)
        self.update_intrinsic_values(all=all)
        self.online = False
        self.update_intrinsic_values(all=all, quarter=True)
        self.online = online
        #self.file.save(filename=self.file_path)

    def update_ticker(self, ticker: str, save=True):
        ticker = standardize_ticker(ticker)

        sheet = self.file.active
        header_location = self.__get_header_location('Hisse')
        ticker_column = sheet[header_location]
        ticker_row = -1
        for ticker_idx in range(len(ticker_column)):
            if ticker_column[ticker_idx].value == ticker:
                ticker_row = ticker_idx + 1
        if ticker_row == -1:
            raise KeyError(ticker)

        price_header = self.__get_header_location('Fiyat')
        cell_location = price_header + str(ticker_row)
        sheet[cell_location] = self.__get_price(ticker)

        intrinsic_header = self.__get_header_location('İçsel Değer')
        cell_location = intrinsic_header + str(ticker_row)
        sheet[cell_location] = self.__get_intrinsic_value(ticker)
        intrinsic_header = self.__get_header_location('İçsel Değer (Çeyrek)')
        cell_location = intrinsic_header + str(ticker_row)
        sheet[cell_location] = self.__get_intrinsic_value(ticker, quarter=True)

        if save:
            self.file.save(filename=self.file_path)


    def update_intrinsic_values(self, all=True, quarter=False, save=True):
        # Load the sheet
        sheet = self.file.active
        # Get header location, update the header if needed
        intrinsic_header_str = 'İçsel Değer (Çeyrek)' if quarter else 'İçsel Değer'
        intrinsic_header = self.__get_header_location(intrinsic_header_str)
        ticker_header = self.__get_header_location('Hisse')
        # Update all values on the column
        tickers = self.__get_values(ticker_header)
        values = self.__get_values(intrinsic_header)
        for idx, value in enumerate(values):
            if tickers[idx] is None or tickers[idx] == 'Total':
                continue
            # This happens on empty parts
            if all or value is None:
                cell_location = intrinsic_header + str(idx + 2)
                intr_value = self.__get_intrinsic_value(tickers[idx], quarter=quarter)
                sheet[cell_location] = intr_value
        
        if save:
            self.file.save(filename=self.file_path)

    def update_prices(self, all=True, save=True):
        # Load the sheet
        sheet = self.file.active
        # Get header location, update the header if needed
        price_header = self.__get_header_location('Fiyat')
        ticker_header = self.__get_header_location('Hisse')
        # Update all values on the column
        tickers = self.__get_values(ticker_header)
        values = self.__get_values(price_header)
        for idx, value in enumerate(values):
            if tickers[idx] is None or tickers[idx] == 'Total':
                continue
            # This happens on empty parts
            if all or value is None:
                cell_location = price_header + str(idx + 2)
                price_value = self.__get_price(tickers[idx])
                sheet[cell_location] = price_value
        
        if save:
            self.file.save(filename=self.file_path)
                
    def __get_header_location(self, header_name):
        # Load the sheet
        sheet = self.file.active
        try:
            headers = [cell.value for cell in next(sheet.rows)]
        except StopIteration:
            headers = []
        # Try to get the header
        try:
            header_location = headers.index(header_name)
            header_location = chr(ord('A') + header_location)
        # If it does not work, create the header
        except ValueError:
            # Try to find an empty cell
            header_location = 'A'
            while sheet[header_location + '1'].value:
                header_location = chr(ord(header_location) + 1)
            sheet[header_location + '1'] = header_name
        # Return the header location
        return header_location
    
    def __get_values(self, header_location: str):
        # Load the sheet
        sheet = self.file.active

        header_idx = ord(header_location) - ord('A')
        header_cells = next(islice(sheet.columns, header_idx, None))
        values = [cell.value for cell in header_cells]
        values = values[1:] # Remove the header

        return values

    def __set_values(self, header_name: str, values: list, save=False):
        # Load the sheet
        sheet = self.file.active
        # Get header location
        header_location = self.__get_header_location(header_name)
        # Save the values
        value_idx = 2
        for value in values:
            cell_name = header_location + str(value_idx)
            sheet[cell_name] = value
            value_idx += 1
        if save:
            self.file.save(self.file_path)
            

    def __get_intrinsic_value(self, ticker: str, quarter=False):
        company = Company(ticker, self.file_path.parents[1], update=self.online)
        multiplier = 1.0
        return company.default_valuation(quarter=quarter, extra_multiple=multiplier)

    def __get_price(self, ticker: str):
        # TODO: Get the price here
        try:
            stock = Ticker(ticker=ticker + '.IS', session=self.yahoo_session)
            metadata = stock.get_history_metadata()
            price = metadata['regularMarketPrice']
            price = np.round(price, 2)
            print('Price for', ticker, 'obtained:', price)
            return price
        except:
            print('Price for', ticker, 'could not be obtained.')
            return 0.0
