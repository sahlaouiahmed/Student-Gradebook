import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
import os
from oauth2client.client import OAuth2Credentials
from gspread.exceptions import APIError, WorksheetNotFound
import json


# Define the scope
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Authenticate using the service account credentials from environment variables
try:
    credentials_info = json.loads(os.getenv("CREDS"))
    creds = Credentials.from_service_account_info(credentials_info)
    client = gspread.authorize(creds)
except Exception as e:
    print(f"Error in authentication: {e}")
    exit(1)


# Open the Google Sheet
try:
    spreadsheet = client.open('Student Gradebook')
except APIError as e:
    print(f"Error in accessing the Google Sheet: {e}")
    exit(1)

def get_or_create_worksheet(spreadsheet, class_name):
    """
    Get or create a worksheet with the given class name
    """
    while True:
        try:
            worksheet = spreadsheet.worksheet(class_name)
            print(f"Worksheet '{class_name}' found.")
            use_existing = input("A worksheet with this class name already exists. Do you want to use the existing worksheet? (yes/no): \n")
            if use_existing.lower() == "yes":
                return worksheet
            else:
                class_name = input("Please enter a different class name: \n")
        except WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=class_name, rows="100", cols="20")
            print(f"Worksheet '{class_name}' created.")
            return worksheet

# Define the Student class
class Student:
    def __init__(self, firstName, lastName, grades):
        self.firstName = firstName
        self.lastName = lastName
        self.grades = grades
        self.average = sum(grades.values()) / len(grades)
        self.status = 'Pass' if self.average >= 50 else 'Fail'
        self.grade = self.assign_grade()

    def assign_grade(self):
        """
        Assign a grade to each student based on their average
        """
        if self.average >= 90:
            return 'Excellent'
        elif self.average >= 80:
            return 'Very good'
        elif self.average >= 70:
            return 'Good'
        elif self.average >= 50 and self.average < 70:
            return 'Passable'
        else:
            return 'Failed'

def style_worksheet(worksheet):
    """
    Style the header and sections of the worksheet for a clear and polished look
    """
    # Define the header range
    header_range = 'A1:K1'

    # Define the ranges for different data sections
    student_data_range = 'A2:B100'
    subjects_range = 'C2:G100'
    other_data_range = 'H2:K100'

    # Apply formatting to the header
    worksheet.format(header_range, {
        "backgroundColor": {
            "red": 0.2,
            "green": 0.6,
            "blue": 0.8
        },
        "textFormat": {
            "foregroundColor": {
                "red": 1.0,
                "green": 1.0,
                "blue": 1.0
            },
            "fontSize": 12,
            "bold": True
        },
        "borders": {
            "top": {
                "style": "SOLID",
                "width": 2,
                "color": {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0
                }
            },
            "bottom": {
                "style": "SOLID",
                "width": 2,
                "color": {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0
                }
            },
            "left": {
                "style": "SOLID",
                "width": 2,
                "color": {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0
                }
            },
            "right": {
                "style": "SOLID",
                "width": 2,
                "color": {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0
                }
            }
        }
    })

    # Apply formatting to student data section
    worksheet.format(student_data_range, {
        "backgroundColor": {
            "red": 0.9,
            "green": 0.9,
            "blue": 0.98
        },
        "textFormat": {
            "fontSize": 11
        }
    })

    # Apply formatting to subjects section
    worksheet.format(subjects_range, {
        "backgroundColor": {
            "red": 0.88,
            "green": 1.0,
            "blue": 0.88
        },
        "textFormat": {
            "fontSize": 11
        }
    })

    # Apply formatting to other data section
    worksheet.format(other_data_range, {
        "backgroundColor": {
            "red": 1.0,
            "green": 0.92,
            "blue": 0.8
        },
        "textFormat": {
            "fontSize": 11
        }
    })


