class Graph:
    def __init__(self):
        self.adjacency = {}  # vertex -> list of vertices it has an edge going to

    def addVertex(self, vertex):
        if vertex in self.adjacency:
            return False
        self.adjacency[vertex] = []
        return True

    def addEdge(self, from_vertex, to_vertex):
        if from_vertex not in self.adjacency or to_vertex not in self.adjacency:
            raise KeyError("Both vertices must be added before connecting them")
        if from_vertex == to_vertex or to_vertex in self.adjacency[from_vertex]:
            return False
        self.adjacency[from_vertex].append(to_vertex)
        return True

    def removeEdge(self, from_vertex, to_vertex):
        if to_vertex in self.adjacency.get(from_vertex, []):
            self.adjacency[from_vertex].remove(to_vertex)
            return True
        return False

    def listIncomingAdjacentVertex(self, vertex):
        return [v for v, targets in self.adjacency.items() if vertex in targets]

    def listOutgoingAdjacentVertex(self, vertex):
        return list(self.adjacency.get(vertex, []))

    def hasPath(self, start, goal):
        visited, stack = set(), [start]
        while stack:
            current = stack.pop()
            if current == goal:
                return True
            if current not in visited:
                visited.add(current)
                stack.extend(self.adjacency.get(current, []))
        return False

    def getVertices(self):
        return list(self.adjacency)


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
        self.courses = {}

    def add_course(self, course):
        if course.course_code in self.courses:
            raise ValueError(f"{course.course_code} already exists")
        if len(self.courses) >= self.MAX_COURSES:
            raise ValueError(f"Cannot have more than {self.MAX_COURSES} courses")
        self.courses[course.course_code] = course
        self.graph.addVertex(course)

    def add_prerequisite(self, course_code, prereq_code):
        course, prereq = self.courses[course_code], self.courses[prereq_code]
        if course == prereq:
            raise ValueError("A course cannot be its own prerequisite")
        if self.graph.hasPath(course, prereq):  # would create a loop
            raise ValueError(f"{prereq_code} already requires {course_code}, "
                             f"this would create a circular prerequisite")
        if not self.graph.addEdge(prereq, course):  # edge goes prereq -> course
            raise ValueError(f"{prereq_code} is already a prerequisite of {course_code}")

    def remove_prerequisite(self, course_code, prereq_code):
        return self.graph.removeEdge(self.courses[prereq_code], self.courses[course_code])

    def prerequisites_of(self, course_code):
        return self.graph.listIncomingAdjacentVertex(self.courses[course_code])

    def unlocked_by(self, course_code):
        return self.graph.listOutgoingAdjacentVertex(self.courses[course_code])

    def load_sample_data(self):
        for c in [
            Course("CS101", "Introduction to Programming", 4, "core", "Python basics, variables, loops and functions."),
            Course("MA101", "Discrete Mathematics", 3, "core", "Logic, sets, relations and graph theory."),
            Course("CS201", "Data Structures", 4, "core", "Lists, stacks, queues, trees and hash tables."),
            Course("CS202", "Computer Architecture", 3, "core", "CPU design, memory and instruction sets."),
            Course("CS301", "Algorithms", 4, "core", "Sorting, searching, graph algorithms and Big-O."),
            Course("CS302", "Database Systems", 3, "core", "Relational models, SQL and normalisation."),
            Course("CS310", "Artificial Intelligence", 3, "elective", "Search, knowledge representation and ML basics."),
            Course("CS401", "Software Engineering", 4, "core", "Requirements, design patterns and team projects."),
        ]:
            self.add_course(c)

        for course, prereq in [
            ("CS201", "CS101"), ("CS202", "CS101"),
            ("CS301", "CS201"), ("CS301", "CS101"), ("CS301", "MA101"),
            ("CS302", "CS201"),
            ("CS310", "CS301"),
            ("CS401", "CS301"), ("CS401", "CS302"),
        ]:
            self.add_prerequisite(course, prereq)


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
    for i, c in enumerate(system.courses.values(), start=1):
        print(f"{i}. {c.course_code} - {c.course_name}")


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
        if level in ("core", "elective"):
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

    menu = [
        ("View All Courses", view_all_courses),
        ("View Course Details", view_course_details),
        ("View Prerequisites of a Course", view_prerequisites),
        ("View Courses Unlocked by a Course", view_unlocked),
        ("Add a New Course", add_new_course),
        ("View Course Profile (electives show name only)", view_course_profile),
        ("Add a Prerequisite to a Course", add_prerequisite),
        ("Remove a Prerequisite from a Course", remove_prerequisite),
    ]
    exit_choice = str(len(menu) + 1)

    while True:
        print("\n==== University Course Prerequisite System ====")
        for i, (label, _) in enumerate(menu, start=1):
            print(f"{i}. {label}")
        print(f"{exit_choice}. Exit")
        choice = input("Enter choice: ").strip()

        if choice == exit_choice:
            print("Exiting program. Goodbye!")
            break
        if choice.isdigit() and 1 <= int(choice) <= len(menu):
            menu[int(choice) - 1][1](system)
        else:
            print(f"Invalid choice, please enter 1-{exit_choice}.")


if __name__ == "__main__":
    main()