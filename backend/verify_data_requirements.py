import mysql.connector
from backend.app.config import Config

db = mysql.connector.connect(
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME
)

cursor = db.cursor(dictionary=True)

checks = [
    (
        "a. At least 100,000 students",
        "SELECT COUNT(*) AS value FROM Students",
        lambda x: x >= 100000,
        ">= 100000"
    ),
    (
        "b. At least 200 courses",
        "SELECT COUNT(*) AS value FROM Courses",
        lambda x: x >= 200,
        ">= 200"
    ),
    (
        "c. No student can do more than 6 courses",
        """
        SELECT MAX(courseCount) AS value
        FROM (
            SELECT COUNT(*) AS courseCount
            FROM Enrollment
            GROUP BY studentId
        ) x
        """,
        lambda x: x <= 6,
        "<= 6"
    ),
    (
        "d. Each student is enrolled in at least 3 courses",
        """
        SELECT MIN(courseCount) AS value
        FROM (
            SELECT COUNT(e.courseCode) AS courseCount
            FROM Students s
            LEFT JOIN Enrollment e ON s.userId = e.studentId
            GROUP BY s.userId
        ) x
        """,
        lambda x: x >= 3,
        ">= 3"
    ),
    (
        "e. Each course has at least 10 members",
        """
        SELECT MIN(memberCount) AS value
        FROM (
            SELECT COUNT(DISTINCT e.studentId) + COUNT(DISTINCT t.lecturerId) AS memberCount
            FROM Courses c
            LEFT JOIN Enrollment e ON c.courseCode = e.courseCode
            LEFT JOIN Teaching t ON c.courseCode = t.courseCode
            GROUP BY c.courseCode
        ) x
        """,
        lambda x: x >= 10,
        ">= 10"
    ),
    (
        "f. No lecturer teaches more than 5 courses",
        """
        SELECT MAX(courseCount) AS value
        FROM (
            SELECT COUNT(*) AS courseCount
            FROM Teaching
            GROUP BY lecturerId
        ) x
        """,
        lambda x: x <= 5,
        "<= 5"
    ),
    (
        "g. Each lecturer teaches at least 1 course",
        """
        SELECT MIN(courseCount) AS value
        FROM (
            SELECT COUNT(t.courseCode) AS courseCount
            FROM Lecturers l
            LEFT JOIN Teaching t ON l.userId = t.lecturerId
            GROUP BY l.userId
        ) x
        """,
        lambda x: x >= 1,
        ">= 1"
    )
]

print("\nDATA REQUIREMENTS CHECK")
print("-" * 60)

passed_all = True

for label, sql, condition, expected in checks:
    cursor.execute(sql)
    value = cursor.fetchone()["value"]

    passed = condition(value)
    status = "PASS" if passed else "FAIL"

    if not passed:
        passed_all = False

    print(f"{status} | {label}")
    print(f"Actual: {value} | Expected: {expected}")
    print("-" * 60)

print("ALL DATA REQUIREMENTS FULFILLED" if passed_all else "SOME DATA REQUIREMENTS FAILED")

cursor.close()
db.close()