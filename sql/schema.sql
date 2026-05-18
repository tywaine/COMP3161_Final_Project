DROP DATABASE IF EXISTS course_management;
CREATE DATABASE course_management;
USE course_management;

-- User and role tables
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

-- Course tables
CREATE TABLE Courses (
    courseCode VARCHAR(8) PRIMARY KEY,
    courseName VARCHAR(100) NOT NULL,
    description TEXT,
    createdByAdminId INT NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (createdByAdminId) REFERENCES Admins(userId)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Enrollment (
    studentId INT NOT NULL,
    courseCode VARCHAR(8) NOT NULL,
    finalGrade DECIMAL(5,2) DEFAULT NULL,
    PRIMARY KEY (studentId, courseCode),
    FOREIGN KEY (studentId) REFERENCES Students(userId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (courseCode) REFERENCES Courses(courseCode)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Teaching (
    lecturerId INT NOT NULL,
    courseCode VARCHAR(8) NOT NULL,
    PRIMARY KEY (lecturerId, courseCode),
    UNIQUE (courseCode),
    FOREIGN KEY (lecturerId) REFERENCES Lecturers(userId)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (courseCode) REFERENCES Courses(courseCode)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Calendar and forums
CREATE TABLE CalendarEvents (
    eventId INT AUTO_INCREMENT PRIMARY KEY,
    courseCode VARCHAR(8) NOT NULL,
    createdByUserId INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    eventDateTime DATETIME NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (courseCode) REFERENCES Courses(courseCode)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (createdByUserId) REFERENCES Users(userId)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Forums (
    forumId INT AUTO_INCREMENT PRIMARY KEY,
    courseCode VARCHAR(8) NOT NULL,
    title VARCHAR(150) NOT NULL,
    createdByUserId INT NOT NULL,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (courseCode) REFERENCES Courses(courseCode)
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


-- Course content
CREATE TABLE Sections (
    sectionId INT AUTO_INCREMENT PRIMARY KEY,
    courseCode VARCHAR(8) NOT NULL,
    title VARCHAR(150) NOT NULL,
    position INT NOT NULL,
    FOREIGN KEY (courseCode) REFERENCES Courses(courseCode)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT unique_course_position UNIQUE (courseCode, position)
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

-- Assignments and submissions
CREATE TABLE Assignments (
    assignmentId INT AUTO_INCREMENT PRIMARY KEY,
    courseCode VARCHAR(8) NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    dueDate DATETIME NOT NULL,
    totalMarks DECIMAL(6,2) NOT NULL DEFAULT 100.00,
    createdByUserId INT NOT NULL,
    FOREIGN KEY (courseCode) REFERENCES Courses(courseCode)
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


-- Helpful indexes

-- Users
CREATE INDEX idx_users_role ON Users(role);
CREATE INDEX idx_users_fullName ON Users(fullName);

-- Courses
CREATE INDEX idx_courses_createdByAdminId ON Courses(createdByAdminId);

-- Enrollment
CREATE INDEX idx_enrollment_courseCode ON Enrollment(courseCode);

-- Teaching
CREATE INDEX idx_teaching_courseCode ON Teaching(courseCode);

-- Calendar Events
CREATE INDEX idx_calendarevents_courseCode ON CalendarEvents(courseCode);
CREATE INDEX idx_calendarevents_createdByUserId ON CalendarEvents(createdByUserId);
CREATE INDEX idx_calendarevents_eventDateTime ON CalendarEvents(eventDateTime);
CREATE INDEX idx_calendarevents_courseCode_eventDateTime
ON CalendarEvents(courseCode, eventDateTime);

-- Forums
CREATE INDEX idx_forums_courseCode ON Forums(courseCode);
CREATE INDEX idx_forums_createdByUserId ON Forums(createdByUserId);

-- Discussion Threads
CREATE INDEX idx_threads_forumId ON DiscussionThreads(forumId);
CREATE INDEX idx_threads_createdByUserId ON DiscussionThreads(createdByUserId);

-- Posts
CREATE INDEX idx_posts_threadId ON Posts(threadId);
CREATE INDEX idx_posts_userId ON Posts(userId);
CREATE INDEX idx_posts_parentPostId ON Posts(parentPostId);
CREATE INDEX idx_posts_threadId_createdAt ON Posts(threadId, createdAt);

-- Sections
CREATE INDEX idx_sections_courseCode ON Sections(courseCode);
CREATE INDEX idx_sections_courseCode_position ON Sections(courseCode, position);

-- Section Items
CREATE INDEX idx_sectionitems_sectionId ON SectionItems(sectionId);
CREATE INDEX idx_sectionitems_uploadedByUserId ON SectionItems(uploadedByUserId);

-- Assignments
CREATE INDEX idx_assignments_courseCode ON Assignments(courseCode);
CREATE INDEX idx_assignments_createdByUserId ON Assignments(createdByUserId);
CREATE INDEX idx_assignments_dueDate ON Assignments(dueDate);
CREATE INDEX idx_assignments_courseCode_dueDate ON Assignments(courseCode, dueDate);

-- Submissions
CREATE INDEX idx_submissions_studentId ON Submissions(studentId);

