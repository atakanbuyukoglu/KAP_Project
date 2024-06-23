# Parsing imports
from bs4 import BeautifulSoup
from bs4.element import Tag

# Miscellaneous imports
from pathlib import Path
import json

# Excel related imports
from openpyxl import Workbook
import pandas as pd

# Internal imports
from .Helpers.utils import standardize_ticker, to_quarter, is_empty_or_hidden
from .CompanyInfo import CompanyInfo


DISCLOSURE_SITE = "https://www.kap.org.tr/tr/Bildirim"
TEST_RESULTS_PATH = Path(__file__).parents[2] / 'Data' / 'Test_Results' / 'Reports'
CONSOLIDATED_STRING = 'Konsolide'



class KAPReport:

    def __init__(self, ticker:str, info:CompanyInfo, path, year:str=None, month:str=None, period:str=None) -> None:
        # Get the standardized ticker
        self.ticker = standardize_ticker(ticker)
        # Get the company information
        self.info = info
        # Get the save and load path for the company and create the path as a directory
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        # Get the report period
        # The case where it is obtained from month and year
        if period is None:
            if year is None or month is None:
                raise ValueError(f"Year and month info must be given if period is not given for {ticker}.")
            else:
                self.period = to_quarter(year, month)
        # The case where it is obtained from the period
        else:
            self.period = period

    def get_report(self, report_index):
        # Try to get the consolidated report
        report_name = self.get_report_name(consolidated=True)
        report_exists = (self.path / report_name).is_file()
        return_value = None
        if report_exists:
            report_metadata = pd.read_excel(self.path / report_name, sheet_name='Metadata')
            # Get the value corresponding to 'report_index'
            report_index_value = report_metadata.loc[report_metadata['Metadata'] == 'report_index', 'Value'].values[0]
            if report_index_value == report_index:
                return pd.read_excel(self.path / report_name)
            else:
                return_value = 'Consolidated'
        # Try to get the solo report if consolidated does not exist or is not the right one
        report_name = self.get_report_name(consolidated=False)
        report_exists = (self.path / report_name).is_file()
        # Return the report if it exists
        if report_exists:
            report_metadata = pd.read_excel(self.path / report_name, sheet_name='Metadata')
            # Get the value corresponding to 'report_index'
            report_index_value = report_metadata.loc[report_metadata['Metadata'] == 'report_index', 'Value'].values[0]
            if report_index_value == report_index:
                return pd.read_excel(self.path / report_name)
            else:
                return_value = 'Solo'
        # Return None if the report does not exist
        return return_value

    def save_report(self, session, report_index):
        # A list of pandas DataFrames for the tables
        pd_reports = []
        # Get the report from the website as HTML
        report = session.get(DISCLOSURE_SITE + '/' + str(report_index)).text
        # Get the HTML file to the parser
        soup = BeautifulSoup(report, 'html.parser')
        
        
        # Find the currency and its multiple
        report_info = soup('td', class_='financial-header-title', limit=2) # The header for currency and report type
        # Get to the elements from headers
        try:
            currency = report_info[0].next_sibling.next_sibling
            report_type = report_info[1].next_sibling.next_sibling
        # This happens when the financial report is not properly summmarized in the disclosure. Example: DOCO
        except IndexError:
            # Just save the metadata to not try to download it next time
            with pd.ExcelWriter(self.get_report_path(consolidated=True)) as writer:
                metadata = pd.DataFrame({
                    'Metadata': ['report_index'],
                    'Value': [report_index]
                })
                metadata.to_excel(writer, sheet_name='Metadata')
                return
        # Get the currency multiple
        currency_multiple = 10 ** str(currency.string).count('0')
        # Get the report type
        report_type = str(report_type.string)
        consolidated = report_type == CONSOLIDATED_STRING

        # Save the HTML file for later use
        test_path = TEST_RESULTS_PATH / self.ticker
        test_path.mkdir(parents=True, exist_ok=True)
        with open(test_path / self.get_report_name(consolidated=consolidated).replace('.xlsx', '.html'), 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

        # Get all financial tables
        financial_tables = soup('table', class_='financial-table')
        # Loop through each table: Balance sheet, income statement etc.
        report_idx = 1
        for table_idx, financial_table in enumerate(financial_tables):
            # Get to the body part
            table_body = financial_table.tbody
            # Save the body in the test for later use
            with open(test_path / f'Table_{table_idx}.html', 'w', encoding='utf-8') as f:
                f.write(table_body.prettify())
            # First, get the table name
            financial_table_row = financial_table.find('tr', class_='abstract-row')
            financial_table_cell = financial_table_row.find(class_='taxonomy-field-title')
            financial_table_name = financial_table_cell.find(class_='content-tr').get_text(strip=True)
            # DO NOT USE THE TABLE NAME FOR NOW: TABLE NAME TOO LONG
            financial_table_name = 'Table ' + str(report_idx)
            report_idx += 1
            # Then, get the table columns
            columns = [financial_table_name] # First column is the table name
            # Add the date headers to the columns
            financial_table_info = financial_table.find('tr')
            financial_table_headers = financial_table_info.find_all(class_='context-header')
            for table_header in financial_table_headers:
                header = table_header.find(class_='content-tr')
                header = str(header.contents[-1]).strip()
                columns.append(header)
            # Get the pandas variable for the report
            pd_reports.append(self.__table_2_pandas(table_body, columns, currency_multiple))
        
        # Save the financials to an Excel file
        with pd.ExcelWriter(self.get_report_path(consolidated=consolidated)) as writer:
            report_idx = 1
            for report in pd_reports:
                financial_table_name = 'Table ' + str(report_idx)
                report.to_excel(writer, sheet_name=financial_table_name)
                report_idx += 1
            # Save the metadata to one last sheet
            metadata = pd.DataFrame({
                'Metadata': ['report_index'],
                'Value': [report_index]
            })
            metadata.to_excel(writer, sheet_name='Metadata')
            
        return True

    def get_report_path(self, consolidated=False):
        return self.path / self.get_report_name(consolidated=consolidated)

    def exists(self):
        # The path should exist
        if not self.path.is_dir():
            return False
        # The path should have the file
        return self.get_report_path(consolidated=True).is_file() or \
                self.get_report_path(consolidated=False).is_file()
    
    def get_report_name(self, consolidated = False):
        cons = 'Kons' if consolidated else 'Solo'
        return f'Financials_{self.ticker}_{cons}_{self.period}.xlsx'

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
                # Add the table row
                pd_balance_sheet.append(pd_element)
        pd_balance_sheet = pd.DataFrame(pd_balance_sheet, columns=report_columns)
        pd_balance_sheet.set_index(report_columns[0], inplace=True)

        return pd_balance_sheet