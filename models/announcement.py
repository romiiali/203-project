<<<<<<< HEAD
class Announcement:
    def __init__(self, id, title, content, poster_id, course_id):
        self.id = id
        self.title = title
        self.content = content
        self.poster_id = poster_id
        self.course_id = course_id
        self.timestamp = "2023-10-15"
    
    @staticmethod
    def get_by_course(course_id):
        announcements = []
        if course_id == 1:
            announcements.append(Announcement(1, "Welcome to CSAI 203", "Welcome message", 2, 1))
            announcements.append(Announcement(2, "Midterm Exam", "Midterm details", 2, 1))
        elif course_id == 2:
            announcements.append(Announcement(3, "Calculus Syllabus", "Syllabus posted", 2, 2))
=======
class Announcement:
    def __init__(self, id, title, content, poster_id, course_id):
        self.id = id
        self.title = title
        self.content = content
        self.poster_id = poster_id
        self.course_id = course_id
        self.timestamp = "2023-10-15"
    
    @staticmethod
    def get_by_course(course_id):
        announcements = []
        if course_id == 1:
            announcements.append(Announcement(1, "Welcome to CSAI 203", "Welcome message", 2, 1))
            announcements.append(Announcement(2, "Midterm Exam", "Midterm details", 2, 1))
        elif course_id == 2:
            announcements.append(Announcement(3, "Calculus Syllabus", "Syllabus posted", 2, 2))
>>>>>>> 20617a8a8979aaf50a951e6b8ac6723f6f13f32b
        return announcements