from src.Valuation.Metrics import Company
from pathlib import Path

data_path = Path(__file__).parent / "Data/"
data_path.mkdir(parents=True, exist_ok=True)

company_name = 'fonet'

company = Company(company_name, data_path, update=False)
multiplier = 10

company_name_upper = company_name.upper()
print(company_name_upper, '(A) Ana Ortaklık Özkaynak', '{:,.2f}'.format(company.get_equity()))
print(company_name_upper, '(B) Toplam Özkaynak', '{:,.2f}'.format(company.get_total_equity()))
print(company_name_upper, '(C = A/B) Özkaynak Kontrol Oranı:', '{:.2%}'.format(company.get_controlling_equity_ratio()))
print(company_name_upper, '(D) İşletme Sermayesi:', '{:,.2f}'.format(company.get_working_capital(control_adjusted=True)))
print(company_name_upper, '(E) Faaliyette Kullanılan Duran Varlıklar:', '{:,.2f}'.format(company.get_working_capital(control_adjusted=True)))
print(company_name_upper, '(F = C*(B-D-E)) Değerleme için Net Ek Varlık:', '{:,.2f}'.format(company.get_net_assets_for_ev(control_adjusted=True)))
print(company_name_upper, '(G) Hasılat (Son 12 Ay):', '{:,.2f}'.format(company.get_revenue(ttm=True)))
print(company_name_upper, '(H) Faaliyet Karı (Son 12 Ay, Diğer Hariç):', '{:,.2f}'.format(company.get_basic_operating_income(ttm=True)))
print(company_name_upper, '(I) Amortizasyon (Son 12 Ay):', '{:,.2f}'.format(company.get_amortization(ttm=True)))
print(company_name_upper, '(J, tanımı C gibi) Net Kar Kontrol Oranı:', '{:.2%}'.format(company.get_controlling_profit_ratio()))
print(company_name_upper, '(K = H+I) FAVÖK (Son 12 Ay):', '{:,.2f}'.format(company.get_ebitda(ttm=True)))
print(company_name_upper, '(L = J*K) Düzeltilmiş FAVÖK (Son 12 Ay):', '{:,.2f}'.format(company.get_adjusted_ebitda(ttm=True, control_adjusted=True)))
print(company_name_upper, '(M) Hisse Sayısı:', '{:,.2f}'.format(company.get_share_count(online=False)))
#print(company_name_upper, 'Defter Değerlemesi (Çarpan:', multiplier, '):', '{:,.2f}'.format(company.book_value_valuation(multiple=1)))
print(company_name_upper, '(N=(10*L+F)/M) FD/Favök Değerlemesi (Çarpan:', multiplier, '):', '{:,.2f}'.format(company.ebitda_valuation(multiple=multiplier)), 'TL')

