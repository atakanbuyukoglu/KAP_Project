from src.Valuation.Metrics import Company
from pathlib import Path

data_path = Path(__file__).parent / "Data/"
data_path.mkdir(parents=True, exist_ok=True)

company_name = 'megap'

company = Company(company_name, data_path)
multiplier = 10

company_name_upper = company_name.upper()
print(company_name_upper, 'Özkaynak Kontrol Oranı:', company.get_controlling_equity_ratio())
print(company_name_upper, 'Net Kar Kontrol Oranı:', company.get_controlling_profit_ratio())
print(company_name_upper, 'Hasılat (Son 12 Ay):', company.get_revenue(ttm=True))
print(company_name_upper, 'Faaliyet Karı (Son 12 Ay, Diğer Hariç):', company.get_basic_operating_income(ttm=True))
print(company_name_upper, 'Amortizasyon (Son 12 Ay):', company.get_amortization(ttm=True))
print(company_name_upper, 'FAVÖK (Son 12 Ay):', company.get_ebitda(ttm=True))
print(company_name_upper, 'Düzeltilmiş FAVÖK (Son 12 Ay):', company.get_adjusted_ebitda(ttm=True, control_adjusted=True))
print(company_name_upper, 'Değerleme için Net Varlık:', company.get_net_assets_for_ev(control_adjusted=True))
print(company_name_upper, 'Hisse Sayısı:', company.get_share_count())
print(company_name_upper, 'Favök Değerlemesi (Çarpan:', multiplier, '):', company.ebitda_valuation(multiple=multiplier))

