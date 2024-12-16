# Student Gradebook
This Python project allows users to manage student data efficiently. Users can enter each student’s first and last name, along with their grades in various subjects. The program then processes this data to:

1. Validate the entered information.
2. Calculate the average grade for each student.
3. Determine the rank of each student based on their average grade.
4. Assign a grade of success.
5. Evaluate the student’s status as pass or fail.

This project aims to streamline the process of student evaluation, making it easier for educators to track and analyze student performance.

You can access the live version of the application at the following link: [Student Gradebook App](https://student-gradebook-d718e2d334b6.herokuapp.com/)

## Features
1. User-Friendly Data Entry:
    * Allows users to input student names, surnames, and grades in various subjects.
    * Enables users to add a class for each group of students.

2. Data Validation:
    * Ensures that all entered data is accurate and complete before processing.

3. Average Grade Calculation:
    * Automatically calculates the average grade for each student based on their subject grades.

4. Student Ranking:
    * Ranks students according to their average grades, providing a clear view of their performance relative to peers.

5. Grade of Success Assignment:
    * Assigns a grade of success (e.g., A, B, C) based on predefined criteria.

6. Pass/Fail Status Evaluation:
    * Determines whether a student has passed or failed based on their average grade and other criteria.

7. Comprehensive Reporting:
    * Generates detailed reports summarizing each student’s performance, including their average grade, rank, grade of success, and pass/fail status.

8. Scalability:
    * Can handle a large number of students and subjects, making it suitable for various educational settings.

9. Class Management:
    * Allows users to add a class for each group of students.
    * If the class already exists, users can add new student data to the existing class, ensuring seamless data management.

## Code Explanation

1. Authentication and Setup

```python
import gspread
from google.oauth2.service_account import Credentials
import os
from gspread.exceptions import WorksheetNotFound
import json

# Define the scope
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Authenticate using the service account credentials from environment variables
try:
    if 'CREDS' in os.environ:
        credentials_info = json.loads(os.getenv('CREDS'))
    else:
        # For local development in Gitpod, use the credentials file
        credentials_info = json.load(open('credentials.json'))
    
    creds = Credentials.from_service_account_info(credentials_info)
    SCOPED_CREDS = creds.with_scopes(SCOPE)
    GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
    spreadsheet = GSPREAD_CLIENT.open('Student Gradebook')
except Exception as e:
    print(f"Error in authentication: {e}")
    exit(1)
```

This section handles the authentication and setup process for accessing and manipulating the Google Sheets API using service account credentials. The code dynamically determines whether to use environment variables (for deployment environments like Heroku) or a local credentials file (for development environments like Gitpod).

2. Worksheet Management

```python
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
                while True:
                    class_name = input("Please enter a different class name (alphanumeric and spaces only): \n")
                    if is_valid_class_name(class_name):
                        break
                    else:
                        print("Invalid class name. Please enter a name with alphanumeric characters and spaces only.")
        except WorksheetNotFound:
            while True:
                if is_valid_class_name(class_name):
                    worksheet = spreadsheet.add_worksheet(title=class_name, rows="100", cols="20")
                    print(f"Worksheet '{class_name}' created.")
                    return worksheet
                else:
                    print("Invalid class name. Please enter a name with alphanumeric characters and spaces only.")
                    class_name = input("Please enter a valid class name (alphanumeric and spaces only): \n")
```
- Function Description : The function checks for the existence of a worksheet with the specified class name, prompts the user to either use the existing worksheet or create a new one, and ensures the class name is valid before proceeding.

- Validation Function : is_valid_class_name checks if the class name contains only alphanumeric characters and spaces, and is not empty.

- User Prompt : The program validates the class name and prompts the user to re-enter until a valid name is provided.

3. Student Class

```python
class Student:
    def __init__(self, firstName, lastName, grades):
        self.firstName = firstName
        self.lastName = lastName
        self.grades = grades
        self.average = sum(grades.values()) / len(grades)
        self.status = 'Pass' if self.average >= 50 else 'Fail'
        self.grade = self.assign_grade()

    def assign_grade(self):
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
```

The Student class defines the attributes and methods for each student, including calculating averages and assigning grades.

4. Inserting Data

```python
def insert_data(worksheet, students):
    all_values = worksheet.get_all_values()
    if not all_values or all_values[0] != ["First name", "Last name", "English", "Math", "Physics", "History", "Python", "Average", "Rank", "Grade", "Status"]:
        headers = ["First name", "Last name", "English", "Math", "Physics", "History", "Python", "Average", "Rank", "Grade", "Status"]
        worksheet.append_row(headers)
        print("Headers inserted.")
    
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
```

This function inserts student data into the Google Sheets and includes headers if they are not already present.

5. Ranking Students

```python
def rank_students(students):
    students.sort(key=lambda x: x.average, reverse=True)
    for rank, student in enumerate(students, start=1):
        student.rank = rank
    print("Done")
```

This function sorts and ranks students based on their average grades.

6. Updating Ranks

```python
def update_ranks(worksheet):
    data = worksheet.get_all_values()
    averages = [float(row[7]) for row in data[1:] if row[7].replace('.', '', 1).isdigit()]
    ranks = [sorted(averages, reverse=True).index(x) + 1 for x in averages]
    
    for i, rank in enumerate(ranks, start=2):
        worksheet.update_cell(i, 9, rank)
    print("Done")
```

This function updates the ranks in the worksheet based on the student averages.

7. Main Function

```python
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
                if is_valid_name(firstName):
                    break
                else:
                    print("Invalid first name. Please enter a name with alphabetic characters only.")

            while True:
                lastName = input("Enter student's Last name: \n")
                if is_valid_name(lastName):
                    break
                else:
                    print("Invalid last name. Please enter a name with alphabetic characters only.")

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
        
        print("Data saved successfully.")
        another_class = input("Do you want to add data for another class? (yes/no): \n")
        if another_class.lower() != "yes":
            print("Thank you! Quitting now.")
            break

```

This function handles the entire workflow of the application, from gathering class and student information, validating inputs, calculating student averages and ranks, to inserting the data into Google Sheets and applying appropriate styling. The function continues to prompt the user for new class data until they choose to stop.

## Manual Testing and Input Validation

To ensure that our application is robust and free of bugs, we implemented several input validation checks and performed manual testing. Here are the steps we took:

#### Input Validation (Saisie Control)
1. **Class Name Validation**:
    - The user is prompted to enter a class name. If a worksheet with the entered class name already exists, the user is given the option to use the existing worksheet or enter a different class name.
    
2. **Student Data Validation**:
    - **First Name and Last Name**: The application checks if the entered names contain only alphabetic characters and are not empty. If the input is invalid, the user is prompted to re-enter the names.
    - **Grades**: The application checks if the entered grades are numeric values between 0 and 100. If the input is invalid, the user is prompted to re-enter the grades.

#### Manual Testing
To manually test the application, we followed these steps:
1. **Run the Application**:
    - Start the application by running the `run.py` script using the command `python run.py`.
    
2. **Enter Class and Student Data**:
    - Enter a class name and verify if the application correctly handles existing and new class names.
    - Input multiple student records and ensure that the application validates the names and grades correctly.
    
3. **Verify Google Sheets Output**:
    - Check the Google Sheets to verify that the student data has been correctly inserted.
    - Ensure that the headers, student data, and other data are styled correctly.
    
4. **Test Edge Cases**:
    - Test with invalid inputs such as empty names, non-numeric grades, and grades outside the valid range (0-100).
    - Verify that the application handles these cases gracefully by prompting the user to re-enter the data.

By performing these validation checks and manual testing steps, we ensured that the application is user-friendly and free of bugs. This helps maintain data integrity and provides a smooth user experience.

## Deployment

This project is deployed to Heroku using the GitHub integration. Follow the steps below to deploy a version of this project.

### Steps to Deploy

1. **Create a Heroku App**:
   - Log in to a Heroku account and create a new app by clicking the "New" button on the dashboard and selecting "Create new app." Provide the app a unique name and select the appropriate region.

2. **Connect GitHub Repository**:
   - In the Deploy tab of the newly created app, locate the "Deployment method" section.
   - Select "GitHub" as the deployment method.
   - Connect the GitHub account and select the repository to deploy.

3. **Environment Variables**:
   - Set up environment variables in the "Settings" tab of the Heroku app. Add any necessary environment variables specific to your project.

4. **Procfile and requirements.txt files**:
   - Ensure a `Procfile` with the following content is present:
     ```
        web: node index.js
     ```
   - We created a `requirements.txt` file to list all the necessary Python dependencies. This file ensures that Heroku installs all the required libraries for the project to run smoothly.

5. **Push to GitHub**:
   - Ensure all changes are committed to the GitHub repository.

6. **Deploy via Heroku Dashboard**:
   - In the Deploy tab, scroll down to the "Manual deploy" section.
   - Select the branch you want to deploy.
   - Click "Deploy Branch."

7. **Automatic Deploys (Optional)**:
   - Enable automatic deploys from the selected GitHub branch to ensure your Heroku app is always up-to-date with the latest changes from GitHub.

## Future Enhancements

Here are some ideas for future enhancements and features that could be added to the Student Gradebook project:

1. **Export to CSV**:
    - Add functionality to export student grade data to a CSV file for offline access and sharing.

2. **Import from CSV**:
    - Allow users to import student data from a CSV file to quickly populate the gradebook.

3. **Enhanced User Interface**:
    - Improve the user interface for easier navigation and data entry.

4. **Data Filtering and Sorting**:
    - Add features to filter and sort student data based on various criteria such as grades, subjects, and status.

5. **Performance Graphs**:
    - Create visual performance graphs to help users understand student progress over time.

6. **Customizable Themes**:
    - Allow users to customize the look and feel of the gradebook with different themes.

7. **Feedback System**:
    - Implement a feedback system where teachers can provide comments on student performance.

These enhancements can help make the Student Gradebook app more useful and user-friendly, providing additional features and improvements for managing student grades.
