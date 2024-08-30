import gspread
from oauth2client.service_account import ServiceAccountCredentials


def authenticate_google_sheets(credentials_path, sheet_name):
    """
    Authenticate and connect to Google Sheets
    """
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1


# Define the Student class
class Student:
    def __init__(self, firstName,lastName, grades):
        self.firstName = firstName
        self.lastName = lastName
        self.grades = grades
        self.average = sum(grades.values()) / len(grades)
        self.status = 'Pass' if self.average >= 50 else 'Fail'
        self.grade =  self.assign_grade() 

    def assign_grade(self):
        """
        Assign a grade to each student based on his average
        """
        if self.average >= 90:
            return 'Excellent'
        elif self.average >= 80:
            return 'Very good'
        elif self.average >= 70:
            return 'Good'
        elif self.average >= 50 and self.average <70 :
            return 'Passable'
        else:
            return 'Failed'  
        


def insert_data(sheet, students):
    """
    Function to insert data into Google Sheets
    """
# Check if the first row is empty
    if not sheet.row_values(1):
        # Add headers
        headers = ["First name" ,"Last name", "English", "Math", "Physics", "History", "Python", "Average", "Rank", "Grade", "Status"]
        sheet.append_row(headers)
    print("Insertion of the students data in your worksheet...")
    # Add student data
    for student in students:
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
        sheet.append_row(row)
    print("Done")
    # Update ranks
    update_ranks(sheet)



def rank_students(students):
    """
    Function to rank students
    """
    print("Calculating each student rank ...")
    students.sort(key=lambda x: x.average, reverse=True)
    for rank, student in enumerate(students, start=1):
        student.rank = rank
    print("Done")


def update_ranks(sheet):
    """
    Function to update the rank of each student when the user add new data
    """
    # Get all data
    data = sheet.get_all_values()
    
    # Extract averages
    averages = [float(row[6]) for row in data[1:]]
    print("Updating ranks ...")
    # Calculate ranks
    ranks = [sorted(averages, reverse=True).index(x) + 1 for x in averages]
    
    # Update ranks in the sheet
    for i, rank in enumerate(ranks, start=2):
        sheet.update_cell(i, 9, rank)  # Column 9 is the Rank column
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
    A valid name contains only alphabetic characters and is not empty.
    """
    return name.isalpha()


def main():
    """
    Main function to input student data and process it
    """
    print("Welcome to our student gradebook ")
    students = []
    print("Entering student(s) information")
    num_students = int(input("Please enter the number of students: \n"))
    
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
        students.append(Student(firstName,lastName, grades))
    


    print("Calculating each student's average...")
    print("Assign a grade to each student based on his average ...")
    print("Evaluate the student’s status as pass or fail ...")
    rank_students(students)
    # Insert data into Google Sheets
    sheet = authenticate_google_sheets("credentials.json", "Student Gradebook")
    insert_data(sheet, students)

if __name__ == "__main__":
    main()
