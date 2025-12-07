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
        elif course_id == 3:
            assignments.append(Assignment(4, "Essay 1", "500-word essay", "2023-11-25", 3))
        elif course_id == 4:
            assignments.append(Assignment(5, "Lab Report 1", "Physics lab report", "2023-11-30", 4))
        return assignments
    
    @staticmethod
    def get_by_id(assignment_id):
        assignments = []
        assignments.extend(Assignment.get_by_course(1))
        assignments.extend(Assignment.get_by_course(2))
        assignments.extend(Assignment.get_by_course(3))
        assignments.extend(Assignment.get_by_course(4))
        
        for assignment in assignments:
            if assignment.id == assignment_id:
                return assignment
        return None
    
    def add_submission(self, student_id, submission_text):
        if student_id not in self.submissions:
            self.submissions[student_id] = {
                'text': submission_text,
                'grade': None,
                'feedback': None,
                'submitted': True,
                'timestamp': '2023-10-20'
            }
            return True, "Submission successful"
        return False, "Already submitted"
    
    def grade_submission(self, student_id, grade, feedback=""):
        if student_id in self.submissions:
            self.submissions[student_id]['grade'] = grade
            self.submissions[student_id]['feedback'] = feedback
            return True, "Grade submitted"
        return False, "Student submission not found"
    
    def get_submission(self, student_id):
        return self.submissions.get(student_id)
    
    def get_all_submissions(self):
        return self.submissions
    
    def get_submission_status(self, student_id):
        if student_id in self.submissions:
            submission = self.submissions[student_id]
            return {
                'submitted': True,
                'grade': submission['grade'],
                'timestamp': submission['timestamp']
            }
        return {'submitted': False, 'grade': None, 'timestamp': None}