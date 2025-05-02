class PestDetectionSystem:
    def __init__(self):
        self.model = joblib.load('models/pest_detection_model_2.pkl')
        self.scope = ['https://spreadsheets.google.com/feeds',
                      'https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(os.getenv('GOOGLE_CREDS')), self.scope)
        self.client = gspread.authorize(self.creds)
        self._init_sheet()

