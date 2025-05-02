import gspread
import joblib
import os
import numpy as np
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class PestDetectionSystem:
    def __init__(self):
        self.model = joblib.load('models/pest_detection_model_2.pkl')
        self.scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
       self.creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(os.getenv('GOOGLE_CREDS')), self.scope)
        self.client = gspread.authorize(self.creds)
        self._init_sheet()
    
    def _init_sheet(self):
        self.sheet = self.client.open_by_key(os.getenv('SHEET_ID')).sheet1
        headers = ['timestamp'] + os.getenv("SENSORS").split(',') + ['prediction', 'processed_at']
        if self.sheet.row_values(1) != headers:
            self.sheet.clear()
            self.sheet.append_row(headers)

    def append_to_sheet(self, row_data):
        self.sheet.append_row(row_data)

    def process_new_entries(self):
        records = self.sheet.get_all_records()
        for idx, record in enumerate(records):
            if not record.get('prediction'):
                try:
                    features = np.array([float(record[s]) for s in os.getenv("SENSORS").split(',')]).reshape(1, -1)
                    prediction = self.model.predict(features)[0]
                    
                    self.sheet.update_cell(idx+2, len(record)+1, 
                        'Pest Detected' if prediction == 1 else 'No Pest')
                    self.sheet.update_cell(idx+2, len(record)+2, 
                        datetime.now().isoformat())
                except Exception as e:
                    self.sheet.update_cell(idx+2, len(record)+2, f'Error: {str(e)}')
