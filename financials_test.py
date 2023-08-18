from src.DataFetch.KAP import KAP
from pathlib import Path

data_path = Path(__file__).parent / "Data/"
data_path.mkdir(parents=True, exist_ok=True)

kap = KAP(data_path=data_path)

#with open(data_path / 'Report_Sample.html', 'r', encoding='utf-8') as f:
#    report = f.read()

#kap.save_report(report, data_path / 'Report_Sample.xlsx')
#kap.report_2_pandas(report)
#kap.save_company_financials('avod)
#kap.get_company_financials('avod')
kap.get_share_count('avod')
