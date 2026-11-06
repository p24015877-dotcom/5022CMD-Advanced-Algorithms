class Graph:
    def __init__(self):
        self.adj_list = dict()   # vertex -> list of vertices it has an edge to

    def addVertex(self, vertex):
        if vertex not in self.adj_list:
            self.adj_list[vertex] = []

    def addEdge(self, from_vertex, to_vertex):
        if from_vertex in self.adj_list and to_vertex in self.adj_list:
            self.adj_list[from_vertex].append(to_vertex)
        else:
            raise ValueError("One or both vertices are not found in the graph")

    def removeEdge(self, from_vertex, to_vertex):
        if from_vertex in self.adj_list:
            if to_vertex in self.adj_list[from_vertex]:
                self.adj_list[from_vertex].remove(to_vertex)
            else:
                raise ValueError("Edge does not exist")

    def hasVertex(self, vertex):
        return vertex in self.adj_list

    def hasEdge(self, from_vertex, to_vertex):
        if from_vertex in self.adj_list:
            return to_vertex in self.adj_list[from_vertex]
        return False

    def getNeighbours(self, vertex):
        return self.adj_list.get(vertex, [])

    def listIncomingAdjacentVertex(self, vertex):
        incoming = []
        for from_vertex, neighbours in self.adj_list.items():
            if vertex in neighbours:
                incoming.append(from_vertex)
        return incoming

    def getVertices(self):
        return list(self.adj_list.keys())


class Course:
    def __init__(self, course_code, course_name, credit_hours, level, description):
        self.course_code = course_code.upper()
        self.course_name = course_name
        self.credit_hours = int(credit_hours)
        self.level = level.lower()
        self.description = description

    def full_details(self):
        return (f"Course Code : {self.course_code}\n"
                f"Course Name : {self.course_name}\n"
                f"Credit Hours: {self.credit_hours}\n"
                f"Level       : {self.level.capitalize()}\n"
                f"Description : {self.description}")

    def profile(self):
        if self.level == "elective":
            return f"Course Name : {self.course_name}\n(Elective course - other details are hidden)"
        return self.full_details()

    def __str__(self):
        return f"{self.course_code} ({self.course_name})"


class CourseSystem:
    MAX_COURSES = 10

    def __init__(self):
        self.graph = Graph()
        self.courses = dict()    # course code -> Course object

    def add_course(self, course):
        if course.course_code in self.courses:
            raise ValueError(f"{course.course_code} already exists")
        if len(self.courses) >= self.MAX_COURSES:
            raise ValueError(f"Cannot have more than {self.MAX_COURSES} courses")
        self.courses[course.course_code] = course
        self.graph.addVertex(course)

    def add_prerequisite(self, course_code, prereq_code):
        course = self.courses[course_code]
        prereq = self.courses[prereq_code]
        if course == prereq:
            raise ValueError("A course cannot be its own prerequisite")
        if self.graph.hasEdge(prereq, course):
            raise ValueError(f"{prereq_code} is already a prerequisite of {course_code}")
        if self.graph.hasEdge(course, prereq):
            raise ValueError(f"{course_code} is already a prerequisite of {prereq_code}")
        self.graph.addEdge(prereq, course)   # edge goes prerequisite -> course

    def remove_prerequisite(self, course_code, prereq_code):
        course = self.courses[course_code]
        prereq = self.courses[prereq_code]
        if not self.graph.hasEdge(prereq, course):
            return False
        self.graph.removeEdge(prereq, course)
        return True

    def prerequisites_of(self, course_code):
        return self.graph.listIncomingAdjacentVertex(self.courses[course_code])

    def unlocked_by(self, course_code):
        return self.graph.getNeighbours(self.courses[course_code])

    def load_sample_data(self):
        self.add_course(Course("CS101", "Introduction to Programming", 4, "core", "Python basics, variables, loops and functions."))
        self.add_course(Course("MA101", "Discrete Mathematics", 3, "core", "Logic, sets, relations and graph theory."))
        self.add_course(Course("CS201", "Data Structures", 4, "core", "Lists, stacks, queues, trees and hash tables."))
        self.add_course(Course("CS202", "Computer Architecture", 3, "core", "CPU design, memory and instruction sets."))
        self.add_course(Course("CS301", "Algorithms", 4, "core", "Sorting, searching, graph algorithms and Big-O."))
        self.add_course(Course("CS302", "Database Systems", 3, "core", "Relational models, SQL and normalisation."))
        self.add_course(Course("CS310", "Artificial Intelligence", 3, "elective", "Search, knowledge representation and ML basics."))
        self.add_course(Course("CS401", "Software Engineering", 4, "core", "Requirements, design patterns and team projects."))

        self.add_prerequisite("CS201", "CS101")
        self.add_prerequisite("CS202", "CS101")
        self.add_prerequisite("CS301", "CS101")
        self.add_prerequisite("CS301", "MA101")
        self.add_prerequisite("CS301", "CS201")
        self.add_prerequisite("CS302", "CS201")
        self.add_prerequisite("CS310", "CS301")
        self.add_prerequisite("CS401", "CS301")
        self.add_prerequisite("CS401", "CS302")


