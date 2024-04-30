from .KAP_Interface import KAPParser
from ..DataFetch.Helpers.utils import standardize_ticker
import pandas as pd

# TODO: Fix the functions for yearly financials
class Company:

    def __init__(self, ticker, data_path, update=True) -> None:
        self.ticker = standardize_ticker(ticker)
        self.parser = KAPParser(data_path)

        self.last_quarter = None

        self.financials = self.parser.get_financials(self.ticker, update=update)
        self.balance_sheet = self.__get_balance_sheet()
        self.income_statement = self.__get_income_statement()
        self.cash_flow_statement = self.__get_cash_flow_statement()
        self.yearly_balance_sheet = self.__get_balance_sheet(yearly=True)
        self.yearly_income_statement = self.__get_income_statement(yearly=True)
        self.yearly_cash_flow_statement = self.__get_cash_flow_statement(yearly=True)
        self.prev_cash_flow_statement = self.__get_cash_flow_statement(previous=True)

    def __get_balance_sheet(self, yearly=False):
        # Get the latest financial report
        if yearly:
            financials = {period: report for period, report in self.financials.items() if 'Q4' in period}
        else:
            financials = self.financials
        if financials:
            if not yearly:
                self.last_quarter = int(max(financials)[-1])
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
    
    def __get_cash_flow_statement(self, yearly=False, previous=False):
        # Get the latest financial report
        if yearly:
            financials = {period: report for period, report in self.financials.items() if 'Q4' in period}
        elif previous:
            financials = self.financials.copy()
            if financials:
                del financials[max(financials)]
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

    def get_share_count(self, online: bool=False):
        return self.parser.get_share_count(self.ticker, online=online)

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
    def get_total_equity(self):
        return self.__get_balance_sheet_value('TOPLAM ÖZKAYNAKLAR')
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
    def get_revenue(self, ttm=False, quarter=False):
        return self.__get_income_statement_value('Hasılat', ttm=ttm, quarter=quarter)
    def get_net_profit(self, ttm=False, quarter=False):
        return self.__get_income_statement_value('Ana Ortaklık Payları', ttm=ttm, quarter=quarter)
    def get_noncontrolling_profit(self, ttm=False, quarter=False):
        try:
            return self.__get_income_statement_value('Kontrol Gücü Olmayan Paylar', ttm=ttm, quarter=quarter)
        except KeyError:
            return 0
    def get_gross_profit(self, ttm=False, quarter=False):
        return self.__get_income_statement_value('BRÜT KAR (ZARAR)', ttm=ttm, quarter=quarter)
    def get_operating_profit(self, ttm=False, quarter=False):
        return self.__get_income_statement_value('ESAS FAALİYET KARI (ZARARI)', ttm=ttm, quarter=quarter)
    def get_other_operating_income(self, ttm=False, quarter=False):
        return self.__get_income_statement_value('Esas Faaliyetlerden Diğer Gelirler', ttm=ttm, quarter=quarter)
    def get_other_operating_expense(self, ttm=False, quarter=False):
        return self.__get_income_statement_value('Esas Faaliyetlerden Diğer Giderler', ttm=ttm, quarter=quarter)
    
    def __get_income_statement_value(self, value_name, ttm=False, quarter=False, priority=0):
        try:
            value = self.income_statement.loc[value_name]
        except KeyError:
            return 0.0
        # Handle multiple occurrences
        if type(value) == pd.DataFrame:
            value = value.iloc[priority]
        if ttm:
            try:
                value_year = self.yearly_income_statement.loc[value_name]
                # Handle multiple occurrences
                if type(value_year) == pd.DataFrame:
                    value_year = value_year.iloc[priority]
                # Subtract the part not in TTM
                value_year = value_year.iloc[0] - value.iloc[1]
            except AttributeError:
                value_year = 0.0
            return value_year + value.iloc[0]
        elif quarter:
            return value.iloc[2]
        else:
            return value.iloc[0]
    
    ### Values from the cash flow statement ###
    def get_amortization(self, ttm=False, quarter=False):
        return self.__get_cash_flow_statement_value('Amortisman ve İtfa Gideri İle İlgili Düzeltmeler', ttm=ttm, quarter=quarter)

    def __get_cash_flow_statement_value(self, value_name, ttm=False, quarter=False, priority=0):
        try:
            value = self.cash_flow_statement.loc[value_name]
        except KeyError:
            return 0.0
        if ttm:
            try:
                value_year = self.yearly_cash_flow_statement.loc[value_name]
                # Handle multiple occurrences
                if type(value_year) == pd.DataFrame:
                    value_year = value_year.iloc[priority]
                # Subtract the part not in TTM
                value_year = value_year.iloc[0] - value.iloc[1]
            except AttributeError:
                value_year = 0.0
            return value_year + value.iloc[0]
        elif quarter:
            if self.last_quarter == 4:
                return value.iloc[0]
            else:
                try:
                    prev_value = self.prev_cash_flow_statement.loc[value_name]
                    return value.iloc[0] - prev_value.iloc[0]
                except KeyError:
                    return value.iloc[0] / self.last_quarter
        else:
            return value.iloc[0]
    
    ### Values calculated using the data from the tables
    def get_controlling_equity_ratio(self):
        equity = self.get_equity()
        control_equity = equity / (equity + self.get_noncontrolling_equity())
        control_equity = min(1.0, control_equity)
        control_equity = max(0.0, control_equity)
        return control_equity
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
        net_assets = self.get_total_equity() - self.get_noncurrent_operating_assets() - self.get_working_capital()
        return control_multiplier * net_assets
    
    def get_controlling_profit_ratio(self):
        profit = self.get_net_profit()
        control_profit = profit / (profit + self.get_noncontrolling_profit())
        control_profit = min(1.0, control_profit)
        control_profit = max(0.0, control_profit)
        return control_profit
    def get_basic_operating_income(self, control_adjusted=False, ttm=False, quarter=False):
        control_multiplier = self.get_controlling_profit_ratio() if control_adjusted else 1.0
        basic_operating_income = self.get_operating_profit(ttm=ttm, quarter=quarter) - self.get_other_operating_income(ttm=ttm, quarter=quarter) - self.get_other_operating_expense(ttm=ttm, quarter=quarter)
        return control_multiplier * basic_operating_income
    def get_ebitda(self, control_adjusted=False, ttm=False, quarter=False):
        control_multiplier = self.get_controlling_profit_ratio() if control_adjusted else 1.0
        ebitda = self.get_basic_operating_income(ttm=ttm, quarter=quarter) + self.get_amortization(ttm=ttm, quarter=quarter)
        return control_multiplier * ebitda
    def get_adjusted_ebitda(self, control_adjusted=True, ttm=False, quarter=False):
        ebitda = self.get_ebitda(control_adjusted=control_adjusted, ttm=ttm, quarter=quarter)
        return ebitda
    
    ### Valuation methods
    def ebitda_valuation(self, multiple=10, control_adjusted=True, quarter=False):
        quarter_multiplier = 4 if quarter else 1
        return (quarter_multiplier * self.get_adjusted_ebitda(ttm=False, quarter=quarter, control_adjusted=control_adjusted) * multiple + self.get_net_assets_for_ev(control_adjusted=control_adjusted)) / self.get_share_count()
    def book_value_valuation(self, multiple=1.0):
        return multiple * self.get_equity() / self.get_share_count()
    def default_valuation(self, extra_multiple = 1.0, quarter=False):
        ticker_info = self.parser.get_info(self.ticker)
        if 'YATIRIM ORTAKLIĞI' in ticker_info.loc['NAME']:
            try:
                return extra_multiple * self.book_value_valuation()
            except:
                print('Book valuation not found for', self.ticker)
                return 0.0
        else:
            try:
                return extra_multiple * self.ebitda_valuation(quarter=quarter)
            except:
                print('Ebitda valuation not found for', self.ticker)
                try:
                    return extra_multiple * self.book_value_valuation()
                except:
                    print('Book valuation not found for', self.ticker)
                    return 0.0
                    
