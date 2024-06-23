from openpyxl import Workbook, worksheet
from datetime import datetime, timedelta

report_periods = {
    '3 Aylık': 1,
    '6 Aylık': 2,
    '9 Aylık': 3,
    'Yıllık': 4
}

book_value_strings = [
    'YATIRIM ORTAKLIĞI',
    'GAYRİMENKUL YATIRIM',
    'GAYRİMENKUL GELİŞTİRME'
]

solo_names = ['Solo', 'Bireysel', 'Konsolide Olmayan']

# Auto fit the columns of a worksheet to its data
def auto_fit_columns(sheet: worksheet):
    for column_cells in sheet.columns:
        max_length = 0
        column = column_cells[0].column_letter  # Get the column name
        for cell in column_cells:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        sheet.column_dimensions[column].width = max_length

def standardize_ticker(ticker:str) -> str:
    # Accept only upper characters
    ticker = ticker.upper()
    # Some tickers have multiple keys separated by comma
    ticker = ticker.split(', ')
    # Take the longest ticker only
    ticker = max(ticker, key=len)
    return ticker

def to_quarter(year, period: str):
    quarter_info = str(year) + 'Q' + str(report_periods[period])
    return quarter_info

def is_solo(report_name):
    for solo_name in solo_names:
        if solo_name.lower() in report_name.lower():
            return True
    return False

# Function to check if a cell is empty or hidden
def is_empty_or_hidden(cell):
    return not cell.get_text(strip=True) or 'display: none;' in cell.get('style', '')

# First checks if the date string contains "Today", "Tomorrow", or "Yesterday", and replaces these with the appropriate date.
# Then it converts the modified string into a datetime object using datetime.strptime.
def convert_date_string(date_string):
    now = datetime.now()
    
    if "Bugün" in date_string:
        date_string = date_string.replace("Bugün", now.strftime("%d.%m.%y"))
    elif "Yarın" in date_string:
        date_string = date_string.replace("Yarın", (now + timedelta(days=1)).strftime("%d.%m.%y"))
    elif "Dün" in date_string:
        date_string = date_string.replace("Dün", (now - timedelta(days=1)).strftime("%d.%m.%y"))
    
    # Convert the date string to datetime object
    return datetime.strptime(date_string, "%d.%m.%y %H:%M")
