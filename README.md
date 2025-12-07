# SCRS – Smart Course Registration System

A smart web platform to manage course registration, schedules, assignments, and announcements for Students, Professors, TAs, and Admins.

---

## 📘 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
  - [Student](#-student)
  - [Professor--instructor](#-professor--instructor)
  - [Teaching-assistant-ta](#-teaching-assistant-ta)
  - [Admin](#-admin)
- [System Architecture](#-system-architecture)
- [User Roles](#-user-roles)
- [Tech Stack](#-tech-stack)
- [Functional Requirements](#-functional-requirements)
- [Non-Functional Requirements](#-non-functional-requirements)
- [Use Cases](#-use-cases)
- [Core Data Entities](#-core-data-entities)
- [Team Members](#-team-members)

---

## 📝 Overview

The **Smart Course Registration System (SCRS)** is a web-based platform that digitizes the course registration process in a university setting.

It allows:

- Students to browse available courses, register/drop, view schedules, and track assignments & grades.
- Professors and Teaching Assistants (TAs) to manage course content, assignments, announcements, and grading.
- Admins to manage users, courses, and overall system operations.

The system is developed as part of the **Software Engineering Project – Phase 2** using **Flask, HTML, and CSS**.

---

## ✨ Features

### 🎓 Student

- Secure register/login.
- View available courses with:
  - Course name, code, credits
  - Capacity and remaining seats
  - Time slots / schedule
- Register for courses (with capacity & time-conflict checks).
- Drop registered courses during add/drop period.
- View weekly timetable of registered courses.
- View course details, announcements, and assignments.
- Submit assignments online.
- View assignment and course grades.
- Receive email reminders (e.g., upcoming classes, deadlines).

### 👨‍🏫 Professor / Instructor

- Secure login.
- View assigned courses.
- See enrolled students in each course.
- Post and manage assignments (title, description, deadline).
- View and download student submissions.
- Grade assignments and publish grades.
- Post course announcements (e.g., room changes, exam dates).
- Assign TAs and manage their permissions.

### 🧑‍🏫 Teaching Assistant (TA)

- Secure login.
- View courses they assist.
- View enrolled students.
- (If allowed) post announcements and assignments.
- (If allowed) grade student submissions and update grades.

### 🛠️ Admin

- Secure login.
- Manage users:
  - Create student/professor/TA/admin accounts.
  - Edit user info.
  - Delete users.
  - Assign/change roles.
- Manage courses:
  - Create/edit/delete courses.
  - Set course capacity, credits, and schedule.
  - Assign instructors and TAs.
- Monitor system usage and basic reports (e.g., number of students per course).

---

## 🧱 System Architecture

SCRS follows a **modular client–server architecture**:

- **Authentication & Authorization Module**  
  Handles registration, login, logout, and role-based access control.

- **Course & Section Management Module**  
  Manages course definitions, capacities, time slots, and assigned instructors/TAs.

- **Registration & Schedule Module**  
  Handles course enrollment, drop operations, conflict checks, and timetable generation.

- **Assignments & Grading Module**  
  Allows instructors/TAs to create assignments, students to submit, and staff to grade.

- **Announcements & Notification Module**  
  Manages course announcements and sends email reminders/alerts to users.

- **Admin & Reporting Module**  
  Provides admin tools for managing users, courses, and viewing summary information.

> In this phase, data is stored in **in-memory Python structures** (lists/dicts) instead of a persistent database.

---

## 👥 User Roles

| Role       | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| Student   | Registers/drops courses, views schedule, assignments, announcements, grades |
| Professor | Manages course content, assignments, announcements, and grading             |
| TA        | Assists the professor in managing course content and grading                |
| Admin     | Manages all users, courses, and system configuration                        |

---

## 🧰 Tech Stack

- **Frontend:** HTML, CSS  
- **Backend:** Python (Flask)  
- **Data Storage (current phase):** In-memory Python data structures (no external DB yet)  
- **External Services:** Email (SMTP) for notifications and reminders  
- **Protocols:** HTTP/HTTPS, SMTP  
- **Supported Browsers:** Chrome, Edge, Firefox  
- **Supported OS (development):** Windows, Linux  

---

## ✅ Functional Requirements

### Students

- Register/login/logout securely.
- View profile and registered courses.
- Browse all available courses and their details.
- Register for a course if:
  - Seats are available.
  - No schedule conflict with existing courses.
- Drop a registered course during the allowed period.
- View timetable of registered courses.
- View course announcements and materials.
- View assignments and their deadlines.
- Submit assignments.
- View assignment and course grades.
- Receive reminders/notifications (e.g., upcoming classes or deadlines).

### Professors

- Login securely.
- View list of assigned courses.
- View enrolled students in each course.
- Create/edit/delete assignments for their courses.
- View student submissions.
- Grade assignments and update grades.
- Post course announcements.
- Assign and manage TAs for their courses.

### Teaching Assistants (TAs)

- Login securely.
- View courses they are assigned to.
- View enrolled students.
- Perform allowed actions as given by the professor (e.g., grading, post
  ### Admins

- Login securely.
- Create/update/delete user accounts (students, professors, TAs, admins).
- Assign roles and manage permissions.
- Create/update/delete courses.
- Assign professors and TAs to courses.
- Monitor system usage and basic reports.

### System

- Enforce role-based access control.
- Validate inputs and enforce business rules (capacity, conflicts, etc.).
- Send email notifications when needed (e.g., reminders, important announcements).

---

## 🔐 Non-Functional Requirements

- **Usability**
  - Simple and intuitive web interface.
  - Clear navigation for each role (Student/Professor/TA/Admin).
  - Consistent layout and labels.

- **Performance**
  - Reasonable response time for typical operations (view courses, register, view schedule).
  - Efficient in-memory operations for current scale.

- **Security**
  - Secure login with unique credentials.
  - Role-based access to pages and actions.
  - Basic protection of user data (no exposure of passwords in plain text).

- **Reliability**
  - System should operate correctly during registration periods.
  - Minimal failures during normal operation.

- **Portability**
  - Runs on common OS platforms (Windows, Linux) with Python and Flask.
  - Accessible via modern browsers (Chrome, Edge, Firefox).

- **Maintainability**
  - Modular code structure (separated models, controllers, templates).
  - Clear separation of concerns to support future enhancements (e.g., adding a real DB).

---

## 🧩 Use Cases

### Main Actors

- Student  
- Professor  
- Teaching Assistant (TA)  
- Admin  

### Includes

- User login / logout  
- View dashboard (role-based)  
- Browse available courses  
- Course registration and drop  
- View timetable  
- Create and manage assignments (Professor/TA)  
- Submit assignments (Student)  
- Grade assignments (Professor/TA)  
- Post and view announcements  
- Manage users and courses (Admin)  
- Send and receive notifications/reminders  

---

## 🗂️ Core Data Entities

| Entity       | Attributes                                                                                      |
|-------------|--------------------------------------------------------------------------------------------------|
| User        | UserID, Name, Email, Password, Role                                                              |
| Student     | StudentID, Level, Department, RegisteredCourses                                                  |
| Professor   | ProfessorID, Name, Department, AssignedCourses                                                   |
| TA          | TAID, Name, AssignedCourses                                                                      |
| Course      | CourseID, Code, Name, Credits, Capacity, Schedule, InstructorID                                  |
| Enrollment  | EnrollmentID, StudentID, CourseID, Status (Registered/Dropped)                                   |
| Assignment  | AssignmentID, CourseID, Title, Description, Deadline, MaxGrade                                   |
| Submission  | SubmissionID, AssignmentID, StudentID, FilePath, Grade, Feedback                                 |
| Announcement| AnnouncementID, CourseID, Title, Message, Date                                                   |
| Reminder    | ReminderID, UserID, Message, SendDate, Type                                                      |

> In this phase, these entities are represented using Python lists/dictionaries (no real database tables yet).

---

## 👨‍💻 Team Members

Course: **Software Engineering Project – Phase 2**  
Instructor: **Mohameds Sami Rakha**

- 👩‍💻 Mariam Ahmed Maher – 202400733 – s-mariam.maher@zewailcity.edu.eg  
- 👩‍💻 Farida Ehab  – 202201509 – s-farida.fouad@zewailcity.edu.eg  
- 👩‍💻 Elaliaa Elmoez  – 202402473 – s-elaliaa.kotb@zewailcity.edu.eg  
- 👩‍💻 Rahma Ali – 202400365 – s-rahma.anwar@zewailcity.edu.eg  

---

> This project is developed for educational and academic purposes
