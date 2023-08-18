from .KAP_Interface import KAPParser
from ..DataFetch.utils import standardize_ticker
import pandas as pd

# TODO: Write a code to list all ratios
class Company:

    def __init__(self, ticker, data_path) -> None:
        self.ticker = standardize_ticker(ticker)
        self.parser = KAPParser(data_path)

        self.financials = self.parser.get_financials(self.ticker)
        self.balance_sheet = self.__get_balance_sheet()
        self.income_statement = self.__get_income_statement()
        self.cash_flow_statement = self.__get_cash_flow_statement()
        self.yearly_balance_sheet = self.__get_balance_sheet(yearly=True)
        self.yearly_income_statement = self.__get_income_statement(yearly=True)
        self.yearly_cash_flow_statement = self.__get_cash_flow_statement(yearly=True)

    def __get_balance_sheet(self, yearly=False):
        # Get the latest financial report
        if yearly:
            financials = {period: report for period, report in self.financials.items() if 'Q4' in period}
        else:
            financials = self.financials
        latest_report = financials[max(financials)]
        # Find the table item with the desired name
        item_name = 'Nakit ve Nakit Benzerleri'
        balance_sheet = None
        for table_name, table in latest_report.items():
            table_column = table[table_name].tolist()
            if item_name in table_column:
                balance_sheet = table.rename(columns={table_name: 'Item'})
                balance_sheet.set_index('Item', inplace=True)

        return balance_sheet

    def __get_income_statement(self, yearly=False):
        # Get the latest financial report
        if yearly:
            financials = {period: report for period, report in self.financials.items() if 'Q4' in period}
        else:
            financials = self.financials
        latest_report = financials[max(financials)]
        # Find the table item with the desired name
        item_name = 'Hasılat'
        income_statement = None
        for table_name, table in latest_report.items():
            table_column = table[table_name].tolist()
            if item_name in table_column:
                income_statement = table.rename(columns={table_name: 'Item'})
                income_statement.set_index('Item', inplace=True)

        return income_statement
    
    def __get_cash_flow_statement(self, yearly=False):
        # Get the latest financial report
        if yearly:
            financials = {period: report for period, report in self.financials.items() if 'Q4' in period}
        else:
            financials = self.financials
        latest_report = financials[max(financials)]
        # Find the table item with the desired name
        item_name = 'DÖNEM BAŞI NAKİT VE NAKİT BENZERLERİ'
        cash_flow_statement = None
        for table_name, table in latest_report.items():
            table_column = table[table_name].tolist()
            if item_name in table_column:
                cash_flow_statement = table.rename(columns={table_name: 'Item'})
                cash_flow_statement.set_index('Item', inplace=True)

        return cash_flow_statement

    ### Values from the balance sheet ###
    def get_cash(self):
        return self.balance_sheet.loc['Nakit ve Nakit Benzerleri'].iloc[0]
    def get_short_term_financial_debt(self):
        return self.balance_sheet.loc['Kısa Vadeli Borçlanmalar'].iloc[0]
    def get_long_term_financial_debt(self):
        return self.balance_sheet.loc['Uzun Vadeli Borçlanmalar'].iloc[0]
    def get_share_count(self):
        return self.balance_sheet.loc['Ödenmiş Sermaye'].iloc[0]
    def get_equity(self):
        return self.balance_sheet.loc['Ana Ortaklığa Ait Özkaynaklar'].iloc[0]
    def get_noncontrolling_equity(self):
        try:
            return self.balance_sheet.loc['Kontrol Gücü Olmayan Paylar'].iloc[0]
        except KeyError:
            return 0
    
    ### Values from the income statement ###
    def get_revenue(self, ttm=False):
        return self.__get_income_statement_value('Hasılat', ttm=ttm)
    def get_net_profit(self, ttm=False):
        return self.__get_income_statement_value('Ana Ortaklık Payları', ttm=ttm)
    def get_noncontrolling_profit(self, ttm=False):
        try:
            return self.__get_income_statement_value('Kontrol Gücü Olmayan Paylar', ttm=ttm)
        except KeyError:
            return 0
    def get_gross_profit(self, ttm=False):
        return self.__get_income_statement_value('BRÜT KAR (ZARAR)', ttm=ttm)
    def get_operating_profit(self, ttm=False):
        return self.__get_income_statement_value('ESAS FAALİYET KARI (ZARARI)', ttm=ttm)
    def get_other_operating_income(self, ttm=False):
        return self.__get_income_statement_value('Esas Faaliyetlerden Diğer Gelirler', ttm=ttm)
    def get_other_operating_expense(self, ttm=False):
        return self.__get_income_statement_value('Esas Faaliyetlerden Diğer Giderler', ttm=ttm)
    
    def __get_income_statement_value(self, value_name, ttm=False, priority=0):
        value = self.income_statement.loc[value_name]
        # Handle multiple occurrences
        if type(value) == pd.DataFrame:
            value = value.iloc[priority]
        if ttm:
            value_year = self.yearly_income_statement.loc[value_name]
            # Handle multiple occurrences
            if type(value_year) == pd.DataFrame:
                value_year = value_year.iloc[priority]
            return value_year.iloc[0] + value.iloc[0] - value.iloc[1]
        else:
            return value.iloc[0]
    
    ### Values from the cash flow statement ###
    def get_amortization(self, ttm=False):
        return self.__get_cash_flow_statement_value('Amortisman ve İtfa Gideri İle İlgili Düzeltmeler', ttm=ttm)

    def __get_cash_flow_statement_value(self, value_name, ttm=False):
        value = self.cash_flow_statement.loc[value_name]
        if ttm:
            value_year = self.yearly_cash_flow_statement.loc[value_name].iloc[0]
            return value_year + value.iloc[0] - value.iloc[1]
        else:
            return value.iloc[0]
    
    ### Values calculated using the data from the tables
    def get_controlling_equity_ratio(self):
        equity = self.get_equity()
        return equity / (equity + self.get_noncontrolling_equity())
    def get_net_cash(self, control_adjusted=False):
        control_multiplier = self.get_controlling_equity_ratio() if control_adjusted else 1.0
        net_cash = self.get_cash() - self.get_short_term_financial_debt() - self.get_long_term_financial_debt()
        return control_multiplier * net_cash
    
    def get_controlling_profit_ratio(self):
        profit = self.get_net_profit()
        return profit / (profit + self.get_noncontrolling_profit())
    def get_basic_operating_income(self, control_adjusted=False, ttm=False):
        control_multiplier = self.get_controlling_profit_ratio() if control_adjusted else 1.0
        basic_operating_income = self.get_operating_profit(ttm=ttm) - self.get_other_operating_income(ttm=ttm) - self.get_other_operating_expense(ttm=ttm)
        return control_multiplier * basic_operating_income
    def get_ebitda(self, control_adjusted=False, ttm=False):
        control_multiplier = self.get_controlling_profit_ratio() if control_adjusted else 1.0
        ebitda = self.get_basic_operating_income(ttm=ttm) + self.get_amortization(ttm=ttm)
        return control_multiplier * ebitda
    
    ### Valuation methods
    def ebitda_valuation(self, multiple=10, control_adjusted=True):
        return ((self.get_ebitda(ttm=True, control_adjusted=control_adjusted) * multiple) + self.get_net_cash(control_adjusted=control_adjusted)) / self.get_share_count()

