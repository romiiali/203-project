class Assignment:
    def __init__(self, id, title, description, due_date, course_id):
        self.id = id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.course_id = course_id
        self.submissions = {}
    
    @staticmethod
    def get_by_course(course_id):
        assignments = []
        if course_id == 1:
            assignments.append(Assignment(1, "Assignment 1", "First assignment", "2023-11-15", 1))
            assignments.append(Assignment(2, "Assignment 2", "Second assignment", "2023-12-01", 1))
        elif course_id == 2:
            assignments.append(Assignment(3, "Calculus Homework", "Chapter 1 problems", "2023-11-20", 2))
        return assignments
    
    def add_submission(self, student_id, submission_text):
        if student_id not in self.submissions:
            self.submissions[student_id] = {
                'text': submission_text,
                'grade': None,
                'timestamp': '2023-10-20'
            }
            return True, "Submission successful"
        return False, "Already submitted"
    
    def grade_submission(self, student_id, grade):
        if student_id in self.submissions:
            self.submissions[student_id]['grade'] = grade
            return True, "Grade submitted"
        return False, "Student submission not found"
    
    def get_submission(self, student_id):
        return self.submissions.get(student_id)