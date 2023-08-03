from .RequestWrapper import Request
import bs4
from bs4 import BeautifulSoup
import re
from openpyxl import Workbook
from .utils import auto_fit_columns

# Constants related to the KAP website
KAP_SITE = "https://www.kap.org.tr"
COMPANY_LIST_SITE = "https://www.kap.org.tr/tr/bist-sirketler"
FILTER_SITE = "https://www.kap.org.tr/tr/FilterSgbf/FILTERSGBF"
# Sleep time between each request, in seconds
SLEEP_TIME = 5.0

# An interface for the KAP website
# Try to keep as high level as possible
class KAP:
    def __init__(self, data_path) -> None:
        self.companies_path = data_path
        self.r = Request(sleep_time=SLEEP_TIME)
 
    # Save the legal information about companies to the database about companies
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
        wb.save(self.companies_path /  'Company_Info.xlsx')
            

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



