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

COURSE_WORDS = {
    "COMP": ["Programming", "Software", "Algorithms", "Databases", "Networks", "AI", "Systems"],
    "BIOL": ["Genetics", "Ecology", "Microbiology", "Anatomy", "Botany", "Zoology"],
    "PHYS": ["Mechanics", "Optics", "Quantum", "Thermodynamics", "Electricity", "Astrophysics"],
    "ECON": ["Microeconomics", "Macroeconomics", "Finance", "Markets", "Trade", "Development"],
    "HIST": ["Ancient History", "Modern History", "Caribbean History", "World History", "Empire", "Revolution"],
    "MATH": ["Calculus", "Algebra", "Statistics", "Geometry", "Probability", "Discrete Math"],
    "CHEM": ["Organic Chemistry", "Inorganic Chemistry", "Biochemistry", "Analytical Chemistry", "Physical Chemistry"],
    "ENGL": ["Literature", "Writing", "Poetry", "Drama", "Linguistics", "Composition"],
    "SOCI": ["Sociology", "Culture", "Identity", "Society", "Institutions", "Social Theory"],
    "GEOG": ["Geography", "Climate", "Mapping", "Urban Studies", "Environment", "Regions"]
}


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
        full_name = fake.name()
        email = f"admin{i + 1}@school.edu"
        admins.append({
            "userId": user_id,
            "fullName": full_name,
            "email": email,
            "role": "admin"
        })
    return admins


def generate_lecturers():
    lecturers = []
    for i in range(NUM_LECTURERS):
        user_id = LECTURER_START_ID + i
        full_name = fake.name()
        email = f"lecturer{i + 1}@school.edu"
        department = random.choice(DEPARTMENTS)
        lecturers.append({
            "userId": user_id,
            "fullName": full_name,
            "email": email,
            "role": "lecturer",
            "department": department
        })
    return lecturers


def generate_students():
    students = []
    for i in range(NUM_STUDENTS):
        user_id = STUDENT_START_ID + i
        full_name = fake.name()
        email = f"student{i + 1}@school.edu"
        gpa = round(random.uniform(0.0, 4.0), 2)
        students.append({
            "userId": user_id,
            "fullName": full_name,
            "email": email,
            "role": "student",
            "gpa": gpa
        })
    return students


def make_course_code(existing_codes):
    """
    Format:
    4 letters + 4 digits
    first digit indicates year level: 1, 2, or 3
    examples:
    COMP1210, BIOL1000, PHYS2190, ECON3100
    """
    while True:
        prefix = random.choice(COURSE_PREFIXES)
        first_digit = str(random.randint(1, 3))
        last_three = f"{random.randint(0, 999):03d}"
        code = f"{prefix}{first_digit}{last_three}"
        if code not in existing_codes:
            existing_codes.add(code)
            return code


def generate_course_title(prefix, used_titles):
    subject_word = random.choice(COURSE_WORDS.get(prefix, ["Studies"]))

    suffix_options = [
        fake.word().capitalize(),
        fake.catch_phrase(),
        fake.bs().title(),
        f"{fake.word().capitalize()} Systems",
        f"{fake.word().capitalize()} Applications",
        f"{fake.word().capitalize()} Methods",
        f"{fake.word().capitalize()} Principles",
        f"{fake.word().capitalize()} Concepts"
    ]

    while True:
        suffix = random.choice(suffix_options)
        title = f"{subject_word} {suffix}".strip()

        if title not in used_titles:
            used_titles.add(title)
            return title


def generate_courses(admin_ids):
    existing_codes = set()
    used_titles = set()
    courses = []

    for _ in range(NUM_COURSES):
        code = make_course_code(existing_codes)
        prefix = code[:4]
        title = generate_course_title(prefix, used_titles)
        description = f"{title} for {code}"
        created_by_admin_id = random.choice(admin_ids)

        courses.append({
            "courseCode": code,
            "courseName": title,
            "description": description,
            "createdByAdminId": created_by_admin_id
        })

    return courses


def assign_teaching(courses, lecturer_ids):
    """
    Constraints:
    - each lecturer teaches at least 1 course
    - no lecturer teaches more than 5 courses
    - each course has exactly 1 lecturer
    """
    num_courses = len(courses)
    lecturer_course_counts = {lecturer_id: 0 for lecturer_id in lecturer_ids}
    teaching = []

    course_indexes = list(range(num_courses))
    random.shuffle(course_indexes)

    for lecturer_id in lecturer_ids:
        if not course_indexes:
            break
        course_index = course_indexes.pop()
        teaching.append((lecturer_id, course_index))
        lecturer_course_counts[lecturer_id] += 1

    for course_index in course_indexes:
        available = [lid for lid in lecturer_ids if lecturer_course_counts[lid] < 5]
        lecturer_id = random.choice(available)
        teaching.append((lecturer_id, course_index))
        lecturer_course_counts[lecturer_id] += 1

    teaching.sort(key=lambda x: x[1])
    return teaching


