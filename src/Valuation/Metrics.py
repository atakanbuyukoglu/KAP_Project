from .KAP_Interface import KAPParser
from ..DataFetch.utils import standardize_ticker

# TODO: Write a code to list all ratios
class Company:
    def __init__(self, ticker, data_path) -> None:
        self.ticker = standardize_ticker(ticker)
        self.parser = KAPParser(data_path)

        self.financials = self.parser.get_financials(self.ticker)
        self.balance_sheet = self.__get_balance_sheet()
        self.income_statement = self.__get_income_statement()
        self.cash_flow_statement = self.__get_cash_flow_statement()

    def __get_balance_sheet(self):
        # Get the latest financial report
        latest_report = self.financials[max(self.financials)]
        # Find the table item with the desired name
        item_name = 'Nakit ve Nakit Benzerleri'
        balance_sheet = None
        for table_name, table in latest_report.items():
            table_column = table[table_name].tolist()
            if item_name in table_column:
                balance_sheet = table.rename(columns={table_name: 'Item'})
                balance_sheet.set_index('Item', inplace=True)

        return balance_sheet

    def __get_income_statement(self):
        # Get the latest financial report
        latest_report = self.financials[max(self.financials)]
        # Find the table item with the desired name
        item_name = 'Hasılat'
        income_statement = None
        for table_name, table in latest_report.items():
            table_column = table[table_name].tolist()
            if item_name in table_column:
                income_statement = table.rename(columns={table_name: 'Item'})
                income_statement.set_index('Item', inplace=True)

        return income_statement
    
    def __get_cash_flow_statement(self):
        # Get the latest financial report
        latest_report = self.financials[max(self.financials)]
        # Find the table item with the desired name
        item_name = 'DÖNEM BAŞI NAKİT VE NAKİT BENZERLERİ'
        cash_flow_statement = None
        for table_name, table in latest_report.items():
            table_column = table[table_name].tolist()
            if item_name in table_column:
                cash_flow_statement = table.rename(columns={table_name: 'Item'})
                cash_flow_statement.set_index('Item', inplace=True)

        return cash_flow_statement

    def get_cash(self):
        return self.balance_sheet.loc['Nakit ve Nakit Benzerleri'].iloc[0]