def insert_data(worksheet, students):
    """
    Function to insert data into Google Sheets
    """
    all_values = worksheet.get_all_values()

    if not all_values or all_values[0] != ["First name", "Last name", "English", "Math", "Physics", "History", "Python", "Average", "Rank", "Grade", "Status"]:
        # Add headers
        headers = ["First name", "Last name", "English", "Math", "Physics", "History", "Python", "Average", "Rank", "Grade", "Status"]
        worksheet.append_row(headers)
        print("Headers inserted.")

    print("Insertion of the students' data into your worksheet...")

    # Add student data
    for student in students:
        try:
            row = [
                student.firstName,
                student.lastName,
                student.grades["English"],
                student.grades["Math"],
                student.grades["Physics"],
                student.grades["History"],
                student.grades["Python"],
                student.average,
                student.rank,
                student.grade,
                student.status
            ]
            worksheet.append_row(row)
        except KeyError as e:
            print(f"Missing grade data for subject: {e}")
    print("Done")
    
    # Update ranks
    update_ranks(worksheet)
    # Apply styling
    style_worksheet(worksheet)

def rank_students(students):
    """
    Function to rank students
    """
    print("Calculating each student's rank ...")
    students.sort(key=lambda x: x.average, reverse=True)
    for rank, student in enumerate(students, start=1):
        student.rank = rank
    print("Done")

def update_ranks(worksheet):
    """
    Function to update the rank of each student when the user adds new data
    """
    # Get all data
    data = worksheet.get_all_values()
    
    # Extract averages
    averages = [float(row[7]) for row in data[1:] if row[7].replace('.', '', 1).isdigit()]
    print("Updating ranks ...")
    # Calculate ranks
    ranks = [sorted(averages, reverse=True).index(x) + 1 for x in averages]
    
    # Update ranks in the sheet
    for i, rank in enumerate(ranks, start=2):
        worksheet.update_cell(i, 9, rank)  # Column 9 is the Rank column
    print("Done")

def get_valid_grade(subject):
    """
    Check if the provided grade is valid.
    A valid grade is between 0 and 100.
    """
    while True:
        try:
            grade = float(input(f"Enter {subject} grade (0-100): \n"))
            if 0 <= grade <= 100:
                return grade
            else:
                print("Grade should be between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def is_valid_name(name):
    """
    Check if the provided name is valid.
    A valid name contains only alphabetic characters and spaces, and is not empty.
    """
    return all(part.isalpha() for part in name.split()) and name.strip() != ""

def main():
    """
    Main function to input student data and process it
    """
    print("Welcome to our student gradebook")
    while True:
        class_name = input("Enter the class name: \n")
        worksheet = get_or_create_worksheet(spreadsheet, class_name)
        
        students = []
        print(f"Entering student(s) information for class: {class_name}")
        while True:
            try:
                num_students = int(input("Please enter the number of students: \n"))
                if num_students > 0:
                    break
                else:
                    print("Number of students should be positive.")
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

        for _ in range(num_students):
            while True:
                firstName = input("Enter student's First name: \n")
                lastName = input("Enter student's Last name: \n")
                if is_valid_name(firstName) and is_valid_name(lastName):
                    break
                else:
                    print("Invalid name. Please enter names with alphabetic characters only.")

            grades = {
                "English": get_valid_grade("English"),
                "Math": get_valid_grade("Math"),
                "Physics": get_valid_grade("Physics"),
                "History": get_valid_grade("History"),
                "Python": get_valid_grade("Python")
            }
            students.append(Student(firstName, lastName, grades))
        
        print("Calculating each student's average...")
        print("Assigning a grade to each student based on their average...")
        print("Evaluating the student’s status as pass or fail...")
        
        # Calculating the rank of students
        rank_students(students)
        
        # Insert data into Google Sheets
        insert_data(worksheet, students)
        
        another_class = input("Do you want to add data for another class? (yes/no): \n")
        if another_class.lower() != "yes":
            break

if __name__ == "__main__":
    main()
