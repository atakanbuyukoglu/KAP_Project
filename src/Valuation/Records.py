from pathlib import Path
from openpyxl import Workbook, load_workbook
from itertools import islice
from .Metrics import Company
from yfinance import Ticker

# TODO: Create an Excel file and update it given the company names with the valuations and prices
class Records():
    
    def __init__(self, file_path) -> None:
        self.file_path = Path(file_path)
        self.file = load_workbook(filename=self.file_path)

    def update(self):
        self.update_prices(save=False)
        self.update_intrinsic_values(save=False)
        self.file.save(filename=self.file_path)

    def update_intrinsic_values(self, all=False, save=True):
        # Load the sheet
        sheet = self.file.active
        # Get header location, update the header if needed
        intrinsic_header = self.__get_header_location('İçsel Değer')
        ticker_header = self.__get_header_location('Hisse')
        # Update all values on the column
        tickers = self.__get_values(ticker_header)
        values = self.__get_values(intrinsic_header)
        for idx, value in enumerate(values):
            if tickers[idx] is None or tickers[idx] == 'Total':
                continue
            # This happens on empty parts
            if value is None:
                cell_location = intrinsic_header + str(idx + 2)
                intr_value = self.__get_intrinsic_value(tickers[idx])
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
        headers = [cell.value for cell in next(sheet.rows)]
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

    def __get_intrinsic_value(self, ticker: str):
        company = Company(ticker, self.file_path.parents[1])
        multiplier = 1.0
        return company.default_valuation(extra_multiple=multiplier)

    def __get_price(self, ticker: str):
        # TODO: Get the price here
        return Ticker(ticker=ticker + '.IS').fast_info['last_price']
