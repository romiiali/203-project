class People:
    def __init__(self, name, id, role):
        self.id = id
        self.name = name
        self.role = role

    def get_all_people(self):
        return [
            People("John Smith", "P001", "Student"),            
            People("Emily Chen", "P002", "Student"),
            People("Mike Wilson", "P003", "Student"),           
            People("Lisa Garcia", "P004", "Student"),
            People("David Lee", "P005", "Student"),             
            People("Anna Taylor", "P006", "Student")
        ]

    def get_person(self, id):
        people_data = self.get_all_people()
        for person in people_data:
            if person.id == id:
                return person
        return None
    
    def add_person(self, name, id, role):
        new_person = People(name, id, role)
        people_data = self.get_all_people()
        people_data.append(new_person)
        return people_data
    
    def edit_person(self, name, id, role):
        people_data = self.get_all_people()
        for person in people_data:
            if person.id == id:
                person.name = name
                person.role = role
                return person
        return None

    def delete_person(self, id):
        people_data = self.get_all_people()
        for person in people_data:
            if person.id == id:
                people_data.remove(person)
                return people_data
        return None
    
    def get_person_by_role(self, role):
        people_data = self.get_all_people()
        filtered_people = [person for person in people_data if person.role == role]
        return filtered_people
    
    def search_people(self, search_term=""):
        people_data = self.get_all_people()
        
        if not search_term or search_term.strip() == "":
            return people_data
        
        search_term = search_term.lower().strip()
        matching_people = []
        
        for person in people_data:
            if (search_term in person.name.lower() or 
                search_term in person.role.lower() or
                search_term in person.id.lower()):
                matching_people.append(person)
        
        return matching_people