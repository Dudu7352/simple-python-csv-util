# 1. ucznioweie
# 2. przedmioty
# 3. oceny

from abc import abstractmethod


class IFromRow:
    @abstractmethod
    def from_row(r):
        pass

class Grade:
    def __init__(self, id, student: 'Student', grade: int, date: str, subject: 'Subject'):
        self.id = id
        self.student = student
        self.grade = grade
        self.date = date
        self.subject = subject

class Person:
    def __init__(self, id, name, surname):
        self.id = id
        self.name = name
        self.surname = surname

class Address:
    def __init__(self, street, house_number):
        self.street = street
        self.house_number = house_number

class Subject:
    def __init__(self, s_name, teacher: 'Person'):
        self.s_name = s_name
        self.teacher = teacher

class Student(Person, IFromRow):
    def __init__(self, id, name, surname, address: 'Address'):
        super().__init__(self, id, name, surname)
        self.address = address
        self.__grades: list['Grade'] = []

    def add_grade(self, g: 'Grade'):
        self.__grades.append(g)

    def avg_grades(self):
        return sum(self.__grades) / len(self.__grades)

    def from_row(r):
        return Student(
            id = int(r['IDucznia']),
            name = r['imie'],
            surname= r['nazwisko'],
            address= Address(
                street = r['ulica'],
                house_number= int(r['dom'])
            ))

class SchoolClass:
    def __init__(self, id, students: list['Student']):
        self.id = id
        self.students: list['Student']

    def add(self, student: 'Student'):
        self.students.append(student)

classes: dict[SchoolClass] = dict()

with open('uczniowie.txt') as f:
    cols = f.readline().strip().split(';')
    for row_str in f:
        student = Student.from_row({i: j for i, j in zip(cols, row_str.strip(';'))})