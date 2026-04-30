import random
from faker import Faker
from werkzeug.security import generate_password_hash

fake = Faker()
random.seed(42)
Faker.seed(42)

OUTPUT_FILE = "../sql/insert_data.sql"

NUM_STUDENTS = 100_000
NUM_COURSES = 200
NUM_LECTURERS = 50
NUM_ADMINS = 5

ADMIN_START_ID = 100000001
LECTURER_START_ID = 200000001
STUDENT_START_ID = 300000001

DEFAULT_PASSWORD = "password123"
PASSWORD_HASH = generate_password_hash(DEFAULT_PASSWORD)

DEPARTMENTS = [
    "Computer Science", "Biology", "Physics", "Economics", "History",
    "Mathematics", "Chemistry", "English", "Sociology", "Geography"
]

COURSE_PREFIXES = [
    "COMP", "BIOL", "PHYS", "ECON", "HIST",
    "MATH", "CHEM", "ENGL", "SOCI", "GEOG"
]


def esc(value: str) -> str:
    return value.replace("'", "''")


def write_insert_batches(file_obj, table_name, columns, rows, batch_size=1000):
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        values_sql = ",\n".join(batch)
        file_obj.write(f"INSERT INTO {table_name} ({columns}) VALUES\n{values_sql};\n\n")


def generate_admins():
    admins = []

    for i in range(NUM_ADMINS):
        user_id = ADMIN_START_ID + i
        admins.append({
            "userId": user_id,
            "fullName": fake.name(),
            "email": f"admin{i + 1}@school.edu",
            "role": "admin"
        })

    return admins


def generate_lecturers():
    lecturers = []

    for i in range(NUM_LECTURERS):
        user_id = LECTURER_START_ID + i
        lecturers.append({
            "userId": user_id,
            "fullName": fake.name(),
            "email": f"lecturer{i + 1}@school.edu",
            "role": "lecturer",
            "department": random.choice(DEPARTMENTS)
        })

    return lecturers


def generate_students():
    students = []

    for i in range(NUM_STUDENTS):
        user_id = STUDENT_START_ID + i
        students.append({
            "userId": user_id,
            "fullName": fake.name(),
            "email": f"student{i + 1}@school.edu",
            "role": "student"
        })

    return students


