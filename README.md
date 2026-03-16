# COMP3161 FINAL PROJECT (OURVLE CLONE API) 2026

## Overview
The API is built using **Flask** and **MySQL**, and uses **raw SQL queries** instead of an ORM.

The system supports:

- User registration and login
- Course creation (admin only)
- Student course enrollment
- Lecturer course management
- Calendar events for courses
- Discussion forums and threads
- Course content organized by sections
- Assignments, submissions, and grading
- Reporting using SQL views

---

## Installation

### 1. Clone the repository

```bash
git clone
cd course-management-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
### Mac / Linux
source venv/bin/activate

### Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```
