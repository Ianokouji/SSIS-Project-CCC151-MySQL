from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import QtCore 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QStyleFactory, QTableWidgetItem
from SSIS_Interface_Final import Ui_MainWindow  
from PyQt5.QtGui import QColor


# Import the Database Operations File
from Course_Student import CourseOperations, StudentOperations, Student, Course

class Controller:
    def __init__(self):
        self.app = QApplication([])

        # Create the main window
        self.main_window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_window)
        

        # Global variables used to fetch old data as condition for update
        self.old_student_id = None
        self.old_course_code = None



        # Create instances of database operations classes
        self.course_operations = CourseOperations(host="localhost", user="root", password="2022-1729", database="SSIS_DATABASE")
        self.student_operations = StudentOperations(host="localhost", user="root", password="2022-1729", database="SSIS_DATABASE")

        #----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Mode Handling
        self.Mode = ["View", "Edit", "Delete"]
        self.current_mode = "View"                   # Initial mode is View mode

        #----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Button Connects

        self.ui.ViewButton.clicked.connect(self.set_view_mode)
        self.ui.EditButton.clicked.connect(self.set_edit_mode)
        self.ui.DeleteButton.clicked.connect(self.set_delete_mode)
        self.ui.AddStudentB.clicked.connect(self.set_addStudent)
        self.ui.AddCourseB.clicked.connect(self.set_addCourse)




        
        self.ui.CourseTable.itemClicked.connect(self.Mode_Handler)
        self.ui.StudentTable.itemClicked.connect(self.Mode_Handler)


        self.ui.SaveStudentEdit.clicked.connect(self.UpdateStudent)
        self.ui.SaveCourseEdit.clicked.connect(self.UpdateCourse)

        self.ui.SearchStudentB.clicked.connect(self.search_student)
        self.ui.SearchCourseB.clicked.connect(self.search_course)

        self.ui.SaveStudent.clicked.connect(self.AddStudent)
        self.ui.SaveCourse.clicked.connect(self.AddCourse)

    
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Event Handlers
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def set_addCourse(self):
        self.ChangeWidget(2)

    def set_addStudent(self):
        self.ChangeWidget(1)

    



    # Edit mode Condition
    def set_edit_mode(self):
        self.current_mode = "Edit"
        self.ChangeWidget(7)
        self.EditState()
       

    # Delete mode Condition
    def set_delete_mode(self):
        self.current_mode = "Delete"
        self.ChangeWidget(5)
        self.DeleteState()

    # View mode condition
    def set_view_mode(self):
        self.current_mode = "View"
        self.ChangeWidget(0)
        self.ViewState()


    def EditState(self):
        if self.current_mode == "Edit":
            QMessageBox.information(self.main_window, "Edit Mode active", "You are currently using edit mode")
            

    def DeleteState(self):
        if self.current_mode == "Delete":
            QMessageBox.information(self.main_window, "Delete Mode active", "You are currently using delete mode")

    def ViewState(self):
        if self.current_mode == "View":
            QMessageBox.information(self.main_window, "View Mode active", "You are currently using view mode")
            
            
    

    
    
    def Mode_Handler(self, item):

        # Edit mode initialization
        if self.current_mode == "Edit":
            if item.tableWidget() == self.ui.CourseTable:  # Use self.ui.CourseTable
                # Change the stacked widget to the corresponding index for course table in edit mode
                self.ChangeWidget(4)
                self.ui.CourseTable.itemClicked.connect(self.CourseSelect)

                
            elif item.tableWidget() == self.ui.StudentTable:  # Use self.ui.StudentTable
                # Change the stacked widget to the corresponding index for student table in edit mode
                self.ChangeWidget(3)
                self.ui.StudentTable.itemClicked.connect(self.StudentSelect)

                
        # Delete mode initialization
        elif self.current_mode == "Delete":
            
            

            if item.tableWidget() == self.ui.CourseTable:  # Use self.ui.CourseTable
                # Change the stacked widget to the corresponding index for course table in edit mode
                self.ChangeWidget(5)
                self.ui.CourseTable.clicked.connect(self.confirmDeleteCourse)
                

            elif item.tableWidget() == self.ui.StudentTable:  # Use self.ui.StudentTable
                # Change the stacked widget to the corresponding index for student table in edit mode
                self.ChangeWidget(5)
                self.ui.StudentTable.clicked.connect(self.confirmDeleteStudent)

                

        # View mode initialization
        else:
            self.ChangeWidget(0)
            
       
            
        


    # Functionality for changing Stacked Widgets
    def ChangeWidget(self, index):
        self.ui.SideStackWidget.setCurrentIndex(index)



    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Course Operations
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    # Updates the course table everytime a change is made
    def UpdateCourseTable(self):
        self.ui.CourseTable.clearContents()  # Clear the table contents

        # Collect course data in a list of tuples
        course_data = []                                                        # Creates a data structure to store the course tuples
        for course_code, course in self.course_operations.courses.items():      # Loops through the dictionary using course code as keys
            course_tuple = (course_code, course.course_name)                    # Creates course tuple for each course
            course_data.append(course_tuple)                                    # Appends the created tuple to the data structure

        sorted_course_data = sorted(course_data, key=lambda x: x[0])            # Sort course data based on course code

        total_rows = len(sorted_course_data)                                    # Gets the total number of courses
        self.ui.CourseTable.setRowCount(total_rows)                             # Sets the number of rows in the table
        self.ui.CourseTable.setColumnCount(2)                                   # Sets the number of columns in the table

        # Populate the table with sorted data
        for count, course_tuple in enumerate(sorted_course_data):
            course_code, course_name = course_tuple                             # Unpacks tuple and assigns to variables
            course_code_item = QTableWidgetItem(course_code)                    # Creates QTableWidgetItem for course code
            course_name_item = QTableWidgetItem(course_name)                    # Creates QTableWidgetItem for course name

            # Set the text color for the items
            course_code_item.setForeground(QColor("#00C9FF"))                   # Set text color to #00C9FF
            course_name_item.setForeground(QColor("#00C9FF"))                   # Set text color to #00C9FF

            self.ui.CourseTable.setItem(count, 0, course_code_item)             # Sets course code in the first column
            self.ui.CourseTable.setItem(count, 1, course_name_item)



    # Function that handles adding course 
    # Handling format and conditions for course
    def AddCourse(self):
        try:
            course_name = self.ui.CourseNameAdd.toPlainText()
            course_code = self.ui.CourseCodeAdd.text()

            if course_code and course_name:
                # Check if student ID or name already exists
                for existing_course_code, existing_course in self.course_operations.courses.items():
                    if existing_course_code == course_code or existing_course.course_name == course_name:
                        QMessageBox.critical(self.main_window, "Add Course Error", "Course Code or Course Name already exists.")
                        return
                course = Course(course_name,course_code)

                self.ui.CourseNameAdd.clear()
                self.ui.CourseCodeAdd.clear()
                if self.course_operations.add_course(course):
                    self.UpdateCourseTable()
                    self.UpdateComboBoxCourse()
                    self.UpdateComboBoxCourse_EDIT()
                    QMessageBox.information(self.main_window, "Course Add Successful", "Course Added Successfully.") 
            else:
                QMessageBox.critical(self.main_window, "Insufficient Arguments", "Please fill in all required items.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")
        return  


    # Function that sends the course code of the course to be deleted in the course operations
    def deleteCourse(self):
        try:
            
            item = self.ui.DeleteOutput.text()                                      # Get the course code as text
            if item:
                course_code = item   
                
                # Update the enrollment status of students in the deleted course
                for i in range(self.ui.StudentTable.rowCount()):
                    course_code_item = self.ui.StudentTable.item(i, 4)              # Get the course code item for the current student
                    if course_code_item and course_code_item.text() == course_code:
                        course_code_item.setText("Not Enrolled")                    # Update the course code to "Not Enrolled"
                        
                # Delete the course and update UI
                if self.course_operations.delete_course(course_code):
                    
                    # Update the UI from the changes
                    self.UpdateCourseTable()
                    self.UpdateComboBoxCourse_EDIT()  
                    self.UpdateComboBoxCourse()
                    QMessageBox.information(self.main_window, "Course Deletion", "Course deleted successfully.")
                    self.ui.DeleteOutput.setText("")
                    
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")


    # Displays course for deletion in StackedWidget
    def confirmDeleteCourse(self, item):
        try:
            
            # Get the row and course code to be deleted
            row = item.row()
            course_code_item = self.ui.CourseTable.item(row, 0)
            course_code = course_code_item.text()

            if course_code:
                
                self.ui.DeleteOutput.setText(course_code)
                self.ui.ExecuteDelete.clicked.connect(self.deleteCourse)

        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")



    # Getter method for old student ID
    def getOldCourseCode(self):
        return self.old_course_code

    # Setter method for old student ID
    def setOldCourseCode(self, old_course_code):
        self.old_course_code = old_course_code



    # Displays the course information that has been clicked into the LineEdits for Editing
    def CourseSelect(self,item):
        
        row = item.row()
        course_code_item = self.ui.CourseTable.item(row, 0)
        course_name_item = self.ui.CourseTable.item(row, 1)

        if course_code_item and course_name_item:
            course_code = course_code_item.text()
            self.setOldCourseCode(course_code)
            course_name = course_name_item.text()

            # Display the selected course in line edits
            self.ui.CourseCodeCourseEdit.setText(course_code)
            self.ui.CourseNameEdit.setText(course_name)



    # Function that updates course and displays changes in the student and course table
    def UpdateCourse(self):
        try:
            if (self.ui.CourseNameEdit and self.ui.CourseCodeCourseEdit):
                course_code_edited = self.ui.CourseCodeCourseEdit.text()
                old_course_code = self.getOldCourseCode()

                # Check if the new student ID is unique
                for key in self.course_operations.courses.keys():

                    # Skip the old student ID
                    # It means the Course Name is the only element that is updated
                    if key == old_course_code:
                        continue
                    
                    # Check if the current student ID matches any other student ID
                    if key == course_code_edited:
                        QMessageBox.critical(self.main_window, "Error", "Course Code must be Unique.")
                        return


                self.course_operations.update_course(old_course_code,course_code_edited,self.ui.CourseNameEdit.toPlainText())
                

                # Update the enrollment status of students in the deleted course
                for i in range(self.ui.StudentTable.rowCount()):
                    course_code_item = self.ui.StudentTable.item(i, 4)  # Get the course code item for the current student
                    if course_code_item and course_code_item.text() == old_course_code:
                        course_code_item.setText(course_code_edited)  # Update the course code to "Not Enrolled"
                        

                # Update the UI from the changes
                self.UpdateCourseTable()
                self.UpdateComboBoxCourse_EDIT()
                self.UpdateComboBoxCourse()
                QMessageBox.information(self.main_window, "Success", "Course information updated successfully.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")



    # Search Course and display results in Course table
    def search_course(self):
        try:
            # Get the search input from the SearchCourse LineEdit
            search_input = self.ui.SearchCourse.text().lower()

            
            # Clear the table contents before populating with search results
            self.ui.CourseTable.clearContents()

            # Filter the courses based on the search input (partial matching)
            filtered_courses = []
            for course_code, course in self.course_operations.courses.items():
                if search_input in course_code.lower():                 # Check if the search input is a partial match for the course code
                    course_tuple = (course_code, course.course_name)
                    filtered_courses.append(course_tuple)

            # Check if any courses are found based on the search input
            if not filtered_courses:
                QMessageBox.warning(self.main_window, "Search Course Error", "No courses found")
                return

            total_rows = len(filtered_courses)                          # Get the total number of filtered courses
            self.ui.CourseTable.setRowCount(total_rows)                 # Set the number of rows in the table
            self.ui.CourseTable.setColumnCount(2)                       # Set the number of columns in the table

            # Populate the table with filtered course data and set text color
            for count, course_tuple in enumerate(filtered_courses):
                course_code, course_name = course_tuple
                course_code_item = QTableWidgetItem(course_code)
                course_name_item = QTableWidgetItem(course_name)

                # Set text color for all items in the row
                course_code_item.setForeground(QColor("#00C9FF"))
                course_name_item.setForeground(QColor("#00C9FF"))

                self.ui.CourseTable.setItem(count, 0, course_code_item)
                self.ui.CourseTable.setItem(count, 1, course_name_item)
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")

        

    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Students Operations
    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    # Updates the students table everytime a change is made
    def UpdateStudentTable(self):
        self.ui.StudentTable.clearContents()  # Clear the table contents

        # Collect student data in a list of tuples
        student_data = []
        for student_id, student in self.student_operations.students.items():
            student_tuple = (student_id, student.Name, student.Gender, student.Year_level, student.Course_code)
            student_data.append(student_tuple)

        sorted_student_data = sorted(student_data, key=lambda x: x[0])  # Sort student data based on student ID

        total_rows = len(sorted_student_data)  # Get the total number of students
        self.ui.StudentTable.setRowCount(total_rows)  # Set the number of rows in the table
        self.ui.StudentTable.setColumnCount(5)  # Set the number of columns in the table

        # Populate the table with sorted data and set text color
        for count, student_tuple in enumerate(sorted_student_data):
            student_id, name, gender, year_level, course_code = student_tuple
            student_id_item = QTableWidgetItem(student_id)
            name_item = QTableWidgetItem(name)
            gender_item = QTableWidgetItem(gender)
            year_level_item = QTableWidgetItem(year_level)
            course_code_item = QTableWidgetItem(course_code)

            # Set text color for all items in the row
            student_id_item.setForeground(QColor("#00C9FF"))
            name_item.setForeground(QColor("#00C9FF"))
            gender_item.setForeground(QColor("#00C9FF"))
            year_level_item.setForeground(QColor("#00C9FF"))
            course_code_item.setForeground(QColor("#00C9FF"))

            self.ui.StudentTable.setItem(count, 0, student_id_item)
            self.ui.StudentTable.setItem(count, 1, name_item)
            self.ui.StudentTable.setItem(count, 3, gender_item)
            self.ui.StudentTable.setItem(count, 2, year_level_item)
            self.ui.StudentTable.setItem(count, 4, course_code_item)




    # Getter method for old student ID
    def getOldStudentID(self):
        return self.old_student_id

    # Setter method for old student ID
    def setOldStudentID(self, old_student_id):
        self.old_student_id = old_student_id


    
    # Displays the student information that has been clicked into the LineEdits for Editing
    def StudentSelect(self, item):
        row = item.row()
        student_id_item = self.ui.StudentTable.item(row, 0)
        name_item = self.ui.StudentTable.item(row, 1)
        gender_item = self.ui.StudentTable.item(row, 3)
        year_level_item = self.ui.StudentTable.item(row, 2)
        course_code_item = self.ui.StudentTable.item(row, 4)

        if student_id_item and name_item and gender_item and year_level_item and course_code_item:
            student_id = student_id_item.text()
            self.setOldStudentID(student_id)
            name = name_item.text()
            gender = gender_item.text()
            year_level = year_level_item.text()
            course_code = course_code_item.text()

            # Display the selected student in line edits
            self.ui.StudentIDEdit.setText(student_id)
            self.ui.NameEdit.setText(name)
            self.ui.YearLevelEdit.setText(year_level)
            
            # Set the selected item in the GenderEdit QComboBox
            gender_index = self.ui.GenderEdit.findText(gender, QtCore.Qt.MatchFixedString)
            if gender_index >= 0:
                self.ui.GenderEdit.setCurrentIndex(gender_index)

            # Set the selected item in the CourseCodeEdit QComboBox
            course_code_index = self.ui.CouseCodeEdit.findText(course_code, QtCore.Qt.MatchFixedString)
            if course_code_index >= 0:
                self.ui.CouseCodeEdit.setCurrentIndex(course_code_index)

            

    # Function that updates a student and displays changes in the student table
    def UpdateStudent(self):
        try:
            # Check if the required data is not None
            if (
                self.ui.StudentIDEdit.text()
                and self.ui.NameEdit.text()
                and self.ui.GenderEdit.currentText()
                and self.ui.YearLevelEdit.text()
                and self.ui.CouseCodeEdit.currentText()
            ):
                # Check if student_id is in the format XXXX-XXXX
                student_id = self.ui.StudentIDEdit.text()
                student_name = self.ui.NameEdit.text()
                if len(student_id) == 9 and student_id[4] == '-':
                    
                    old_student_id = self.getOldStudentID()
                    #old_student_name = self.getOldStudentName()
                    
                     # Check if the new student ID is unique
                    for key in self.student_operations.students.keys():
                        # Skip the old student ID
                        if key == old_student_id:
                            continue
                        
                        # Check if the current student ID matches any other student ID
                        if key == student_id:
                            QMessageBox.critical(self.main_window, "Update Student Error", "Student ID already in use.")
                            return
                       

                    self.student_operations.update_student(old_student_id,student_id, self.ui.NameEdit.text(), self.ui.GenderEdit.currentText(), self.ui.YearLevelEdit.text(), self.ui.CouseCodeEdit.currentText())
                    
                    self.UpdateStudentTable()
                    
                    # Show success message
                    QMessageBox.information(self.main_window, "Update Student Success", "Student information updated successfully.")
                else:
                    # Display an error message or handle the case where student_id format is incorrect
                    QMessageBox.critical(self.main_window, "Update Student Error", "Student ID format should be XXXX-XXXX.")
            else:
                # Display an error message or handle the case where data is missing
                QMessageBox.critical(self.main_window, "Error", "Please fill in all required fields.")
        except Exception as e:
            # Display an error message if an exception occurs during the update process
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")
    


    # Function that sends the student id of the student to be deleted in the student operations
    def deleteStudent(self):
        try:
            #row = item.row()
            #student_id_item = self.ui.StudentTable.item(row,0)
            item = self.ui.DeleteOutput.text()
            if item:
                student_id = item
                if self.student_operations.delete_student(student_id):
                    #self.ui.StudentTable.removeRow(row)
                    self.UpdateStudentTable()
                    QMessageBox.information(self.main_window, "Student Deletion", "Student deleted successfully.")
                    self.ui.DeleteOutput.setText("")

        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")


    # Displays student for deletion in StackedWidget 
    def confirmDeleteStudent(self,item):
        try:
            #self.ChangeWidget(6)
            row = item.row()
            student_id_item = self.ui.StudentTable.item(row,0)
            student_id = student_id_item.text()

            if student_id:
                
                self.ui.DeleteOutput.setText(student_id)
                self.ui.ExecuteDelete.clicked.connect(self.deleteStudent)  

        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")
    


    # Function that handles adding course 
    # Handling format and conditions for course
    def AddStudent(self):
        try:
            student_name = self.ui.Name.text()
            YearLvl = self.ui.YearLevel.text()
            gender = self.ui.Gender.currentText()
            studentID = self.ui.StudentID.text()
            course_code = self.ui.CouseCode.currentText()

            if student_name and YearLvl and gender and studentID and course_code:
                # Check if student ID or name already exists
                for existing_student_id, existing_student in self.student_operations.students.items():
                    if existing_student_id == studentID or existing_student.Name == student_name:
                        QMessageBox.critical(self.main_window, "Enrollment Error", "Student ID or Name already exists.")
                        return

                student = Student(studentID, student_name, gender, YearLvl, course_code)

                self.ui.Name.clear()
                self.ui.YearLevel.clear()
                self.ui.StudentID.clear()

                if self.student_operations.add_student(student):
                    self.UpdateStudentTable()
                    QMessageBox.information(self.main_window, "Enrollment Successful", "Student Enrolled Successfully.")  
            else:
                QMessageBox.critical(self.main_window, "Insufficient Arguments", "Please fill in all required items.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")
    
    

   
    # Search Student and display results in Students table
    def search_student(self):
        try:
            # Get the search input from the SearchStudent LineEdit
            search_input = self.ui.SearchStudent.text()

            # Check if the search input exceeds 9 characters
            if len(search_input) > 9:
                QMessageBox.warning(self.main_window, "Input Error", "Please do not exceed student ID format XXXX-XXXX")
                return

            # Clear the table contents before populating with search results
            self.ui.StudentTable.clearContents()

            # Filter the students based on the search input (partial matching)
            filtered_students = []
            for student_id, student in self.student_operations.students.items():
                if search_input in student_id:                                          # Check if the search input is a partial match for the student ID
                    student_tuple = (student_id, student.Name, student.Gender, student.Year_level, student.Course_code)
                    filtered_students.append(student_tuple)

            # Check if any students are found based on the search input
            if not filtered_students:
                QMessageBox.warning(self.main_window, "Search Student Error", "No students found")
                return

            total_rows = len(filtered_students)                                         # Get the total number of filtered students
            self.ui.StudentTable.setRowCount(total_rows)                                # Set the number of rows in the table
            self.ui.StudentTable.setColumnCount(5)                                      # Set the number of columns in the table

            # Populate the table with filtered student data and set text color
            for count, student_tuple in enumerate(filtered_students):
                student_id, name, gender, year_level, course_code = student_tuple
                student_id_item = QTableWidgetItem(student_id)
                name_item = QTableWidgetItem(name)
                gender_item = QTableWidgetItem(gender)
                year_level_item = QTableWidgetItem(year_level)
                course_code_item = QTableWidgetItem(course_code)

                # Set text color for all items in the row
                student_id_item.setForeground(QColor("#00C9FF"))
                name_item.setForeground(QColor("#00C9FF"))
                gender_item.setForeground(QColor("#00C9FF"))
                year_level_item.setForeground(QColor("#00C9FF"))
                course_code_item.setForeground(QColor("#00C9FF"))

                self.ui.StudentTable.setItem(count, 0, student_id_item)
                self.ui.StudentTable.setItem(count, 1, name_item)
                self.ui.StudentTable.setItem(count, 3, gender_item)
                self.ui.StudentTable.setItem(count, 2, year_level_item)
                self.ui.StudentTable.setItem(count, 4, course_code_item)
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An error occurred: {str(e)}")


    # Functions that updates comboboxes from Course Codes and Genders


    def update_gender_combobox_EDIT(self):
        # Clear existing items in the GenderEdit QComboBox
        self.ui.GenderEdit.clear()
        self.gender_options = ["Male", "Female"]
        # Add items to the GenderEdit QComboBox based on the gender_options list
        self.ui.GenderEdit.addItems(self.gender_options)


        # Set the item text color directly in the combobox's model
        model = self.ui.GenderEdit.model()
        for i in range(model.rowCount()):
            index = model.index(i, self.ui.GenderEdit.modelColumn())
            model.setData(index, QColor("#00C9FF"), role=Qt.TextColorRole)


    def UpdateComboBoxCourse_EDIT(self):
        self.ui.CouseCodeEdit.clear()  # Clear the comboBox first

        # Get all available course codes from course_operations
        course_codes = [course.course_code for course in self.course_operations.courses.values()]

        # Add the course codes to the comboBox with colors
        for course_code in course_codes:
            index = self.ui.CouseCodeEdit.addItem(course_code)  # Get the index directly
            

        # Set the item text color directly in the combobox's model
        model = self.ui.CouseCodeEdit.model()
        for i in range(model.rowCount()):
            index = model.index(i, self.ui.CouseCodeEdit.modelColumn())
            model.setData(index, QColor("#00C9FF"), role=Qt.TextColorRole)


    def UpdateComboBoxCourse(self):

        # Clear the comboBox first
        self.ui.CouseCode.clear()   

        # Get all available course codes from course_operations
        course_codes = [course.course_code for course in self.course_operations.courses.values()]

        # Add the course codes to the comboBox with colors
        for course_code in course_codes:
             # Get the index directly
            index = self.ui.CouseCode.addItem(course_code)     
            

        # Set the item text color directly in the combobox's model
        model = self.ui.CouseCode.model()
        for i in range(model.rowCount()):
            index = model.index(i, self.ui.CouseCode.modelColumn())
            model.setData(index, QColor("#00C9FF"), role=Qt.TextColorRole)


    def update_gender_combobox(self):
        # Clear existing items in the GenderEdit QComboBox
        self.ui.Gender.clear()
        self.gender_options = ["Male", "Female"]
        # Add items to the GenderEdit QComboBox based on the gender_options list
        self.ui.Gender.addItems(self.gender_options)


        # Set the item text color directly in the combobox's model
        model = self.ui.Gender.model()
        for i in range(model.rowCount()):
            index = model.index(i, self.ui.Gender.modelColumn())
            model.setData(index, QColor("#00C9FF"), role=Qt.TextColorRole)




    # Default function that needs to run as the program starts
    def run(self):
        self.UpdateComboBoxCourse()
        self.UpdateComboBoxCourse_EDIT()
        self.update_gender_combobox()
        self.update_gender_combobox_EDIT()
        self.UpdateStudentTable()
        self.UpdateCourseTable()
        self.ChangeWidget(0)
        self.main_window.show()
        self.app.exec_()
        

# Main function
if __name__ == "__main__":
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QApplication.setStyle(QStyleFactory.create("Fusion"))
    controller = Controller()
    controller.run()








    