SUBJECT_COURSES = {
    "COMP": {
        0: ["Introduction to Computing", "Digital Literacy", "Computational Thinking", "Computer Applications", "Foundations of Programming"],
        1: ["Programming Fundamentals", "Data Structures", "Discrete Mathematics for Computing", "Web Development I",
            "Computer Organization", "Introduction to Algorithms", "Object-Oriented Programming", "Database Fundamentals",
            "Systems Programming", "Software Engineering Principles"],
        2: ["Operating Systems", "Computer Networks", "Software Engineering", "Database Management Systems",
            "Theory of Computation", "Computer Architecture", "Web Development II", "Mobile Application Development",
            "Human-Computer Interaction", "Information Security"],
        3: ["Artificial Intelligence", "Machine Learning", "Compiler Design", "Distributed Systems",
            "Computer Graphics", "Cloud Computing", "Data Mining", "Cybersecurity",
            "Natural Language Processing", "Capstone Project in Computing"]
    },
    "BIOL": {
        0: ["Foundations of Biology", "Introduction to Life Sciences", "Basic Anatomy", "Nature and Environment", "Biology Lab Techniques"],
        1: ["Cell Biology", "Genetics", "General Ecology", "Zoology I", "Botany I",
            "Biochemistry I", "Microbiology", "Human Anatomy", "Evolutionary Biology", "Marine Biology"],
        2: ["Molecular Biology", "Immunology", "Plant Physiology", "Animal Behaviour", "Developmental Biology",
            "Biostatistics", "Environmental Biology", "Parasitology", "Histology", "Comparative Anatomy"],
        3: ["Genomics and Bioinformatics", "Advanced Genetics", "Neurobiology", "Conservation Biology",
            "Tropical Ecology", "Biotechnology", "Virology", "Medical Microbiology",
            "Research Methods in Biology", "Capstone Project in Biology"]
    },
    "PHYS": {
        0: ["Introductory Physics", "Physics for Everyday Life", "Basic Mechanics", "Foundations of Physical Science", "Physics Lab Safety"],
        1: ["Classical Mechanics", "Electricity and Magnetism", "Waves and Optics", "Thermal Physics",
            "Mathematical Methods for Physics", "Introduction to Astrophysics", "Physics Lab I",
            "Modern Physics", "Fluid Mechanics", "Physics Problem Solving"],
        2: ["Quantum Mechanics I", "Electrodynamics", "Thermodynamics and Statistical Mechanics", "Solid State Physics",
            "Nuclear Physics", "Computational Physics", "Atomic Physics", "Physics Lab II",
            "Analytical Mechanics", "Electronics for Scientists"],
        3: ["Quantum Mechanics II", "General Relativity", "Particle Physics", "Plasma Physics",
            "Advanced Astrophysics", "Condensed Matter Physics", "Photonics",
            "Medical Physics", "Research Methods in Physics", "Capstone Project in Physics"]
    },
    "ECON": {
        0: ["Introduction to Economics", "Economic Reasoning", "Foundations of Business", "Personal Finance", "Global Economy Basics"],
        1: ["Microeconomics I", "Macroeconomics I", "Mathematics for Economics", "Economic History",
            "Introduction to Econometrics", "Development Economics", "Money and Banking",
            "Labour Economics", "Political Economy", "Caribbean Economics"],
        2: ["Microeconomics II", "Macroeconomics II", "International Trade", "Public Finance",
            "Industrial Organization", "Econometrics", "Environmental Economics",
            "Financial Economics", "Health Economics", "Game Theory"],
        3: ["Advanced Econometrics", "Monetary Economics", "Economic Policy Analysis", "Behavioral Economics",
            "International Finance", "Economic Growth and Development", "Urban Economics",
            "Economics of Innovation", "Research Methods in Economics", "Capstone Project in Economics"]
    },
    "HIST": {
        0: ["World History Survey", "Introduction to Historical Methods", "Foundations of History", "Caribbean Heritage", "History of Ideas"],
        1: ["Ancient Civilizations", "Medieval History", "Caribbean History I", "European History to 1800",
            "African History", "Latin American History", "History of the Americas",
            "Social History", "Economic History", "Historical Research Methods"],
        2: ["Modern European History", "Caribbean History II", "History of Slavery", "Colonial History",
            "American History", "Asian History", "War and Society",
            "Women in History", "Oral History Methods", "Intellectual History"],
        3: ["Historiography", "Postcolonial Studies", "Comparative Caribbean History", "Nationalism and Identity",
            "Digital History", "Public History", "Environmental History",
            "History of Science and Technology", "Research Seminar in History", "Capstone Project in History"]
    },
    "MATH": {
        0: ["Pre-Calculus", "Foundations of Mathematics", "Basic Statistics", "Mathematical Reasoning", "College Algebra"],
        1: ["Calculus I", "Calculus II", "Linear Algebra", "Introduction to Probability",
            "Number Theory", "Geometry", "Mathematical Logic",
            "Calculus III", "Introduction to Proofs", "Applied Mathematics I"],
        2: ["Real Analysis I", "Abstract Algebra I", "Differential Equations", "Numerical Methods",
            "Complex Analysis", "Combinatorics", "Topology",
            "Mathematical Modelling", "Probability and Statistics II", "Applied Mathematics II"],
        3: ["Real Analysis II", "Abstract Algebra II", "Functional Analysis", "Partial Differential Equations",
            "Graph Theory", "Cryptography", "Optimization",
            "Stochastic Processes", "Research Methods in Mathematics", "Capstone Project in Mathematics"]
    },
    "CHEM": {
        0: ["Introduction to Chemistry", "Chemistry in Society", "Lab Safety and Techniques", "Foundations of Chemical Science", "Environmental Chemistry Basics"],
        1: ["General Chemistry I", "General Chemistry II", "Organic Chemistry I", "Analytical Chemistry",
            "Inorganic Chemistry I", "Chemistry Lab I", "Physical Chemistry I",
            "Chemical Bonding", "Stoichiometry", "Chemistry of Materials"],
        2: ["Organic Chemistry II", "Physical Chemistry II", "Inorganic Chemistry II", "Spectroscopy",
            "Polymer Chemistry", "Medicinal Chemistry", "Chemistry Lab II",
            "Chemical Thermodynamics", "Coordination Chemistry", "Industrial Chemistry"],
        3: ["Advanced Organic Chemistry", "Quantum Chemistry", "Electrochemistry", "Nanochemistry",
            "Pharmaceutical Chemistry", "Computational Chemistry", "Natural Products Chemistry",
            "Food Chemistry", "Research Methods in Chemistry", "Capstone Project in Chemistry"]
    },
    "ENGL": {
        0: ["Introduction to English Studies", "Academic Writing Basics", "English Grammar Review", "Foundations of Literature", "Critical Reading Skills"],
        1: ["Introduction to Literature", "English Composition", "Creative Writing I", "Linguistics I",
            "Caribbean Literature", "British Literature I", "American Literature I",
            "Introduction to Poetry", "Academic Writing", "Public Speaking"],
        2: ["Shakespeare Studies", "Postcolonial Literature", "Linguistics II", "Creative Writing II",
            "Literary Theory", "British Literature II", "American Literature II",
            "African Literature", "Gender and Literature", "Professional Communication"],
        3: ["Advanced Literary Theory", "Discourse Analysis", "Sociolinguistics", "Caribbean Literary Criticism",
            "Digital Humanities", "Comparative Literature", "Publishing and Editing",
            "Advanced Creative Writing", "Research Methods in English", "Capstone Project in English"]
    },
    "SOCI": {
        0: ["Introduction to Sociology", "Understanding Society", "Social Issues Today", "Foundations of Social Science", "Community and Culture"],
        1: ["Sociological Theory I", "Research Methods in Sociology", "Social Psychology", "Caribbean Society",
            "Sociology of the Family", "Urban Sociology", "Criminology",
            "Sociology of Education", "Population Studies", "Social Stratification"],
        2: ["Sociological Theory II", "Qualitative Research Methods", "Sociology of Health", "Deviance and Social Control",
            "Political Sociology", "Sociology of Religion", "Race and Ethnicity",
            "Gender Studies", "Sociology of Work", "Media and Society"],
        3: ["Advanced Sociological Theory", "Globalization and Society", "Environmental Sociology", "Sociology of Development",
            "Visual Sociology", "Social Movements", "Youth and Society",
            "Aging and Society", "Research Seminar in Sociology", "Capstone Project in Sociology"]
    },
    "GEOG": {
        0: ["Introduction to Geography", "Maps and Spatial Thinking", "Earth and Environment", "Foundations of Physical Geography", "Caribbean Landscapes"],
        1: ["Physical Geography", "Human Geography", "Cartography and GIS", "Climatology",
            "Geomorphology", "Biogeography", "Economic Geography",
            "Caribbean Geography", "Environmental Management", "Urban Geography"],
        2: ["Remote Sensing", "Advanced GIS", "Hydrology", "Soil Science",
            "Population Geography", "Political Geography", "Coastal Studies",
            "Natural Hazards", "Resource Management", "Transport Geography"],
        3: ["Advanced Remote Sensing", "Climate Change Science", "Geospatial Analysis", "Sustainable Development",
            "Advanced Coastal Management", "Environmental Impact Assessment", "Landscape Ecology",
            "Urban Planning", "Research Methods in Geography", "Capstone Project in Geography"]
    }
}


