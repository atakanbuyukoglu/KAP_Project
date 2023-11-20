from src.Valuation.Metrics import Company
from src.DataFetch.KAP import KAP
from src.Valuation.Records import Records
from pathlib import Path

def value(ticker):
    data_path = Path(__file__).parent / "Data/"
    data_path.mkdir(parents=True, exist_ok=True)

    company = Company(ticker, data_path, update=False)
    multiplier = 10

    company_name_upper = ticker.upper()
    print(company_name_upper, 'Özkaynak', '{:,}'.format(company.get_equity()))
    print(company_name_upper, 'Özkaynak Kontrol Oranı:', '{:,}'.format(company.get_controlling_equity_ratio()))
    print(company_name_upper, 'Net Kar Kontrol Oranı:', '{:,}'.format(company.get_controlling_profit_ratio()))
    print(company_name_upper, 'Hasılat (Son 12 Ay):', '{:,}'.format(company.get_revenue(ttm=True)))
    print(company_name_upper, 'Faaliyet Karı (Son 12 Ay, Diğer Hariç):', '{:,}'.format(company.get_basic_operating_income(ttm=True)))
    print(company_name_upper, 'Amortizasyon (Son 12 Ay):', '{:,}'.format(company.get_amortization(ttm=True)))
    print(company_name_upper, 'FAVÖK (Son 12 Ay):', '{:,}'.format(company.get_ebitda(ttm=True)))
    print(company_name_upper, 'Düzeltilmiş FAVÖK (Son 12 Ay):', '{:,}'.format(company.get_adjusted_ebitda(ttm=True, control_adjusted=True)))
    print(company_name_upper, 'İşletme Sermayesi:', '{:,}'.format(company.get_working_capital(control_adjusted=True)))
    print(company_name_upper, 'Değerleme için Net Varlık:', '{:,}'.format(company.get_net_assets_for_ev(control_adjusted=True)))
    print(company_name_upper, 'Hisse Sayısı:', '{:,}'.format(company.get_share_count()))
    print(company_name_upper, 'Favök Değerlemesi (Çarpan:', multiplier, '):', company.ebitda_valuation(multiple=multiplier))
    print(company_name_upper, 'En Son Değer:', company.default_valuation(extra_multiple=multiplier / 10))

def record(option):
    data_path = Path(__file__).parent / "Data/"
    data_path.mkdir(parents=True, exist_ok=True)

    records_path = Path(__file__).parent / "Data" / 'Valuation'
    records_path.mkdir(parents=True, exist_ok=True)

    kap = KAP(data_path=data_path)
    company_info = kap.get_company_info()
    companies = list(company_info.index)

    record_file = Records(records_path / 'Valuation_all.xlsx', initial_tickers=companies, add_tickers=False, online=True)

    if option == 'Prices':
        record_file.update_prices()
    elif option == 'Intrinsic':
        record_file.update_intrinsic_values()
    elif option == 'All':
        record_file.update()
    else:
        record_file.update_ticker(option)

def main_menu():
    print('######### KAP Analiz Programı #########')
    print('')
    print('1) Hisse Değerlemesi')
    print('2) Veri tabanı Güncellemesi (Fiyatlar)')
    print('3) Veri tabanı Güncellemesi (İçsel Değer)')
    print('4) Veri tabanı Güncellemesi (Hepsi)')
    print('5) Veri tabanı Güncellemesi (Tek Hisse)')
    print('######### KAP Analiz Programı #########')

    x = input('Programlardan birini seçin:')
    return x

def run_option(x):
    if x == '1':
        ticker = input('Değerlenecek hissenin kodunu girin:')
        value(ticker)
    elif x == '2':
        record('Prices')
    elif x == '3':
        record('Intrinsic')
    elif x == '4':
        record('All')
    elif x == '5':
        ticker = input('Güncellenecek hissenin kodunu girin:')
        record(ticker)
    elif x.upper() == 'Q':
        quit()
    else:
        raise ValueError(x)

if __name__ == '__main__':
    x = main_menu()
    run_option(x)