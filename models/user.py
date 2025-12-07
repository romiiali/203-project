class User:
    def __init__(self, id, name, email, password, role):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
    
    @staticmethod
    def login(email, password):
        users = [
            User(1, "John Doe", "john@student.edu", "pass123", "student"),
            User(2, "Dr. Sarah Johnson", "sarah@instructor.edu", "pass123", "instructor"),
            User(3, "Alex Chen", "alex@ta.edu", "pass123", "ta"),
            User(4, "Admin User", "admin@university.edu", "pass123", "admin")
        ]
        
        for user in users:
            if user.email == email and user.password == password:
                return user
        return None
    
    @staticmethod
    def get_by_id(user_id):
        users = [
            User(1, "John Doe", "john@student.edu", "pass123", "student"),
            User(2, "Dr. Sarah Johnson", "sarah@instructor.edu", "pass123", "instructor"),
            User(3, "Alex Chen", "alex@ta.edu", "pass123", "ta"),
            User(4, "Admin User", "admin@university.edu", "pass123", "admin")
        ]
        
        for user in users:
            if user.id == user_id:
                return user
        return None
    
    @staticmethod
    def search_users_by_role(role):
        users = [
            User(1, "John Doe", "john@student.edu", "pass123", "student"),
            User(2, "Dr. Sarah Johnson", "sarah@instructor.edu", "pass123", "instructor"),
            User(3, "Alex Chen", "alex@ta.edu", "pass123", "ta"),
            User(4, "Admin User", "admin@university.edu", "pass123", "admin"),
            User(5, "Jane Smith", "jane@student.edu", "pass123", "student"),
            User(6, "Mike Johnson", "mike@student.edu", "pass123", "student")
        ]
        
        return [user for user in users if user.role == role]
    
    @staticmethod
    def search_users(query=""):
        users = [
            User(1, "John Doe", "john@student.edu", "pass123", "student"),
            User(2, "Dr. Sarah Johnson", "sarah@instructor.edu", "pass123", "instructor"),
            User(3, "Alex Chen", "alex@ta.edu", "pass123", "ta"),
            User(4, "Admin User", "admin@university.edu", "pass123", "admin"),
            User(5, "Jane Smith", "jane@student.edu", "pass123", "student"),
            User(6, "Mike Johnson", "mike@student.edu", "pass123", "student")
        ]
        
        if not query:
            return users
        
        query = query.lower()
        results = []
        for user in users:
            if (query in user.name.lower() or 
                query in user.email.lower() or 
                query in user.role.lower()):
                results.append(user)
        
        return results