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
from .utils import auto_fit_columns

# Constants related to the KAP website
KAP_SITE = "https://www.kap.org.tr"
COMPANY_LIST_SITE = "https://www.kap.org.tr/tr/bist-sirketler"
FILTER_SITE = "https://www.kap.org.tr/tr/FilterSgbf/FILTERSGBF"
DISCLOSURE_SITE = "https://www.kap.org.tr/tr/Bildirim"
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
        ticker = ticker.upper()

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

    def report_2_pandas(self, report):
        # Filter the report to get to the financial report
        filter_string = ''
        def filter_tables(tag: Tag):
            if not tag.name == 'table':
                return False
            if not tag.has_attr('class'):
                return False
            if filter_string not in tag['class']:
                return False
            return True
        soup = BeautifulSoup(report, 'html.parser')
        # Get the balance sheet
        filter_string = 'tbl_general_role_210015'
        balance_sheet = soup(filter_tables)[0]
        balance_sheet = balance_sheet.tbody
        balance_sheet_info = balance_sheet.find('tr')
        balance_sheet_headers = balance_sheet_info.find_all(class_='context-header')
        header_now = balance_sheet_headers[0]
        header_now = header_now.find(class_='content-tr')
        header_now = str(header_now.contents[-1])
        header_now = header_now.strip()
        header_prev = balance_sheet_headers[1]
        header_prev = header_prev.find(class_='content-tr')
        header_prev = str(header_prev.contents[-1])
        header_prev = header_prev.strip()
        # Get the table values
        pd_balance_sheet = []
        for element in balance_sheet.children:
            # Filter visible table elements
            if element.name == 'tr' and element.has_attr('class') and 'presentation-enabled' in element['class']:
                # Prepare the table row
                pd_element = []
                title = element.find(class_='taxonomy-field-title')
                title = str(title.find(class_='content-tr').string)
                title = title.strip()
                pd_element.append(title)
                this_value = element.find(class_='col-order-class-4')
                this_value = this_value.find(class_='monetary-field-default')
                this_value = float(this_value['title']) if this_value.has_attr('title') else 0.0
                pd_element.append(this_value)
                prev_value = element.find(class_='col-order-class-5')
                prev_value = prev_value.find(class_='monetary-field-default')
                prev_value = float(prev_value['title']) if prev_value.has_attr('title') else 0.0
                pd_element.append(prev_value)
                # Add the table row
                pd_balance_sheet.append(pd_element)
        pd_balance_sheet = pd.DataFrame(pd_balance_sheet, columns=['Kalem', header_now, header_prev])
        pd_balance_sheet.to_excel(self.companies_path /  'Balance_Sheet.xlsx', sheet_name='Balance Sheet')

        #print([c.name for c in balance_sheet.children])

        ###Remove after testing the method
        # Save the results to a file
        save_path = self.companies_path / 'Report_Sample.html'
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return pd_balance_sheet

    def save_company_financials(self, ticker: str):
        # Standardize the parameter
        ticker = ticker.upper()

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

        reports = []
        for idx in report_indices[:1]:
            report = self.r.get(DISCLOSURE_SITE + '/' + str(idx)).text
            report = self.report_2_pandas(report)
            reports.append(report)
        # Save the financials to an Excel file
        # Return the financials as a pandas object
        return reports[0]

    @staticmethod
    def __html_2_dict(html_result: bs4.element.Tag):
        company_dict = {}

        ticker = html_result.select('div.comp-cell._04.vtable a.vcell')[0].text
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