def make_course_code_and_name(existing_codes, used_titles):
    while True:
        prefix = random.choice(COURSE_PREFIXES)
        first_digit = random.randint(0, 3)

        available_names = [
            name for name in SUBJECT_COURSES[prefix][first_digit]
            if name not in used_titles
        ]

        if not available_names:
            continue

        name = random.choice(available_names)
        last_three = f"{random.randint(0, 999):03d}"
        code = f"{prefix}{first_digit}{last_three}"

        if code not in existing_codes:
            existing_codes.add(code)
            used_titles.add(name)
            return code, name


def generate_courses(admin_ids):
    existing_codes = set()
    used_titles = set()
    courses = []

    for _ in range(NUM_COURSES):
        code, name = make_course_code_and_name(existing_codes, used_titles)

        courses.append({
            "courseCode": code,
            "courseName": name,
            "description": f"{name} - {code}",
            "createdByAdminId": random.choice(admin_ids)
        })

    return courses


def assign_teaching(courses, lecturer_ids):
    """
    Constraints:
    - each lecturer teaches at least 1 course
    - no lecturer teaches more than 5 courses
    - each course has exactly 1 lecturer
    """
    lecturer_course_counts = {lecturer_id: 0 for lecturer_id in lecturer_ids}
    teaching = []

    course_indexes = list(range(len(courses)))
    random.shuffle(course_indexes)

    for lecturer_id in lecturer_ids:
        if not course_indexes:
            break

        course_index = course_indexes.pop()
        teaching.append((lecturer_id, course_index))
        lecturer_course_counts[lecturer_id] += 1

    for course_index in course_indexes:
        available_lecturers = [
            lecturer_id
            for lecturer_id in lecturer_ids
            if lecturer_course_counts[lecturer_id] < 5
        ]

        lecturer_id = random.choice(available_lecturers)
        teaching.append((lecturer_id, course_index))
        lecturer_course_counts[lecturer_id] += 1

    teaching.sort(key=lambda x: x[1])
    return teaching


