# Request related imports
from .Helpers.RequestWrapper import Request

# Parsing imports
import bs4
from bs4 import BeautifulSoup
from bs4.element import Tag
import re

# Miscellaneous imports
import time
import json
from pathlib import Path

# Excel related imports
from openpyxl import Workbook
import pandas as pd

# Internal imports
from .Helpers.utils import auto_fit_columns, standardize_ticker, to_quarter, is_solo
from .CompanyInfo import CompanyInfo, CompaniesInfo

# Constants related to the KAP website
# KAP Links
# TODO: Create and use a YAML file for the constants
KAP_SITE = "https://www.kap.org.tr"
COMPANY_LIST_SITE = "https://www.kap.org.tr/tr/bist-sirketler"
FILTER_SITE = "https://www.kap.org.tr/tr/FilterSgbf/FILTERSGBF"
DISCLOSURE_SITE = "https://www.kap.org.tr/tr/Bildirim"

# Sleep time between each request, in seconds
SLEEP_TIME = 2.01
# TODO: Search for new financial reports
class KAP:
    """An interface for the KAP website."""

    def __init__(self, data_path: str) -> None:
        """Initialize the KAP interface."""
        self.companies_path = Path(data_path)
        self.r = Request(sleep_time=SLEEP_TIME)
        self.company_info = CompaniesInfo(self.companies_path / 'Company_Info.json')
 
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
    
    # TODO: Handle bank financials
    ### REPORT HANDLING FUNCTIONS ###
    def __save_report(self, report, ticker, year, month, check_solo=False):
        # Define the save path
        save_path = self.__get_save_path(ticker)
        save_path.mkdir(parents=True, exist_ok=True)

        # Parse the HTML file
        soup = BeautifulSoup(report, 'html.parser')
        # Find the currency and its multiple for the reports
        report_info = soup('td', class_='financial-header-title', limit=2)
        currency = report_info[0]
        currency = currency.next_sibling.next_sibling
        currency = str(currency.string)
        currency_multiple = 10 ** currency.count('0')
        # Do not save the report if it is not consolidated if the option to check is enabled.
        if check_solo:
            report_type = report_info[1]
            report_type = report_type.next_sibling.next_sibling
            report_type = str(report_type.string)
            if report_type != 'Konsolide':
                return False
        # Get all parts of the financial tables
        financial_tables = soup('table', class_='financial-table')
        pd_reports = []
        report_idx = 1
        # For each table: Balance sheet, income statement etc.
        for financial_table in financial_tables:
            # Get to the body part
            financial_table = financial_table.tbody
            # Define the headers to get the column names
            columns = []
            financial_table_tr = financial_table.find_all('tr', limit=2)
            financial_table_name = financial_table_tr[1]
            financial_table_name = financial_table_name.find(class_='taxonomy-field-title')
            # TODO: Fix for the banks
            # If the report name is not found, the table is not compatible, it is probably auditor notes. So just pass that part.
            if financial_table_name is None:
                continue
            # TODO: Understand this part
            financial_table_name = str(financial_table_name.find(class_='content-tr').string)
            financial_table_name = financial_table_name.strip()
            financial_table_name = 'Table ' + str(report_idx)
            report_idx += 1
            columns.append(financial_table_name)
            # Add the date headers
            financial_table_info = financial_table_tr[0]
            financial_table_headers = financial_table_info.find_all(class_='context-header')
            for table_header in financial_table_headers:
                header = table_header
                header = header.find(class_='content-tr')
                header = str(header.contents[-1])
                header = header.strip()
                columns.append(header)
            # Get the pandas variable for the report
            pd_reports.append(self.__table_2_pandas(financial_table, columns, currency_multiple))

        # Save the financials to an Excel file
        with pd.ExcelWriter(save_path / ('Financials_'+ticker+'_'+to_quarter(year, month)+'.xlsx')) as writer:
            report_idx = 1
            for report in pd_reports:
                financial_table_name = 'Table ' + str(report_idx)
                report.to_excel(writer, sheet_name=financial_table_name)
                report_idx += 1
        return True

    def __table_2_pandas(self, report: Tag, report_columns: list, multiple):
        # Get the table values
        pd_balance_sheet = []
        for element in report.children:
            # Filter visible table elements
            if element.name == 'tr' and element.has_attr('class') and 'presentation-enabled' in element['class']:
                # Prepare the table row
                pd_element = []
                title = element.find(class_='taxonomy-field-title')
                if title is None:
                    continue
                title = str(title.find(class_='content-tr').string)
                title = title.strip()
                pd_element.append(title)
                for i in range(len(report_columns)-1):
                    col_order_class = i + 4
                    value = element.find(class_='col-order-class-'+str(col_order_class))
                    if value is not None:
                        value = value.find(class_='monetary-field-default')
                        value = float(value['title']) if value is not None and value.has_attr('title') else 0.0
                        value *= multiple
                    else:
                        value = 0.0
                    pd_element.append(value)
                '''
                prev_value = element.find(class_='col-order-class-5')
                prev_value = prev_value.find(class_='monetary-field-default')
                prev_value = float(prev_value['title']) if prev_value is not None and prev_value.has_attr('title') else 0.0
                prev_value *= multiple
                pd_element.append(prev_value)
                '''
                # Add the table row
                pd_balance_sheet.append(pd_element)
        pd_balance_sheet = pd.DataFrame(pd_balance_sheet, columns=report_columns)
        pd_balance_sheet.set_index(report_columns[0], inplace=True)
        # pd_balance_sheet.to_excel(self.companies_path /  'Balance_Sheet.xlsx', sheet_name='Balance Sheet')

        #print([c.name for c in balance_sheet.children])

        ###Remove after testing the method
        # Save the results to a file
        # save_path = self.companies_path / 'Report_Sample.html'
        # with open(save_path, 'w', encoding='utf-8') as f:
        #     f.write(report)

        return pd_balance_sheet

    def save_company_financials(self, ticker: str):
        # Standardize the parameter
        ticker = standardize_ticker(ticker)

        # Get the indices for the financials from the KAP website
        mkk_id = self.get_mkk_id(ticker)
        company_filter_site = FILTER_SITE + '/' + mkk_id + '/FR/365'
        report_loaded = False
        while not report_loaded:
            reports_text = self.r.get(company_filter_site)
            try:
                reports_json = json.loads(reports_text.text)
                report_loaded = True
            except Exception:
                print('JSON report not loaded for', ticker)
                self.refresh_r()
                time.sleep(30)
        with open(self.companies_path / 'Report_Filter_Sample.json', 'w', encoding='utf-8') as f:
            json.dump(reports_json, f, ensure_ascii=False, indent='\t')
        
        # Filter the financial reports to get indices
        reports_financial = [report for report in reports_json if report['basic']['disclosureCategory'] == 'FR']
        report_indices = [report['basic']['disclosureIndex'] for report in reports_financial]
        report_years = [report['basic']['year'] for report in reports_financial]
        report_months = [report['basic']['period'] for report in reports_financial]

        # Filter the reports to filter out solo financials where consolidated is present
        # Get the report periods
        report_years = [report['basic']['year'] for report in reports_financial]
        report_months = [report['basic']['period'] for report in reports_financial]
        report_periods = [to_quarter(year, month) for year, month in zip(report_years, report_months)]
        # Find the unique periods
        first_indices = {}
        periods_unique = [True] * len(report_periods)
        for idx, period in enumerate(report_periods):
            # First encounter
            if period not in first_indices:
                first_indices[period] = idx
            # Duplicate encounter
            else:
                periods_unique[idx] = False
                periods_unique[first_indices[period]] = False
        try:
            # Filter the solo periods out
            reports_financial = [report for unique, report in zip(periods_unique, reports_financial) 
                                if unique or not is_solo(report)]
            solo_filtered = True
            # Update other parts
            report_indices = [report['basic']['disclosureIndex'] for report in reports_financial]
            report_years = [report['basic']['year'] for report in reports_financial]
            report_months = [report['basic']['period'] for report in reports_financial]
        # Summary is not present in all reports
        except KeyError:
            solo_filtered = False

        # Get the financial reports as pandas objects
        for idx, year, month, unique in zip(report_indices, report_years, report_months, periods_unique):
            if not self.__report_exists(ticker, year, month):
                report = self.r.get(DISCLOSURE_SITE + '/' + str(idx)).text
                # The case when the filtering is already done or there are no repetitions
                if solo_filtered or unique:
                    report_saved = self.__save_report(report, ticker, year, month)
                # The case when the filtering needs to be done with saving the report
                else:
                    report_saved = self.__save_report(report, ticker, year, month, check_solo=True)
                if report_saved:
                    print('Report', to_quarter(year, month), 'for', ticker, 'saved.')
            else:
                print('Report', to_quarter(year, month), 'for', ticker, 'already exists.')

    def get_company_financials(self, ticker: str, update=True):
        # Standardize the ticker input
        ticker = standardize_ticker(ticker)

        # Update the data
        company_path = self.__get_save_path(ticker)
        # If the update option is chosen, update the data
        if update:
            self.save_company_financials(ticker)
        # Check if the data exists. if not, update the financials
        elif not (company_path.is_dir() and len(list(company_path.glob('*.xlsx'))) > 0):
            self.save_company_financials(ticker)
        # Get the data from the file path
        financial_tables = {}
        for financial_xl in company_path.glob('*.xlsx'):
            financial_period = financial_xl.name[-11:-5]
            financial_tables[financial_period] = pd.read_excel(financial_xl, sheet_name=None)

        return financial_tables

    def __report_exists(self, ticker, year, month) -> bool:
        report_path = self.__get_save_path(ticker)
        # The path should exist
        if not report_path.is_dir():
            return False
        # The path should have the file
        report_file = report_path / ('Financials_'+ticker+'_'+to_quarter(year, month)+'.xlsx')
        return report_file.is_file()

    def __get_save_path(self, ticker):
        return self.companies_path / 'Companies' / ticker

