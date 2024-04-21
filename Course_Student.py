import mysql.connector


'''
Contents of this file:
1.Class that creates student object
2.Class that creates course object
3.Class that performs operations on students
4.Class that performs operations on course 
'''



# Establish Connection between python file and database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2022-1729",
    database="SSIS_DATABASE"
)

mycursor = db.cursor()

# Class that creates the course object
class Course:
    def __init__(self, course_name, course_code) -> None:
        self.course_name = course_name
        self.course_code = course_code



# Class that contains operations on all Courses
class CourseOperations:
    def __init__(self, host, user, password, database) -> None:
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.mycursor = self.mydb.cursor()                              # Creates Cursor for database queries
        self.courses = self.load_courses_from_mysql()                   # Dictionary that contains the courses loaded from the database


    # Loader function that retrieves data from the database and stores in the dictionary
    def load_courses_from_mysql(self):
        courses = {}                        
        self.mycursor.execute("SELECT * FROM COURSES")
        rows = self.mycursor.fetchall()
        for row in rows:
            course_code = row[0]
            course_name = row[1]  
            courses[course_code] = Course(course_name=course_name, course_code=course_code)
        return courses

    
    # Save function that saves the updated version of the dictionary to the database
    # Checks if the course already exists: If so then Update : If not then Insert
    def save_courses_to_mysql(self):
        for course_code in self.courses:
            course_name = self.courses[course_code].course_name
            sql_check = "SELECT * FROM COURSES WHERE course_code = %s"
            self.mycursor.execute(sql_check, (course_code,))
            existing_course = self.mycursor.fetchone()
            if existing_course:
                # Course exists, update it
                sql_update = "UPDATE COURSES SET course_name = %s WHERE course_code = %s"
                values_update = (course_name, course_code)
                self.mycursor.execute(sql_update, values_update)
            else:
                # Course does not exist, insert it
                sql_insert = "INSERT INTO COURSES (course_code, course_name) VALUES (%s, %s)"
                values_insert = (course_code, course_name)
                self.mycursor.execute(sql_insert, values_insert)
        self.mydb.commit()
    



    # Adds the course to the dictionary and calls the save function to save action
    def add_course(self, course):
        # Check if the course already exists
        if course.course_code in self.courses:
            return False                                     

        self.courses[course.course_code] = course
        self.save_courses_to_mysql()
        return True                                         




    # Deletes the course by calling the DeleteCourse Stored Procedure 
    def delete_course(self, course_code):
        if course_code in self.courses:  # Check if the course code exists in the courses Dictionary
            # Delete the course from the courses table
            sql_delete_course = "CALL DeleteCourse(%s)"
            self.mycursor.execute(sql_delete_course, (course_code,))
            self.mydb.commit()

            # Update the local courses dictionary
            self.courses.pop(course_code)
            self.save_courses_to_mysql()

            return True  # Return True for successful action
        else:
            return False  # Return False for unsuccessful action

   
    
    # Updates the course by calling the UpdateCourse Procedure
    # Also updates local dictionary
    def update_course(self, course_code_old, course_code_new, course_name_new):
        sql_update_course = "CALL UpdateCourse(%s, %s, %s)"
        values_update_course = (course_code_new, course_name_new, course_code_old)
        self.mycursor.execute(sql_update_course, values_update_course)
        self.mydb.commit()
        

        if course_code_old in self.courses:
            course_obj = self.courses.pop(course_code_old)  # Remove the old course object
            course_obj.course_code = course_code_new  # Update the course code
            course_obj.course_name = course_name_new  # Update the course name
            self.courses[course_code_new] = course_obj 



# Class that creates Student object
class Student:
    def __init__(self, Student_id, Name, Gender, Year_level, Course_code) -> None:
        self.Student_id = Student_id
        self.Name = Name
        self.Year_level = Year_level
        self.Gender = Gender
        self.Course_code = Course_code

    
