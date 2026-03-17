USE course_management;

-- =========================================================
-- 1. All courses that have 50 or more students
-- =========================================================
CREATE OR REPLACE VIEW CoursesWith50OrMoreStudents AS
SELECT
    c.courseId,
    c.courseCode,
    c.courseName,
    c.semester,
    c.year,
    COUNT(e.studentId) AS studentCount
FROM Courses c
JOIN Enrollment e
    ON c.courseId = e.courseId
GROUP BY
    c.courseId,
    c.courseCode,
    c.courseName,
    c.semester,
    c.year
HAVING COUNT(e.studentId) >= 50;


-- =========================================================
-- 2. All students that do 5 or more courses
-- =========================================================
CREATE OR REPLACE VIEW StudentsWith5OrMoreCourses AS
SELECT
    s.userId AS studentId,
    u.fullName,
    u.email,
    COUNT(e.courseId) AS courseCount
FROM Students s
JOIN Users u
    ON s.userId = u.userId
JOIN Enrollment e
    ON s.userId = e.studentId
GROUP BY
    s.userId,
    u.fullName,
    u.email
HAVING COUNT(e.courseId) >= 5;


-- =========================================================
-- 3. All lecturers that teach 3 or more courses
-- =========================================================
CREATE OR REPLACE VIEW LecturersWith3OrMoreCourses AS
SELECT
    l.userId AS lecturerId,
    u.fullName,
    u.email,
    COUNT(t.courseId) AS courseCount
FROM Lecturers l
JOIN Users u
    ON l.userId = u.userId
JOIN Teaching t
    ON l.userId = t.lecturerId
GROUP BY
    l.userId,
    u.fullName,
    u.email
HAVING COUNT(t.courseId) >= 3;


-- =========================================================
-- 4. The 10 most enrolled courses
-- =========================================================
CREATE OR REPLACE VIEW Top10MostEnrolledCourses AS
SELECT
    c.courseId,
    c.courseCode,
    c.courseName,
    c.semester,
    c.year,
    COUNT(e.studentId) AS studentCount
FROM Courses c
JOIN Enrollment e
    ON c.courseId = e.courseId
GROUP BY
    c.courseId,
    c.courseCode,
    c.courseName,
    c.semester,
    c.year
ORDER BY studentCount DESC, c.courseName ASC
LIMIT 10;


-- =========================================================
-- 5. The top 10 students with the highest overall averages
-- =========================================================
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
ORDER BY overallAverage DESC, u.fullName ASC
LIMIT 10;