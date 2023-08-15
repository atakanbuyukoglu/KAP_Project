# Request related imports
from .RequestWrapper import Request
import bs4
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
import json
from pathlib import Path

# Excel related imports
from openpyxl import Workbook
import pandas as pd

# Internal imports
from .utils import auto_fit_columns, standardize_ticker

# Constants related to the KAP website
# KAP Links
KAP_SITE = "https://www.kap.org.tr"
COMPANY_LIST_SITE = "https://www.kap.org.tr/tr/bist-sirketler"
FILTER_SITE = "https://www.kap.org.tr/tr/FilterSgbf/FILTERSGBF"
DISCLOSURE_SITE = "https://www.kap.org.tr/tr/Bildirim"

# TODO: Make this generic
# KAP HTML attributes
KAP_FILTER_NAME = {
    'balance_sheet': 'tbl_general_role_210',
    'income_statement': 'tbl_general_role_310',
    'cash_flow_statement': 'tbl_general_role_520'
}

# Sleep time between each request, in seconds
SLEEP_TIME = 1.0

# An interface for the KAP website
# Try to keep as high level as possible
class KAP:
    def __init__(self, data_path) -> None:
        self.companies_path = Path(data_path)
        self.r = Request(sleep_time=SLEEP_TIME)

        self.company_info = None
 
    # Save the legal information about companies to the database about companies from the KAP website
    def save_company_info(self) -> None:
        ### GETTING THE HTML RESULTS

        # Get the company list website response
        companies_html = self.r.get(COMPANY_LIST_SITE)
        # Check the status code
        companies_html.raise_for_status()
        # Get the response in string version
        companies_html = companies_html.text
        # Turn the result into a list with an HTML element for each company
        soup = BeautifulSoup(companies_html, 'html.parser')
        company_list_html = soup.find_all('div', 'w-clearfix w-inline-block comp-row')

        ### CREATING THE EXCEL FILE FROM HTML RESULTS

        # Get the attributes from the HTML output
        companies_dict = {}
        for company_html in company_list_html:
            company_dict = KAP.__html_2_dict(company_html)
            companies_dict[company_dict['ticker']] = company_dict

        # Save the results to an XLSX File
        # Define the file
        wb = Workbook()
        # Define the first worksheet
        ws_info = wb.active
        ws_info.title = 'Info'
        # Write the table headers first
        for idx, company_key in enumerate(company_dict):
            ws_info.cell(1, idx+1).value = company_key.upper().replace('_', ' ')
        # Then write the table elements for each company
        for row_idx, company_dict in enumerate(companies_dict.values()):
            for col_idx, element in enumerate(company_dict.values()):
                ws_info.cell(row_idx+2, col_idx+1).value = element
        # Auto-adjust column width to fit content
        auto_fit_columns(ws_info)
        # Save the results to a file
        save_path = self.companies_path /  'Company_Info.xlsx'
        wb.save(save_path)
        # Return the information as a pandas object
        self.company_info = pd.read_excel(save_path).set_index('TICKER')
        return self.company_info

    # Get the company info object. If not initialized yet, initialize it first.
    def get_company_info(self):
        # Return the object if initialized
        if self.company_info is not None:
            return self.company_info
        return self.save_company_info()
    
    # Update the company info file according to the changes to the internal company_info object
    def __update_company_info(self):
        self.company_info.to_excel(self.companies_path /  'Company_Info.xlsx', sheet_name='Info')

    def __add_mkk_id(self, ticker: str):
        # Get the MKK ID from the KAP website
        resp = self.r.get(url=self.company_info.loc[ticker, 'LINK'])
        soup = BeautifulSoup(resp.text, 'html.parser')
        mkk_id = soup.select('img.comp-logo')[0]['src'].split('/')[-1]
        self.company_info.loc[ticker, 'MKK ID'] = mkk_id
        # Update the company info file with the new information
        self.__update_company_info()
        # Return the updated company info object
        return mkk_id

    def get_mkk_id(self, ticker: str):
        # Standardize the parameter
        ticker = standardize_ticker(ticker)

        # Initialize company info if not initialized yet
        self.get_company_info()

        # Add the MKK ID header if not added yet
        if 'MKK ID' not in self.company_info.columns:
            self.company_info['MKK ID'] = None
        
        # If the MKK ID is already added, return it
        mkk_id_set = self.company_info.loc[ticker, 'MKK ID']
        if mkk_id_set is not None:
            return mkk_id_set
        # Else, return the added MKK ID
        return self.__add_mkk_id(ticker)

    def __save_report(self, report, ticker):
        # Define the save path
        save_path = self.companies_path / 'Companies' / ticker
        save_path.mkdir(parents=True, exist_ok=True)

        # Parse the HTML file
        soup = BeautifulSoup(report, 'html.parser')
        financial_tables = soup('table', class_='financial-table')
        pd_reports = []
        report_date = None
        table_idx = 1
        for financial_table in financial_tables:
            # Get to the body part
            financial_table = financial_table.tbody

            # Define the headers to get the column names
            columns = []
            financial_table_tr = financial_table.find_all('tr', limit=2)
            financial_table_name = financial_table_tr[1]
            financial_table_name = financial_table_name.find(class_='taxonomy-field-title')
            # If the report name is not found, the table is not compatible
            if financial_table_name is None:
                continue
            financial_table_name = str(financial_table_name.find(class_='content-tr').string)
            financial_table_name = financial_table_name.strip()
            financial_table_name = 'Table ' + str(table_idx)
            columns.append(financial_table_name)
            # Add the date headers
            financial_table_info = financial_table_tr[0]
            financial_table_headers = financial_table_info.find_all(class_='context-header')
            header_now = financial_table_headers[0]
            header_now = header_now.find(class_='content-tr')
            header_now = str(header_now.contents[-1])
            header_now = header_now.strip()
            columns.append(header_now)
            header_prev = financial_table_headers[1]
            header_prev = header_prev.find(class_='content-tr')
            header_prev = str(header_prev.contents[-1])
            header_prev = header_prev.strip()
            columns.append(header_prev)
            # Save the report date if not done already
            if report_date is None:
                report_date = header_now
            
            # Get the pandas variable for the report
            pd_reports.append(self.__table_2_pandas(financial_table, columns))
            table_idx += 1

        # Save the financials to an Excel file
        with pd.ExcelWriter(save_path / ('Financials_'+ticker+'_'+report_date+'.xlsx')) as writer:
            for report in pd_reports:
                report.to_excel(writer, sheet_name=report.columns[0])
        
            


    def __table_2_pandas(self, report: Tag, report_columns: list):
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
                this_value = element.find(class_='col-order-class-4')
                this_value = this_value.find(class_='monetary-field-default')
                this_value = float(this_value['title']) if this_value is not None and this_value.has_attr('title') else 0.0
                pd_element.append(this_value)
                prev_value = element.find(class_='col-order-class-5')
                prev_value = prev_value.find(class_='monetary-field-default')
                prev_value = float(prev_value['title']) if prev_value is not None and prev_value.has_attr('title') else 0.0
                pd_element.append(prev_value)
                # Add the table row
                pd_balance_sheet.append(pd_element)
        pd_balance_sheet = pd.DataFrame(pd_balance_sheet, columns=report_columns)
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
        reports_text = self.r.get(company_filter_site)
        reports_json = json.loads(reports_text.text)
        with open(self.companies_path / 'Report_Sample.html', 'w', encoding='utf-8') as f:
            f.write(reports_text.text)
        # Filter the financial reports to get indices
        reports_financial = [report for report in reports_json if report['basic']['disclosureCategory'] == 'FR']
        report_indices = [report['basic']['disclosureIndex'] for report in reports_financial]

        # Get the financial reports as pandas objects
        for idx in report_indices:
            report = self.r.get(DISCLOSURE_SITE + '/' + str(idx)).text
            report = self.__save_report(report, ticker)

    @staticmethod
    def __html_2_dict(html_result: bs4.element.Tag):
        company_dict = {}

        ticker = html_result.select('div.comp-cell._04.vtable a.vcell')[0].text
        ticker = standardize_ticker(ticker)
        company_dict['ticker'] = ticker
        name = html_result.select('div.comp-cell._14.vtable a.vcell')[0].text
        company_dict['name'] = name
        link = html_result.select('div.comp-cell._04.vtable a.vcell[href]')[0]['href']
        company_dict['link'] = KAP_SITE + link
        auditor = html_result.select('div.comp-cell._11.vtable a.vcell')[0].text
        company_dict['auditor'] = auditor
        city = html_result.select('div.comp-cell._12.vtable div.vcell')[0].text
        company_dict['city'] = city
        kap_id = int(re.search(r'\d+', link).group())
        company_dict['kap_id'] = kap_id

        return company_dict