# Class that contains operations on all Students
class StudentOperations:
    def __init__(self, host, user, password, database) -> None:
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.mycursor = self.mydb.cursor()                       # Creates Cursor for database queries
        self.students = self.load_students_from_mysql()          # Dictionary that contains the students loaded from the database


    # Loader function that retrieves data from the database and stores in the dictionary
    def load_students_from_mysql(self):
        students = {}
        self.mycursor.execute("SELECT * FROM STUDENTS")
        rows = self.mycursor.fetchall()
        for row in rows:
            student_id = row[0]  # Assuming the first column is student ID
            name = row[1]  # Assuming the second column is Name
            gender = row[2]  # Assuming the fifth column is Gender
            year_level = row[3]  # Assuming the fourth column is Year_level
            course_code = row[4]  # Assuming the sixth column is Course_code
            students[student_id] = Student(Student_id=student_id, Name=name,
                                           Year_level=year_level, Gender=gender, Course_code=course_code)
        return students
    

    # Save function that saves the updated version of the dictionary to the database
    # Checks if the student already exists: If so then Update : If not then Insert
    def save_students_to_mysql(self):
        for student_id, student in self.students.items():
            student_name = student.Name
            student_gender = student.Gender
            student_yearlvl = student.Year_level
            student_course_code = student.Course_code

            sql_check = "SELECT * FROM STUDENTS WHERE student_id = %s"
            self.mycursor.execute(sql_check, (student_id,))
            existing_student = self.mycursor.fetchone()
            if existing_student:
                # Student exists, update it
                sql_update = "UPDATE STUDENTS SET Student_Name = %s, Gender = %s, Year_lvl = %s, Course_Code = %s WHERE student_ID = %s"
                values_update = (student_name, student_gender, student_yearlvl, student_course_code, student_id)
                self.mycursor.execute(sql_update, values_update)
            else:
                # Student does not exist, insert it
                sql_insert = "INSERT INTO STUDENTS (Student_ID, Student_Name, Gender, Year_lvl, Course_Code) VALUES (%s, %s, %s, %s, %s)"
                values_insert = (student_id, student_name, student_gender, student_yearlvl, student_course_code)
                self.mycursor.execute(sql_insert, values_insert)

        self.mydb.commit()
        

    # Adds the course to the dictionary and calls the save function to save action
    def add_student(self, student):

        # Check if the student ID already exists
        if student.Student_id in self.students:
            return False                        # Student already exists
        self.students[student.Student_id] = student
        self.save_students_to_mysql()
        return True                             # Student added successfully



    # Deletes the student using the DELETE FROM query directly
    def delete_student(self, student_id):
        if student_id in self.students:
            del self.students[student_id]
            sql_delete_student = "DELETE FROM STUDENTS WHERE Student_id = %s"
            self.mycursor.execute(sql_delete_student, (student_id,))
            self.mydb.commit()
            return True  # Student deleted successfully
        else:
            return False  # Student not found
        

    # Updates the course by calling the UpdateStudent Procedure
    # Also updates local dictionary
    def update_student(self, student_id_old, student_id_new, student_name_new, gender_new, year_lvl_new, course_code_new):
        sql_update_student = "CALL UpdateStudent(%s, %s, %s, %s, %s, %s)"
        values_update_student = (student_id_new, student_name_new, gender_new, year_lvl_new, course_code_new, student_id_old)
        self.mycursor.execute(sql_update_student, values_update_student)
        self.mydb.commit()
        #self.load_students_from_mysql()

        if student_id_old in self.students:
            student_obj = self.students.pop(student_id_old)  # Remove the old student object
            student_obj.Student_id = student_id_new  # Update the student ID
            student_obj.Name = student_name_new  # Update the student name
            student_obj.Gender = gender_new  # Update the gender
            student_obj.Year_level = year_lvl_new  # Update the year level
            student_obj.Course_code = course_code_new  # Update the course code
            self.students[student_id_new] = student_obj
        