def assign_enrollments(student_ids, course_codes):
    """
    Constraints:
    - each student has 3 to 6 courses
    - each course has at least 10 students
    """
    enrollments = set()
    student_course_sets = {student_id: set() for student_id in student_ids}

    shuffled_students = student_ids[:]
    random.shuffle(shuffled_students)
    pointer = 0

    for course_code in course_codes:
        assigned = 0

        while assigned < 10:
            student_id = shuffled_students[pointer % len(shuffled_students)]
            pointer += 1

            if (
                len(student_course_sets[student_id]) < 6
                and course_code not in student_course_sets[student_id]
            ):
                student_course_sets[student_id].add(course_code)
                enrollments.add((student_id, course_code))
                assigned += 1

    for student_id in student_ids:
        target_count = random.randint(3, 6)

        while len(student_course_sets[student_id]) < target_count:
            course_code = random.choice(course_codes)

            if course_code not in student_course_sets[student_id]:
                student_course_sets[student_id].add(course_code)
                enrollments.add((student_id, course_code))

    return sorted(enrollments, key=lambda x: (x[0], x[1]))


def main():
    admins = generate_admins()
    lecturers = generate_lecturers()
    students = generate_students()

    admin_ids = [admin["userId"] for admin in admins]
    lecturer_ids = [lecturer["userId"] for lecturer in lecturers]
    student_ids = [student["userId"] for student in students]

    courses = generate_courses(admin_ids)
    course_codes = [course["courseCode"] for course in courses]

    teaching_pairs = assign_teaching(courses, lecturer_ids)
    enrollments = assign_enrollments(student_ids, course_codes)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("USE course_management;\n\n")

        admin_user_rows = [
            f"({admin['userId']}, '{esc(admin['fullName'])}', '{esc(PASSWORD_HASH)}', '{admin['email']}', '{admin['role']}', NOW())"
            for admin in admins
        ]

        write_insert_batches(
            f,
            "Users",
            "userId, fullName, passwordHash, email, role, createdAt",
            admin_user_rows
        )

        admin_rows = [
            f"({admin['userId']})"
            for admin in admins
        ]

        write_insert_batches(
            f,
            "Admins",
            "userId",
            admin_rows
        )

        lecturer_user_rows = [
            f"({lecturer['userId']}, '{esc(lecturer['fullName'])}', '{esc(PASSWORD_HASH)}', '{lecturer['email']}', '{lecturer['role']}', NOW())"
            for lecturer in lecturers
        ]

        write_insert_batches(
            f,
            "Users",
            "userId, fullName, passwordHash, email, role, createdAt",
            lecturer_user_rows
        )

        lecturer_rows = [
            f"({lecturer['userId']}, '{esc(lecturer['department'])}')"
            for lecturer in lecturers
        ]

        write_insert_batches(
            f,
            "Lecturers",
            "userId, department",
            lecturer_rows
        )

        student_user_rows = [
            f"({student['userId']}, '{esc(student['fullName'])}', '{esc(PASSWORD_HASH)}', '{student['email']}', '{student['role']}', NOW())"
            for student in students
        ]

        write_insert_batches(
            f,
            "Users",
            "userId, fullName, passwordHash, email, role, createdAt",
            student_user_rows,
            batch_size=2000
        )

        student_rows = [
            f"({student['userId']})"
            for student in students
        ]

        write_insert_batches(
            f,
            "Students",
            "userId",
            student_rows,
            batch_size=2000
        )

        course_rows = [
            f"('{course['courseCode']}', '{esc(course['courseName'])}', '{esc(course['description'])}', {course['createdByAdminId']}, NOW())"
            for course in courses
        ]

        write_insert_batches(
            f,
            "Courses",
            "courseCode, courseName, description, createdByAdminId, createdAt",
            course_rows
        )

        teaching_rows = []

        for lecturer_id, course_index in teaching_pairs:
            course = courses[course_index]
            course_code = course["courseCode"]

            teaching_rows.append(
                f"({lecturer_id}, '{course_code}')"
            )

        write_insert_batches(
            f,
            "Teaching",
            "lecturerId, courseCode",
            teaching_rows
        )

        enrollment_rows = [
            f"({student_id}, '{course_code}', NULL)"
            for student_id, course_code in enrollments
        ]

        write_insert_batches(
            f,
            "Enrollment",
            "studentId, courseCode, finalGrade",
            enrollment_rows,
            batch_size=3000
        )

    print(f"Generated {OUTPUT_FILE}")
    print(f"Admins: {len(admins)}")
    print(f"Lecturers: {len(lecturers)}")
    print(f"Students: {len(students)}")
    print(f"Courses: {len(courses)}")
    print(f"Teaching rows: {len(teaching_pairs)}")
    print(f"Enrollment rows: {len(enrollments)}")
    print(f"Default password for seeded users: {DEFAULT_PASSWORD}")


if __name__ == "__main__":
    main()