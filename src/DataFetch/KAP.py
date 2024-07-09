# Request related imports
from .Helpers.RequestWrapper import Request

# Parsing imports
import bs4
from bs4 import BeautifulSoup
from bs4.element import Tag
import re

# Miscellaneous imports
import time
from datetime import date
import json
from pathlib import Path

# Excel related imports
from openpyxl import Workbook
import pandas as pd

# Internal imports
from .Helpers.utils import convert_date_string, standardize_ticker, to_quarter, is_solo
from .Helpers.DateHandler import DateHandler
from .CompanyInfo import CompanyInfo, CompaniesInfo
from .KAPSearch import KAPSearch
from .KAPReport import KAPReport

# Constants related to the KAP website
# KAP Links
# TODO: Create and use a YAML file for the constants
KAP_SITE = "https://www.kap.org.tr"
COMPANY_LIST_SITE = "https://www.kap.org.tr/tr/bist-sirketler"
FILTER_SITE = "https://www.kap.org.tr/tr/FilterSgbf/FILTERSGBF"
DISCLOSURE_SITE = "https://www.kap.org.tr/tr/Bildirim"

DATE_PATH = Path(__file__).parents[2] / 'Data' / 'last_search_date.txt'

# Sleep time between each request, in seconds
SLEEP_TIME = 2.01

class KAP:
    """An interface for the KAP website."""

    def __init__(self, data_path: str) -> None:
        """Initialize the KAP interface."""
        self.companies_path = Path(data_path)
        self.r = Request(sleep_time=SLEEP_TIME)
        self.company_info = CompaniesInfo(self.companies_path / 'Company_Info.json')
        self.search = KAPSearch()
 
    def refresh_r(self) -> None:
        """Refresh the request object."""
        self.r = Request(sleep_time=SLEEP_TIME)

    # Get the company info object. If not initialized yet, initialize it first.
    def get_company_info(self, online=False):
        if online:
            self.company_info.get_from_kap()
        return self.company_info
    
    def reset_company_info(self):
        self.company_info.get_from_kap(reset=True)

    def get_mkk_id(self, ticker: str):
        # Standardize the parameter
        ticker = standardize_ticker(ticker)
        return self.company_info.companies[ticker].get_mkk_id(self.r)

    def get_share_count(self, ticker: str, online: bool=False):
        # Standardize the parameter
        ticker = standardize_ticker(ticker)
        return self.company_info.companies[ticker].get_share_count(self.r, reset=online)
    
    ### REPORT HANDLING FUNCTIONS ###
    
    def get_company_financials(self, ticker: str, update=True):
        # Standardize the ticker input
        ticker = standardize_ticker(ticker)

        # Update the data
        company_path = self.__get_save_path(ticker)
        # If the update option is chosen, update the data
        if update:
            self.save_financials(ticker)
        # Check if the data exists. if not, update the financials
        elif not (company_path.is_dir() and len(list(company_path.glob('*.xlsx'))) > 0):
            self.save_financials(ticker)
        
        # Get the data from the file path
        financial_tables = {}
        for financial_xl in company_path.glob('*.xlsx'):
            financial_period = financial_xl.name[-11:-5] # The part before ".xlsx"
            financial_tables[financial_period] = pd.read_excel(financial_xl, sheet_name=None)

        return financial_tables

    def update_financials(self, from_date:date):
        # Define the end date
        to_date = date.today()
        print(f'{from_date} to {to_date}')
        # Search the financials from the start to end dates
        search_results = self.search.search_financials(from_date, to_date)
        # Update the reports for each result
        for search_result in search_results:
            # Get the relevant info from the result
            ticker = standardize_ticker(search_result['stockCodes'])
            ticker_info = self.company_info.companies[ticker]
            report_period = to_quarter(search_result['year'], search_result['ruleTypeTerm'])
            report_idx = search_result['disclosureIndex']
            is_modified = search_result.get('isModified', '') # DUZELTME for modification, DUZELTILMIS for modified
            # Test print
            print(ticker, report_period)
            # Define the report object
            report = KAPReport(ticker, ticker_info, path=self.__get_save_path(ticker), period=report_period)
            # Save the report
            report_data = report.get_report(report_idx)
            # If the exact report is not saved before
            if not isinstance(report_data, pd.DataFrame):
                # If the report is already modified by another one, do not save it
                if is_modified == 'DUZELTILMIS':
                    print(f'Report {report_period} for {ticker} is not saved, it is already modified.')
                # In this case the report is either a modification or it was not seen before in this period, save it.
                else:
                    report.save_report(self.r, report_idx)
                    print(f'Report {report_period} for {ticker} is saved.')
            # If the report already exists, do not save it
            else:
                print(f'Report {report_period} for {ticker} already exists.')

        # Update the last search date
        date_handler = DateHandler(dt_value=date.today(), file_path=DATE_PATH)
        date_handler.save_to_file()

        return [standardize_ticker(search_result['stockCodes']) for search_result in search_results]

    def save_financials(self, ticker:str):
        # Standardize the parameter
        ticker = standardize_ticker(ticker)
        # Get the indices for the financials from the KAP website
        mkk_id = self.get_mkk_id(ticker)
        search_results = self.search.search_ticker_financials(mkk_id)
        for search_result in search_results:
            # Get the relevant info from the result
            ticker = standardize_ticker(search_result['stockCodes'])
            ticker_info = self.company_info.companies[ticker]
            report_period = to_quarter(search_result['year'], search_result['ruleTypeTerm'])
            report_idx = search_result['disclosureIndex']
            is_modified = search_result.get('isModified', '') # DUZELTME for modification, DUZELTILMIS for modified
            # Test print
            print(ticker, report_period)
            # Define the report object
            report = KAPReport(ticker, ticker_info, path=self.__get_save_path(ticker), period=report_period)
            # Save the report
            report_data = report.get_report(report_idx)
            # If the exact report is not saved before
            if not isinstance(report_data, pd.DataFrame):
                # If the report is already modified by another one, do not save it
                if is_modified == 'DUZELTILMIS':
                    print(f'Report {report_period} for {ticker} is not saved, it is already modified.')
                # In this case the report is either a modification or it was not seen before in this period, save it.
                else:
                    report.save_report(self.r, report_idx)
                    print(f'Report {report_period} for {ticker} is saved.')
            # If the report already exists, do not save it
            else:
                print(f'Report {report_period} for {ticker} already exists.')

    # TODO: Replace this with a config from the YAML file
    def __get_save_path(self, ticker):
        return self.companies_path / 'Companies' / ticker

