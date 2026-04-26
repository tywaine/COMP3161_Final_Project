DROP DATABASE IF EXISTS course_management;
CREATE DATABASE course_management;
USE course_management;

-- =========================
-- User and role tables
-- =========================

CREATE TABLE Users (
    userId INT PRIMARY KEY,
    fullName VARCHAR(150) NOT NULL,
    passwordHash VARCHAR(255) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    role ENUM('student', 'lecturer', 'admin') NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (userId BETWEEN 100000000 AND 999999999)
);

CREATE TABLE Students (
    userId INT PRIMARY KEY,
    gpa DECIMAL(4,2) DEFAULT 0.00,
    FOREIGN KEY (userId) REFERENCES Users(userId)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Lecturers (
    userId INT PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    FOREIGN KEY (userId) REFERENCES Users(userId)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Admins (
    userId INT PRIMARY KEY,
    FOREIGN KEY (userId) REFERENCES Users(userId)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- =========================
-- Course tables
-- =========================

CREATE TABLE Courses (
    courseId INT AUTO_INCREMENT PRIMARY KEY,
    courseCode VARCHAR(8) NOT NULL UNIQUE,
    courseName VARCHAR(100) NOT NULL,
    description TEXT,
    createdByAdminId INT NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (createdByAdminId) REFERENCES Admins(userId)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Enrollment (
    studentId INT NOT NULL,
    courseId INT NOT NULL,
    finalGrade DECIMAL(5,2) DEFAULT NULL,
    PRIMARY KEY (studentId, courseId),
    FOREIGN KEY (studentId) REFERENCES Students(userId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (courseId) REFERENCES Courses(courseId)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Teaching (
    lecturerId INT NOT NULL,
    courseId INT NOT NULL,
    PRIMARY KEY (lecturerId, courseId),
    UNIQUE (courseId),
    FOREIGN KEY (lecturerId) REFERENCES Lecturers(userId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (courseId) REFERENCES Courses(courseId)
        ON DELETE CASCADE ON UPDATE CASCADE
);
-- =========================
-- Retrieve Members of a course
-- =========================
-- Get Lecturer
-- SELECT u.userId, u.fullName, 'Lecturer' AS role
-- FROM Users u
-- JOIN Teaching t ON u.userId = t.lecturerId
-- WHERE t.courseId = ?
--
-- UNION ALL
--
-- Get Students
-- SELECT u.userId, u.fullName, 'Student' AS role
-- FROM Users u
-- JOIN Enrollment e ON u.userId = e.studentId
-- WHERE e.courseId = ?;

-- =========================
-- Calendar and forums
-- =========================

CREATE TABLE CalendarEvents (
    eventId INT AUTO_INCREMENT PRIMARY KEY,
    courseId INT NOT NULL,
    createdByUserId INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    eventDateTime DATETIME NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (courseId) REFERENCES Courses(courseId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (createdByUserId) REFERENCES Users(userId)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Forums (
    forumId INT AUTO_INCREMENT PRIMARY KEY,
    courseId INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    createdByUserId INT NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (courseId) REFERENCES Courses(courseId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (createdByUserId) REFERENCES Users(userId)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE DiscussionThreads (
    threadId INT AUTO_INCREMENT PRIMARY KEY,
    forumId INT NOT NULL,
    createdByUserId INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (forumId) REFERENCES Forums(forumId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (createdByUserId) REFERENCES Users(userId)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Posts (
    postId INT AUTO_INCREMENT PRIMARY KEY,
    threadId INT NOT NULL,
    userId INT NOT NULL,
    parentPostId INT DEFAULT NULL,
    content TEXT NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (threadId) REFERENCES DiscussionThreads(threadId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (userId) REFERENCES Users(userId)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (parentPostId) REFERENCES Posts(postId)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- =========================
-- Course content
-- =========================

CREATE TABLE Sections (
    sectionId INT AUTO_INCREMENT PRIMARY KEY,
    courseId INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    position INT NOT NULL,
    FOREIGN KEY (courseId) REFERENCES Courses(courseId)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE SectionItems (
    sectionItemId INT AUTO_INCREMENT PRIMARY KEY,
    sectionId INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    contentType ENUM('link', 'file', 'slide', 'note') NOT NULL,
    contentUrl VARCHAR(500) DEFAULT NULL,
    filePath VARCHAR(500) DEFAULT NULL,
    description TEXT,
    uploadedByUserId INT NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sectionId) REFERENCES Sections(sectionId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (uploadedByUserId) REFERENCES Users(userId)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- =========================
-- Assignments and submissions
-- =========================

CREATE TABLE Assignments (
    assignmentId INT AUTO_INCREMENT PRIMARY KEY,
    courseId INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    dueDate DATETIME NOT NULL,
    totalMarks DECIMAL(6,2) NOT NULL DEFAULT 100.00,
    createdByUserId INT NOT NULL,
    FOREIGN KEY (courseId) REFERENCES Courses(courseId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (createdByUserId) REFERENCES Users(userId)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Submissions (
    submissionId INT AUTO_INCREMENT PRIMARY KEY,
    assignmentId INT NOT NULL,
    studentId INT NOT NULL,
    submittedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    filePath VARCHAR(500) DEFAULT NULL,
    textContent TEXT,
    grade DECIMAL(5,2) DEFAULT NULL,
    feedback TEXT,
    UNIQUE (assignmentId, studentId),
    FOREIGN KEY (assignmentId) REFERENCES Assignments(assignmentId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (studentId) REFERENCES Students(userId)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- =========================
-- Helpful indexes
-- =========================

CREATE INDEX idx_users_role ON Users(role);
CREATE INDEX idx_calendarevents_courseId ON CalendarEvents(courseId);
CREATE INDEX idx_calendarevents_eventDateTime ON CalendarEvents(eventDateTime);
CREATE INDEX idx_forums_courseId ON Forums(courseId);
CREATE INDEX idx_threads_forumId ON DiscussionThreads(forumId);
CREATE INDEX idx_posts_threadId ON Posts(threadId);
CREATE INDEX idx_posts_parentPostId ON Posts(parentPostId);
CREATE INDEX idx_sections_courseId ON Sections(courseId);
CREATE INDEX idx_sectionitems_sectionId ON SectionItems(sectionId);
CREATE INDEX idx_assignments_courseId ON Assignments(courseId);
CREATE INDEX idx_submissions_studentId ON Submissions(studentId);

