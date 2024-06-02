from .KAP_Interface import KAPParser
from ..DataFetch.Helpers.utils import standardize_ticker, book_value_strings
import pandas as pd

class Company:

    def __init__(self, ticker, data_path, update=True) -> None:
        self.ticker = standardize_ticker(ticker)
        self.parser = KAPParser(data_path)

        # Defined as 1 to 4 depending on the latest announced financials
        self.last_quarter = None

        self.financials = self.parser.get_financials(self.ticker, update=update)
        self.balance_sheet = self.__get_balance_sheet()
        self.income_statement = self.__get_income_statement()
        self.cash_flow_statement = self.__get_cash_flow_statement()
        self.yearly_balance_sheet = self.__get_balance_sheet(yearly=True)
        self.yearly_income_statement = self.__get_income_statement(yearly=True)
        self.yearly_cash_flow_statement = self.__get_cash_flow_statement(yearly=True)
        self.prev_income_statement = self.__get_income_statement(previous=True)
        self.prev_cash_flow_statement = self.__get_cash_flow_statement(previous=True)
        self.prev_year_income_statement = self.__get_income_statement(prev_year=True)


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
    
    # TODO: Add functionality to obtain previous year financial for revenue growth
    def __get_income_statement(self, yearly=False, previous=False, prev_year=False):
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
    
    @staticmethod
    def __get_statement_value(self_statement, value_name, priority=0):
        try:
            value = self_statement.loc[value_name]
        except (KeyError, AttributeError):
            return pd.Series([0.0])
        # Handle multiple occurrences
        if type(value) == pd.DataFrame:
            value = value.iloc[priority]
        # High count without multiple occurrences
        elif priority > 0:
            return pd.Series([0.0])
        return value
    
    def __get_balance_sheet_value(self, value_name, priority=0):
        value = Company.__get_statement_value(self.balance_sheet, value_name, priority)
        return value.iloc[0]
    
    ### Values from the income statement ###
    def get_revenue(self, quarter=False):
        return self.__get_income_statement_value('Hasılat', quarter=quarter)
    def get_net_profit(self, quarter=False):
        return self.__get_income_statement_value('Ana Ortaklık Payları', quarter=quarter)
    def get_noncontrolling_profit(self, quarter=False):
        try:
            return self.__get_income_statement_value('Kontrol Gücü Olmayan Paylar', quarter=quarter)
        except KeyError:
            return 0
    def get_gross_profit(self, quarter=False):
        return self.__get_income_statement_value('BRÜT KAR (ZARAR)', quarter=quarter)
    def get_operating_profit(self, quarter=False):
        return self.__get_income_statement_value('ESAS FAALİYET KARI (ZARARI)', quarter=quarter)
    def get_other_operating_income(self, quarter=False):
        return self.__get_income_statement_value('Esas Faaliyetlerden Diğer Gelirler', quarter=quarter)
    def get_other_operating_expense(self, quarter=False):
        return self.__get_income_statement_value('Esas Faaliyetlerden Diğer Giderler', quarter=quarter)
    
    def __get_income_statement_value(self, value_name, quarter=False, priority=0):
        value = Company.__get_statement_value(self.income_statement, value_name, priority)
        # If quarterly data is needed
        if quarter:
            # First quarter, just data
            if self.last_quarter == 1:
                return value.iloc[0]
            # Last quarter - Q3 Data
            elif self.last_quarter == 4:
                if self.prev_income_statement is not None:
                    prev_value = Company.__get_statement_value(self.prev_income_statement, value_name, priority)
                    return value.iloc[0] - prev_value.iloc[0]
                # Alternative solution for the case without previous financials
                else:
                    return value.iloc[0] / 4
            # Q2 and Q3, just get quarterly data
            else:
                return value.iloc[2]
        # If not quarterly, return TTM data (Last 12 months)
        else:
            # Return value on yearly financials
            if self.last_quarter == 4:
                return value.iloc[0]
            # Get last year + difference on this year on Q1 to Q3
            else:
                if self.yearly_income_statement is not None:
                    value_year = Company.__get_statement_value(self.yearly_income_statement, value_name, priority)
                    return value.iloc[0] - value.iloc[1] + value_year.iloc[0]
                # Alternative solution for the case without yearly financials
                else:
                    return value.iloc[0] * 4 / self.last_quarter

    ### Values from the cash flow statement ###
    def get_amortization(self, quarter=False):
        return self.__get_cash_flow_statement_value('Amortisman ve İtfa Gideri İle İlgili Düzeltmeler', quarter=quarter)
    
    def __get_cash_flow_statement_value(self, value_name, quarter=False, priority=0):
        value = Company.__get_statement_value(self.cash_flow_statement, value_name, priority)
        # If quarterly data is needed
        if quarter:
            # First quarter, just data
            if self.last_quarter == 1:
                return value.iloc[0]
            # Last quarter - Q3 Data
            else:
                if self.prev_cash_flow_statement is not None:
                    prev_value = Company.__get_statement_value(self.prev_cash_flow_statement, value_name, priority)
                    return value.iloc[0] - prev_value.iloc[0]
                else:
                    return value.iloc[0] / 3
        # If not quarterly, return TTM data (Last 12 months)
        else:
            # Return value on yearly financials
            if self.last_quarter == 4:
                return value.iloc[0]
            # Get last year + difference on this year on Q1 to Q3
            else:
                if self.yearly_cash_flow_statement is not None:
                    value_year = Company.__get_statement_value(self.yearly_cash_flow_statement, value_name, priority)
                    return value.iloc[0] - value.iloc[1] + value_year.iloc[0]
                # Alternative solution for the case without yearly financials
                else:
                    return value.iloc[0] * 4 / self.last_quarter
                
    ### Values calculated using the data from the tables
    def get_controlling_equity_ratio(self):
        equity = self.get_equity()
        if equity + self.get_noncontrolling_equity() < 0.0001:
            control_equity = 1.0
        else:
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
        if profit + self.get_noncontrolling_profit() < 0.0001:
            control_profit = 1.0
        else:
            control_profit = profit / (profit + self.get_noncontrolling_profit())
            control_profit = min(1.0, control_profit)
            control_profit = max(0.0, control_profit)
        return control_profit
    def get_basic_operating_income(self, control_adjusted=False, quarter=False):
        control_multiplier = self.get_controlling_profit_ratio() if control_adjusted else 1.0
        basic_operating_income = self.get_operating_profit(quarter=quarter) - self.get_other_operating_income(quarter=quarter) - self.get_other_operating_expense(quarter=quarter)
        return control_multiplier * basic_operating_income
    def get_ebitda(self, control_adjusted=False, quarter=False):
        control_multiplier = self.get_controlling_profit_ratio() if control_adjusted else 1.0
        ebitda = self.get_basic_operating_income(quarter=quarter) + self.get_amortization(quarter=quarter)
        return control_multiplier * ebitda
    def get_adjusted_ebitda(self, control_adjusted=True, quarter=False):
        ebitda = self.get_ebitda(control_adjusted=control_adjusted, quarter=quarter)
        return ebitda
    def get_revenue_growth(self):
        revenue = Company.__get_statement_value(self.income_statement, 'Hasılat', priority=0)
        if revenue.iloc[0] == 0.0 or revenue.iloc[1] == 0.0:
            return 0.0
        return 1 * (revenue.iloc[0] / revenue.iloc[1] - 1)

    ### Valuation methods
    def ebitda_valuation(self, multiple=10, control_adjusted=True, quarter=False):
        quarter_multiplier = 4 if quarter else 1
        return (quarter_multiplier * self.get_adjusted_ebitda(quarter=quarter, control_adjusted=control_adjusted) * multiple + self.get_net_assets_for_ev(control_adjusted=control_adjusted)) / self.get_share_count()
    def book_value_valuation(self, multiple=1.0):
        return multiple * self.get_equity() / self.get_share_count()
    def default_valuation(self, extra_multiple = 1.0, quarter=False):
        ticker_info = self.parser.get_info(self.ticker)
        if any(book_value in ticker_info.loc['NAME'] for book_value in book_value_strings):
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
    
