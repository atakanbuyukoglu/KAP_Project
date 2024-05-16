from openpyxl import Workbook, worksheet

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

def standardize_ticker(ticker):
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

def is_solo(report_info):
    for solo_name in solo_names:
        if solo_name.lower() in report_info['basic']['summary'].lower():
            return True
    return False
