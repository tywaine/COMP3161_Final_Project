USE course_management;

CREATE OR REPLACE VIEW CoursesWith50OrMoreStudents AS
SELECT
    c.courseCode,
    c.courseName,
    c.description,
    COUNT(e.studentId) AS studentCount
FROM Courses c
JOIN Enrollment e
    ON c.courseCode = e.courseCode
GROUP BY
    c.courseCode,
    c.courseName,
    c.description
HAVING COUNT(e.studentId) >= 50;


CREATE OR REPLACE VIEW StudentsWith5OrMoreCourses AS
SELECT
    s.userId AS studentId,
    u.fullName,
    u.email,
    COUNT(e.courseCode) AS courseCount
FROM Students s
JOIN Users u
    ON s.userId = u.userId
JOIN Enrollment e
    ON s.userId = e.studentId
GROUP BY
    s.userId,
    u.fullName,
    u.email
HAVING COUNT(e.courseCode) >= 5;


CREATE OR REPLACE VIEW LecturersWith3OrMoreCourses AS
SELECT
    l.userId AS lecturerId,
    u.fullName,
    u.email,
    COUNT(t.courseCode) AS courseCount
FROM Lecturers l
JOIN Users u
    ON l.userId = u.userId
JOIN Teaching t
    ON l.userId = t.lecturerId
GROUP BY
    l.userId,
    u.fullName,
    u.email
HAVING COUNT(t.courseCode) >= 3;


CREATE OR REPLACE VIEW Top10MostEnrolledCourses AS
SELECT
    c.courseCode,
    c.courseName,
    c.description,
    COUNT(e.studentId) AS studentCount
FROM Courses c
JOIN Enrollment e
    ON c.courseCode = e.courseCode
GROUP BY
    c.courseCode,
    c.courseName,
    c.description
ORDER BY studentCount DESC, c.courseName
LIMIT 10;


CREATE OR REPLACE VIEW Top10StudentsHighestOverallAverages AS
SELECT
    s.userId AS studentId,
    u.fullName,
    u.email,
    ROUND(AVG(e.finalGrade), 2) AS overallAverage
FROM Students s
JOIN Users u
    ON s.userId = u.userId
JOIN Enrollment e
    ON s.userId = e.studentId
WHERE e.finalGrade IS NOT NULL
GROUP BY
    s.userId,
    u.fullName,
    u.email
ORDER BY overallAverage DESC, u.fullName
LIMIT 10;