def read_course_code(system, prompt="Enter Course Code: "):
    code = input(prompt).strip().upper()
    if code not in system.courses:
        print(f"Course '{code}' not found.")
        return None
    return code


def read_text(prompt):
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("  This field cannot be empty.")


def print_course_list(title, courses):
    print(title)
    if not courses:
        print("- None")
    for c in courses:
        print(f"- {c}")


def view_all_courses(system):
    print("\nAvailable Courses:")
    number = 1
    for course in system.courses.values():
        print(f"{number}. {course.course_code} - {course.course_name}")
        number += 1


def view_course_details(system):
    code = read_course_code(system)
    if code:
        print()
        print(system.courses[code].full_details())


def view_prerequisites(system):
    code = read_course_code(system)
    if code:
        c = system.courses[code]
        print_course_list(f"Prerequisites for {c.course_code} - {c.course_name}:",
                          system.prerequisites_of(code))


def view_unlocked(system):
    code = read_course_code(system)
    if code:
        c = system.courses[code]
        print_course_list(f"Courses unlocked by {c.course_code} - {c.course_name}:",
                          system.unlocked_by(code))


def add_new_course(system):
    if len(system.courses) >= system.MAX_COURSES:
        print(f"Course limit reached ({system.MAX_COURSES}).")
        return
    code = read_text("Enter new Course Code: ").upper()
    if code in system.courses:
        print(f"{code} already exists.")
        return
    name = read_text("Enter Course Name: ")
    while True:
        try:
            credits = int(input("Enter Credit Hours: "))
            if credits > 0:
                break
        except ValueError:
            pass
        print("  Please enter a positive whole number.")
    while True:
        level = input("Enter Level (core/elective): ").strip().lower()
        if level == "core" or level == "elective":
            break
        print("  Please enter core or elective.")
    description = read_text("Enter Description: ")
    system.add_course(Course(code, name, credits, level, description))
    print(f"Course {code} - {name} added.")


def view_course_profile(system):
    code = read_course_code(system)
    if code:
        print()
        print(system.courses[code].profile())


def add_prerequisite(system):
    code = read_course_code(system, "Enter Course Code (course X): ")
    if not code:
        return
    prereq = read_course_code(system, "Enter Prerequisite Course Code (course Y): ")
    if not prereq:
        return
    try:
        system.add_prerequisite(code, prereq)
        print(f"{prereq} is now a prerequisite of {code}.")
    except ValueError as e:
        print(f"Cannot add: {e}.")


def remove_prerequisite(system):
    code = read_course_code(system, "Enter Course Code (course X): ")
    if not code:
        return
    prereq = read_course_code(system, "Enter Prerequisite to remove (course Y): ")
    if not prereq:
        return
    if system.remove_prerequisite(code, prereq):
        print(f"{prereq} is no longer a prerequisite of {code}.")
    else:
        print(f"{prereq} is not a prerequisite of {code}.")


def main():
    system = CourseSystem()
    system.load_sample_data()

    while True:
        print("\n==== University Course Prerequisite System ====")
        print("1. View All Courses")
        print("2. View Course Details")
        print("3. View Prerequisites of a Course")
        print("4. View Courses Unlocked by a Course")
        print("5. Add a New Course")
        print("6. View Course Profile (electives show name only)")
        print("7. Add a Prerequisite to a Course")
        print("8. Remove a Prerequisite from a Course")
        print("9. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            view_all_courses(system)
        elif choice == "2":
            view_course_details(system)
        elif choice == "3":
            view_prerequisites(system)
        elif choice == "4":
            view_unlocked(system)
        elif choice == "5":
            add_new_course(system)
        elif choice == "6":
            view_course_profile(system)
        elif choice == "7":
            add_prerequisite(system)
        elif choice == "8":
            remove_prerequisite(system)
        elif choice == "9":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice, please enter 1-9.")


if __name__ == "__main__":
    main()