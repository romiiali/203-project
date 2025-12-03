class People:
    def __init__(self,name,id,role):
        self.id = id
        self.name=name
        self.role = role

    def get_all_people(self):
        return[
            People("John Smith", "P001", "Student"),            
            People("Emily Chen", "P002", "Student"),
            People("Mike Wilson", "P003", "Student"),           
            People("Lisa Garcia", "P004", "Student"),
            People("David Lee", "P005", "Student"),             
            People("Anna Taylor", "P006", "Student")
        ]

    def get_pearson(self,id):
        people_data = self.get_all_people()
        for pearson in people_data:
            if pearson.id == id:
                return pearson
        return None
    
    def add_pearson(self,name,id,role):
        new_pearson= People(name,id,role)
        people_data = self.get_all_people()
        people_data.append(new_pearson)
        return people_data
    
    def edit_person(self,name,id,role):
        people_data = self.get_all_people()
        for pearson in people_data:
            if pearson.id == id:
                pearson.name = name
                pearson.role = role
                return pearson
        return None

    def delete_person(self,id):

        people_data = self.get_all_people()
        for pearson in people_data:
            if pearson.id == id:
                people_data.remove(pearson)
                return people_data
        return None
    
    def get_person_by_role(self, role):
        people_data = self.get_all_people()
        filtered_people = [person for person in people_data if person.role == role]
        return filtered_people

