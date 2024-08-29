import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Set up the Google Sheets API client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("Student Gradebook").sheet1

# Get all records from the sheet
data = sheet.get_all_records()

# Convert the data to a DataFrame
df = pd.DataFrame(data)
print(df)
print(type(df))

# Calculate the average grade
df['Average'] = df[['English','Math', 'Science', 'History','Sport']].mean(axis=1)

# Rank the students based on their average grade
df['Rank'] = df['Average'].rank(ascending=False, method='min')

# Determine pass or fail status
df['Status'] = df['Average'].apply(lambda x: 'Pass' if x >= 50 else 'Fail')

# Update the Google Sheet with the new columns
for i, row in df.iterrows():
    sheet.update_cell(i+2, df.columns.get_loc('Average')+1, row['Average'])
    sheet.update_cell(i+2, df.columns.get_loc('Rank')+1, row['Rank'])
    sheet.update_cell(i+2, df.columns.get_loc('Status')+1, row['Status'])

print("Grades processed and updated successfully!")
