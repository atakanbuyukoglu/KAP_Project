from src.DataFetch.KAP import KAP
from src.DataFetch.Helpers.DateHandler import DateHandler
from pathlib import Path
from datetime import date, timedelta

data_path = Path(__file__).parent / "Data/"
date_path = Path(__file__).parent / 'Data' / 'last_search_date.txt'

date_handler = DateHandler(file_path=date_path)
date_handler.load_from_file()
last_date = date_handler.get_date()

kap = KAP(data_path)
kap.update_financials(last_date)