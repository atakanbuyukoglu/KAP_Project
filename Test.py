from src.DataFetch.KAP import KAP
from src.DataFetch.Helpers.DateHandler import DateHandler
from pathlib import Path
from datetime import date, timedelta

data_path = Path(__file__).parent / "Data/"
date_path = Path(__file__).parent / 'Data' / 'last_search_date.txt'

save_date = date.today() - timedelta(days=2)
date_handler = DateHandler(dt_value=save_date, file_path=date_path)
date_handler.save_to_file()

#kap = KAP(data_path)
#kap.save_financials('AKFK')