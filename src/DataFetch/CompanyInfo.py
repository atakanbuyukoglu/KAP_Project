# Request related imports
from .Helpers.RequestWrapper import Request
from requests.exceptions import RequestException

# File related imports
import json
from pathlib import Path

# Parsing imports
from bs4.element import Tag
from bs4 import BeautifulSoup
import re

# Internal imports
from .Helpers.utils import standardize_ticker

# Constants related to the KAP website
# KAP Links
KAP_SITE = "https://www.kap.org.tr"
COMPANY_LIST_SITE = "https://www.kap.org.tr/tr/bist-sirketler"

class CompanyInfo:
    
    def __init__(self, ticker, name, link, auditor, city, kap_id, mkk_id=None, share_count=None) -> None:
        # Initialize the info dictionary to store attribute values
        self.info = {}

        # Set initial values for attributes using __setattr__ method
        self.ticker = ticker
        self.name = name
        self.link = link
        self.auditor = auditor
        self.city = city
        self.kap_id = kap_id
        self.mkk_id = mkk_id
        self.share_count = share_count

    def get_mkk_id(self, session=None):
        # Return the value if it is not None
        if self.mkk_id is not None:
            return self.mkk_id
        # If the session is not given, initialize it
        if session is None:
            session = Request()
        
        # Get the MKK ID from the KAP website
        resp = session.get(url=self.link)
        soup = BeautifulSoup(resp.text, 'html.parser')
        self.mkk_id = soup.select('img.comp-logo')[0]['src'].split('/')[-1]
        return self.mkk_id
    
    def get_share_count(self, session=None, reset=False):
        """
        Retrieves and updates the share count for this company.

        Args:
            session: The session for requesting data from the KAP website

        Returns:
            float: The retrieved or substituted share count.
        """
        # Return the value if it is not None and reset parameter is not set
        if self.share_count is not None and not reset:
            return self.share_count
        # If the session is not given, initialize it
        if session is None:
            session = Request()

        url = self.link.replace('ozet', 'genel')
        # Get the share count from the KAP website
        try:
            response = session.get(url=url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            share_count_tag = soup.find('div', string=' Ödenmiş/Çıkarılmış Sermaye ')
            if share_count_tag:
                share_count_tag = share_count_tag.parent.next_sibling.next_sibling
                share_count = float(share_count_tag.contents[1].string)
            else:
                raise ValueError("Share count tag not found")
        
        except RequestException as e:
            print(f"Network error occurred while requesting share count for {self.ticker}: {e}")
            share_count = 1
        except (ValueError, IndexError) as e:
            print(f"Error processing share count for {self.ticker}: {e}")
            share_count = 1

        # Update the info and return it
        self.share_count = share_count
        return share_count


    def update(self, other: 'CompanyInfo'):
        """
        Update the attributes of the current object based on another CompanyInfo object.
        Only non-None values from the other object are used for updating.
        """
        if not isinstance(other, CompanyInfo):
            raise ValueError("The argument must be an instance of CompanyInfo")

        # Iterate through the other object's info dictionary
        for key, value in other.info.items():
            if value is not None:
                # Use setattr to update the attribute and ensure __setattr__ is called
                setattr(self, key, value)
        return self

    def __getattr__(self, name):
        """
        Handle attribute access. This method is called if the requested attribute
        is not found in the usual places (i.e., it's not an instance attribute).
        """
        if name in self.info:
            return self.info[name]
        raise AttributeError(f"'CompanyInfo' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        """
        Handle attribute setting. This method ensures that attributes are stored
        in the info dictionary as well as being accessible as normal attributes.
        """
        if name == 'info':
            # Allow setting the info dictionary directly
            super().__setattr__(name, value)
        else:
            # Store the attribute in the info dictionary
            self.info[name] = value

    @staticmethod
    def init_from_kap_html(html_result):
        
        # Retrieve the information from HTML
        ticker = html_result.select('div.comp-cell._04.vtable a.vcell')[0].text
        ticker = standardize_ticker(ticker)
        name = html_result.select('div.comp-cell._14.vtable a.vcell')[0].text
        link = KAP_SITE + html_result.select('div.comp-cell._04.vtable a.vcell[href]')[0]['href']
        auditor = html_result.select('div.comp-cell._11.vtable a.vcell')[0].text
        city = html_result.select('div.comp-cell._12.vtable div.vcell')[0].text
        kap_id = int(re.search(r'\d+', link).group())
        
        # Initialize the info object and return it
        company = CompanyInfo(ticker, name, link, auditor, city, kap_id)
        return company
    
    @staticmethod
    def init_from_dict(info_dict):
        """
        Initialize a CompanyInfo object from a dictionary.
        """
        # Extract values from the dictionary
        ticker = info_dict.get('ticker', '')
        name = info_dict.get('name', '')
        link = info_dict.get('link', '')
        auditor = info_dict.get('auditor', '')
        city = info_dict.get('city', '')
        kap_id = info_dict.get('kap_id', '')
        mkk_id = info_dict.get('mkk_id', None)
        share_count = info_dict.get('share_count', None)

        # Create and return a new CompanyInfo object
        return CompanyInfo(ticker, name, link, auditor, city, kap_id, mkk_id, share_count)

    
    @staticmethod
    def init_empty():
        return CompanyInfo('', '', '', '', '', '')


class CompaniesInfo:

    def __init__(self, path) -> None:
        self.companies = {}
        self.path = Path(path)
        self.loaded = False
        self.r = Request()
        if self.path.is_file():
            self.load_from_json()
        else:
            self.get_from_kap()

    def add_company(self, company: CompanyInfo):
        self.companies[company.ticker] = company

    def update_company(self, company: CompanyInfo):
        company_current = self.companies.get(company.ticker, company)
        self.companies[company.ticker] = company_current.update(company)

    def get_from_kap(self, reset=False):
        # Reset the companies if the file is to be written from scratch.
        if reset:
            self.companies = {}
        # Get the company list website response
        companies_html = self.r.get(COMPANY_LIST_SITE)
        # Check the status code
        companies_html.raise_for_status()
        # Get the response in string version
        companies_html = companies_html.text
        # Turn the result into a list with an HTML element for each company
        soup = BeautifulSoup(companies_html, 'html.parser')
        company_list_html = soup.find_all('div', 'w-clearfix w-inline-block comp-row')

        # Get the attributes from the HTML output
        for company_html in company_list_html:
            company = CompanyInfo.init_from_kap_html(company_html)
            self.update_company(company)

        # Save the results to a JSON file
        self.save_as_json()

    def save_as_json(self):
        with open(self.path, 'w', encoding="utf-8") as f:
            json.dump(self.get_companies_dict(), f, ensure_ascii=False, indent=4)

    def load_from_json(self):
        with open(self.path, 'r', encoding="utf-8") as f:
            if self.path.stat().st_size > 0:
                self.update_from_dict(json.load(f))
        self.loaded = True

    def get_company(self, ticker:str):
        return self.companies[ticker]
    
    def __del__(self):
        self.save_as_json()
    
    def get_companies_dict(self):
        return {key: company.info for key, company in self.companies.items()}
    
    def update_from_dict(self, companies_dict: dict):
        for key, company_dict in companies_dict.items():
            company = CompanyInfo.init_from_dict(company_dict)
            self.update_company(company)

