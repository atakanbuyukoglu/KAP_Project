# Request related imports
from .Helpers.RequestWrapper import Request

# Miscellaneous imports
import json
from pathlib import Path
from datetime import date, timedelta

KAP_SEARCH_URL = "https://www.kap.org.tr/tr/api/memberDisclosureQuery"
EMPTY_QUERY_PATH = Path(__file__).parents[2] / 'Data' / 'Empty_Search_Query.json'
TEST_RESULTS_PATH = Path(__file__).parents[2] / 'Data' / 'Test_Results' / 'Search'

class KAPSearch:
    def __init__(self, sleep_time=5.0) -> None:
        
        self.r = Request(sleep_time=sleep_time)

    def get_json_query(self):
        with open(EMPTY_QUERY_PATH, 'r', encoding='utf-8') as f:
            query = json.load(f)
        #with open(EMPTY_QUERY_PATH, 'w', encoding="utf-8") as f:
        #    json.dump(query, f, ensure_ascii=False, indent=4)
        return query
    
    def search_financials(self, start_date:date, end_date:date):
        # Allow supporting string input
        start_date = date.fromisoformat(str(start_date))
        end_date = date.fromisoformat(str(end_date))
        # Create the empty query
        query = self.get_json_query()
        # Set the dates for the query
        query["fromDate"] = str(start_date)
        query["toDate"] = str(end_date)
        # Set the query type, financial reports
        query['disclosureClass'] = 'FR'
        # If an error happens in this index, it is obtained from https://www.kap.org.tr/tr/api/listDisclosureTitles/FR/Y
        query['subjectList'].append("4028328c594bfdca01594c0af9aa0057") # Index for financial reports, no other parts needed
        # Set the member state, only publicly traded companies
        query['memberType'] = 'IGS' # İşlem gören şirketler

        resp = self.r.post(KAP_SEARCH_URL, json=query)
        resp_json = json.loads(resp.text)

        with open(TEST_RESULTS_PATH / 'search_financials.json', 'w', encoding="utf-8") as f:
            json.dump(resp_json, f, ensure_ascii=False, indent=4)

        return resp_json
    
    def search_ticker_financials(self, ticker_mkk_id:str):
        end_date = date.today()
        start_date = end_date.replace(year=end_date.year - 1) + timedelta(days=1)
        # Create the empty query
        query = self.get_json_query()
        # Set the dates for the query
        query["fromDate"] = str(start_date)
        query["toDate"] = str(end_date)
        # Set the query type, financial reports
        query['disclosureClass'] = 'FR'
        # If an error happens in this index, it is obtained from https://www.kap.org.tr/tr/api/listDisclosureTitles/FR/Y
        query['subjectList'].append("4028328c594bfdca01594c0af9aa0057") # Index for financial reports, no other parts needed
        # Set the member state, only publicly traded companies
        query['memberType'] = 'IGS' # İşlem gören şirketler
        # Set the ticker to be searched
        query['mkkMemberOidList'] = [ticker_mkk_id]

        resp = self.r.post(KAP_SEARCH_URL, json=query)
        resp_json = json.loads(resp.text)

        with open(TEST_RESULTS_PATH / 'search_ticker_financials.json', 'w', encoding="utf-8") as f:
            json.dump(resp_json, f, ensure_ascii=False, indent=4)
        
        return resp_json