def assign_enrollments(student_ids, course_ids):
    """
    Constraints:
    - each student has 3 to 6 courses
    - each course has at least 10 students
    """
    enrollments = set()
    student_course_sets = {sid: set() for sid in student_ids}

    shuffled_students = student_ids[:]
    random.shuffle(shuffled_students)
    pointer = 0

    for course_id in course_ids:
        assigned = 0
        while assigned < 10:
            student_id = shuffled_students[pointer % len(shuffled_students)]
            pointer += 1

            if len(student_course_sets[student_id]) < 6 and course_id not in student_course_sets[student_id]:
                student_course_sets[student_id].add(course_id)
                enrollments.add((student_id, course_id))
                assigned += 1

    for student_id in student_ids:
        target_count = random.randint(3, 6)

        while len(student_course_sets[student_id]) < target_count:
            course_id = random.choice(course_ids)
            if course_id not in student_course_sets[student_id]:
                student_course_sets[student_id].add(course_id)
                enrollments.add((student_id, course_id))

    return sorted(enrollments, key=lambda x: (x[0], x[1]))


def main():
    admins = generate_admins()
    lecturers = generate_lecturers()
    students = generate_students()

    admin_ids = [a["userId"] for a in admins]
    lecturer_ids = [l["userId"] for l in lecturers]
    student_ids = [s["userId"] for s in students]

    courses = generate_courses(admin_ids)

    temp_course_ids = list(range(1, NUM_COURSES + 1))

    teaching_pairs = assign_teaching(courses, lecturer_ids)
    enrollments = assign_enrollments(student_ids, temp_course_ids)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("USE course_management;\n\n")

        admin_user_rows = [
            f"({a['userId']}, '{esc(a['fullName'])}', '{esc(PASSWORD_HASH)}', '{a['email']}', '{a['role']}', NOW())"
            for a in admins
        ]
        write_insert_batches(
            f,
            "Users",
            "userId, fullName, passwordHash, email, role, createdAt",
            admin_user_rows
        )

        admin_rows = [f"({a['userId']})" for a in admins]
        write_insert_batches(f, "Admins", "userId", admin_rows)

        lecturer_user_rows = [
            f"({l['userId']}, '{esc(l['fullName'])}', '{esc(PASSWORD_HASH)}', '{l['email']}', '{l['role']}', NOW())"
            for l in lecturers
        ]
        write_insert_batches(
            f,
            "Users",
            "userId, fullName, passwordHash, email, role, createdAt",
            lecturer_user_rows
        )

        lecturer_rows = [
            f"({l['userId']}, '{esc(l['department'])}')"
            for l in lecturers
        ]
        write_insert_batches(f, "Lecturers", "userId, department", lecturer_rows)

        student_user_rows = [
            f"({s['userId']}, '{esc(s['fullName'])}', '{esc(PASSWORD_HASH)}', '{s['email']}', '{s['role']}', NOW())"
            for s in students
        ]
        write_insert_batches(
            f,
            "Users",
            "userId, fullName, passwordHash, email, role, createdAt",
            student_user_rows,
            batch_size=2000
        )

        student_rows = [
            f"({s['userId']}, {s['gpa']})"
            for s in students
        ]
        write_insert_batches(
            f,
            "Students",
            "userId, gpa",
            student_rows,
            batch_size=2000
        )

        course_rows = [
            f"('{c['courseCode']}', '{esc(c['courseName'])}', '{esc(c['description'])}', {c['createdByAdminId']}, NOW())"
            for c in courses
        ]
        write_insert_batches(
            f,
            "Courses",
            "courseCode, courseName, description, createdByAdminId, createdAt",
            course_rows
        )

        teaching_rows = [
            f"({lecturer_id}, {course_index + 1})"
            for lecturer_id, course_index in teaching_pairs
        ]
        write_insert_batches(
            f,
            "Teaching",
            "lecturerId, courseId",
            teaching_rows
        )

        enrollment_rows = [
            f"({student_id}, {course_id}, NULL)"
            for student_id, course_id in enrollments
        ]
        write_insert_batches(
            f,
            "Enrollment",
            "studentId, courseId, finalGrade",
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