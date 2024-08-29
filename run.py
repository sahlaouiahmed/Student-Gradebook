import gspread
from oauth2client.service_account import ServiceAccountCredentials


# Authenticate and connect to Google Sheets
def authenticate_google_sheets(credentials_path, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1


# Define the Student class
class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades
        self.average = sum(grades.values()) / len(grades)
        self.status = 'Pass' if self.average >= 50 else 'Fail'
        self.grade =  self.assign_grade() 

    #Assign a grade to each student based on his average
    def assign_grade(self):
        if self.average >= 90:
            return 'A'
        elif self.average >= 80:
            return 'B'
        elif self.average >= 70:
            return 'C'
        elif self.average >= 60:
            return 'D'
        else:
            return 'F'  



# Main function to input student data and process it
def main():
    students = []
    num_students = int(input("Enter the number of students: "))
    
    for _ in range(num_students):
        while True:
            name = input("Enter student's name: ")
            if name.isalpha() and name.strip():
                break
            else:
                print("Invalid name. Please enter a valid name containing only alphabetic characters.")
        grades = {
            "English": float(input("Enter English grade: ")),
            "Math": float(input("Enter Math grade: ")),
            "Physics": float(input("Enter Physics grade: ")),
            "History": float(input("Enter History grade: ")),
            "Python": float(input("Enter Python grade: "))
        }
        students.append(Student(name, grades))
