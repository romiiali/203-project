class Assignment:
    def __init__(self, title, description, due_date, grade):
        self.title = title
        self.description = description
        self.due_date = due_date
        self.grade = grade

    def save_to_db(self):
        print(f"Saving assignment: {self.title} to database...")
        return True
        