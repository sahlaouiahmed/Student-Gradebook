import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Authenticate and connect to Google Sheets
def authenticate_google_sheets(credentials_path, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1