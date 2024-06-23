from datetime import date

class DateHandler:
    def __init__(self, dt_value=None, file_path=None):
        if dt_value is None:
            self.dt_value = date.today()
        elif isinstance(dt_value, date):
            self.dt_value = dt_value
        else:
            raise TypeError("dt_value must be a date object or None")
        
        self.file_path = file_path
    
    def save_to_file(self, file_path=None):
        if file_path is None:
            if self.file_path is None:
                raise ValueError("No file path provided")
            file_path = self.file_path
        
        with open(file_path, 'w') as file:
            file.write(self.dt_value.isoformat())
    
    def load_from_file(self, file_path=None):
        if file_path is None:
            if self.file_path is None:
                raise ValueError("No file path provided")
            file_path = self.file_path
        
        with open(file_path, 'r') as file:
            dt_str = file.read().strip()
            self.dt_value = date.fromisoformat(dt_str)

    def get_date(self):
        return self.dt_value
    
    def __repr__(self):
        return f"DateHandler(dt_value={self.dt_value}, file_path={self.file_path})"