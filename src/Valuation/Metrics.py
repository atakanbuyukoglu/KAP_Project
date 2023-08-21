from .KAP_Interface import KAPParser
from ..DataFetch.utils import standardize_ticker
import pandas as pd

class Company:

    def __init__(self, ticker, data_path, update=True) -> None:
        self.ticker = standardize_ticker(ticker)
        self.parser = KAPParser(data_path)

        self.financials = self.parser.get_financials(self.ticker, update=update)
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
        if financials:
            latest_report = financials[max(financials)]
        else:
            return None
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
        if financials:
            latest_report = financials[max(financials)]
        else:
            return None
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
        if financials:
            latest_report = financials[max(financials)]
        else:
            return None
        # Find the table item with the desired name
        item_name = 'DÖNEM BAŞI NAKİT VE NAKİT BENZERLERİ'
        cash_flow_statement = None
        for table_name, table in latest_report.items():
            table_column = table[table_name].tolist()
            if item_name in table_column:
                cash_flow_statement = table.rename(columns={table_name: 'Item'})
                cash_flow_statement.set_index('Item', inplace=True)

        return cash_flow_statement

    def get_share_count(self):
        return self.parser.get_share_count(self.ticker)

    ### Values from the balance sheet ###
    def get_cash(self):
        return self.__get_balance_sheet_value('Nakit ve Nakit Benzerleri')
    def get_inventories(self):
        return self.__get_balance_sheet_value('Stoklar')
    def get_short_term_investments(self):
        return self.__get_balance_sheet_value('Finansal Yatırımlar')
    def get_accounts_receivable(self):
        return self.__get_balance_sheet_value('Ticari Alacaklar')
    def get_cash_paid_expenses(self):
        return self.__get_balance_sheet_value('Peşin Ödenmiş Giderler')
    def get_long_term_investments(self):
        return self.__get_balance_sheet_value('Finansal Yatırımlar', priority=1)
    def get_tangible_assets(self):
        return self.__get_balance_sheet_value('Maddi Duran Varlıklar')
    def get_intangible_assets(self):
        return self.__get_balance_sheet_value('Maddi Olmayan Duran Varlıklar')
    def get_noncurrent_cash_paid_expenses(self):
        return self.__get_balance_sheet_value('Peşin Ödenmiş Giderler', priority=1)
    def get_use_right_assets(self):
        return self.__get_balance_sheet_value('Kullanım Hakkı Varlıkları')
    def get_real_estate(self):
        return self.__get_balance_sheet_value('Yatırım Amaçlı Gayrimenkuller')
    def get_equity_investments(self):
        return self.__get_balance_sheet_value('Özkaynak Yöntemiyle Değerlenen Yatırımlar')
    def get_current_assets(self):
        return self.__get_balance_sheet_value('TOPLAM DÖNEN VARLIKLAR')
    def get_noncurrent_assets(self):
        return self.__get_balance_sheet_value('TOPLAM DURAN VARLIKLAR')

    def get_accounts_payable(self):
        return self.__get_balance_sheet_value('Ticari Borçlar')
    def get_short_term_financial_debt(self):
        return self.__get_balance_sheet_value('Kısa Vadeli Borçlanmalar')
    def get_long_term_financial_debt(self):
        return self.__get_balance_sheet_value('Uzun Vadeli Borçlanmalar')
    def get_short_term_debt(self):
        return self.__get_balance_sheet_value('TOPLAM KISA VADELİ YÜKÜMLÜLÜKLER')
    def get_long_term_debt(self):
        return self.__get_balance_sheet_value('TOPLAM UZUN VADELİ YÜKÜMLÜLÜKLER')
    def get_total_debt(self):
        return self.__get_balance_sheet_value('TOPLAM YÜKÜMLÜLÜKLER')

    def get_equity(self):
        return self.__get_balance_sheet_value('Ana Ortaklığa Ait Özkaynaklar')
    def get_noncontrolling_equity(self):
        try:
            return self.__get_balance_sheet_value('Kontrol Gücü Olmayan Paylar')
        except KeyError:
            return 0
    
    def __get_balance_sheet_value(self, value_name, priority=0):
        try:
            value = self.balance_sheet.loc[value_name]
        except KeyError:
            return 0.0
        # Handle multiple occurrences
        if type(value) == pd.DataFrame:
            value = value.iloc[priority]
        # High count without multiple occurrences
        elif priority > 0:
            return 0.0
        return value.iloc[0]
    
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
        try:
            value = self.income_statement.loc[value_name]
        except KeyError:
            return 0.0
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
        try:
            value = self.cash_flow_statement.loc[value_name]
        except KeyError:
            return 0.0
        if ttm:
            value_year = self.yearly_cash_flow_statement.loc[value_name].iloc[0]
            return value_year + value.iloc[0] - value.iloc[1]
        else:
            return value.iloc[0]
    
    ### Values calculated using the data from the tables
    def get_controlling_equity_ratio(self):
        equity = self.get_equity()
        control_equity = equity / (equity + self.get_noncontrolling_equity())
        return min(1.0, control_equity)
    def get_net_cash(self, control_adjusted=False):
        control_multiplier = self.get_controlling_equity_ratio() if control_adjusted else 1.0
        net_cash = self.get_cash() + self.get_long_term_investments() - self.get_short_term_financial_debt() - self.get_long_term_financial_debt()
        return control_multiplier * net_cash
    def get_investments(self, control_adjusted=False):
        control_multiplier = self.get_controlling_equity_ratio() if control_adjusted else 1.0
        investments = self.get_short_term_investments() + self.get_long_term_investments() + self.get_equity_investments()
        return control_multiplier * investments
    def get_working_capital(self, control_adjusted=False):
        control_multiplier = self.get_controlling_equity_ratio() if control_adjusted else 1.0
        working_capital = self.get_inventories() + self.get_accounts_receivable() - self.get_accounts_payable()
        return control_multiplier * working_capital
    def get_noncurrent_operating_assets(self, control_adjusted = False):
        control_multiplier = self.get_controlling_equity_ratio() if control_adjusted else 1.0
        # Remove the assets related to the operations
        assets = self.get_tangible_assets() + self.get_intangible_assets() + self.get_noncurrent_cash_paid_expenses() + self.get_use_right_assets()
        return control_multiplier * assets
    def get_net_assets_for_ev(self, control_adjusted=False):
        control_multiplier = self.get_controlling_equity_ratio() if control_adjusted else 1.0
        # Remove the assets related to the operations
        net_assets = self.get_equity() - self.get_noncurrent_operating_assets() - self.get_working_capital()
        return control_multiplier * net_assets
    
    def get_controlling_profit_ratio(self):
        profit = self.get_net_profit()
        control_profit = profit / (profit + self.get_noncontrolling_profit())
        return min(1.0, control_profit)
    def get_basic_operating_income(self, control_adjusted=False, ttm=False):
        control_multiplier = self.get_controlling_profit_ratio() if control_adjusted else 1.0
        basic_operating_income = self.get_operating_profit(ttm=ttm) - self.get_other_operating_income(ttm=ttm) - self.get_other_operating_expense(ttm=ttm)
        return control_multiplier * basic_operating_income
    def get_ebitda(self, control_adjusted=False, ttm=False):
        control_multiplier = self.get_controlling_profit_ratio() if control_adjusted else 1.0
        ebitda = self.get_basic_operating_income(ttm=ttm) + self.get_amortization(ttm=ttm)
        return control_multiplier * ebitda
    def get_adjusted_ebitda(self, control_adjusted=True, ttm=False):
        ebitda = self.get_ebitda(control_adjusted=control_adjusted, ttm=ttm)
        return ebitda
    
    ### Valuation methods
    def ebitda_valuation(self, multiple=10, control_adjusted=True):
        return ((self.get_adjusted_ebitda(ttm=True, control_adjusted=control_adjusted) * multiple) + self.get_net_assets_for_ev(control_adjusted=control_adjusted)) / self.get_share_count()
    def book_value_valuation(self, multiple=1.0):
        return multiple * self.get_equity() / self.get_share_count()
    def default_valuation(self, extra_multiple = 1.0):
        ticker_info = self.parser.get_info(self.ticker)
        if 'YATIRIM ORTAKLIĞI' in ticker_info.loc['NAME']:
            try:
                return extra_multiple * self.book_value_valuation()
            except:
                print('Book valuation not found for', self.ticker)
                return 0.0
        else:
            try:
                return extra_multiple * self.ebitda_valuation()
            except:
                print('Ebitda valuation not found for', self.ticker)
                try:
                    return extra_multiple * self.book_value_valuation()
                except:
                    print('Book valuation not found for', self.ticker)
                    return 0.0
                    
