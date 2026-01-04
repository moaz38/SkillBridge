
-- PROJECT: Skill Bridge Career System
-- PHASE: 2 Final Submission 
-- AUTHOR: Muhammad Moaz (SAP: 70148238)


CREATE DATABASE SkillBridge_DB;
USE SkillBridge_DB;


-- 1. TABLE CREATION


CREATE TABLE COMPANY (
    company_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    industry VARCHAR(100),
    location VARCHAR(100)
);

CREATE TABLE SKILL (
    skill_id INT PRIMARY KEY AUTO_INCREMENT,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100)
);

CREATE TABLE COURSE (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    provider VARCHAR(100),
    duration VARCHAR(50)
);

CREATE TABLE PROJECT (
    project_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    complexity_level VARCHAR(50),
    description TEXT
);

CREATE TABLE STUDENT (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    major VARCHAR(100),
    graduation_year YEAR
);

-- Dependent Tables
CREATE TABLE INTERNSHIP (
    internship_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(150) NOT NULL,
    role VARCHAR(100),
    start_date DATE,
    duration VARCHAR(50),
    company_id INT,
    FOREIGN KEY (company_id) REFERENCES COMPANY(company_id) ON DELETE CASCADE
);

CREATE TABLE RECOMMENDATION (
    reco_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    target_id INT NOT NULL, 
    reco_type VARCHAR(50) NOT NULL,
    date_generated DATE,
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE
);

-- Linking Tables
CREATE TABLE STUDENT_SKILL (
    student_id INT,
    skill_id INT,
    PRIMARY KEY (student_id, skill_id),
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES SKILL(skill_id) ON DELETE CASCADE
);

CREATE TABLE COURSE_SKILL (
    course_id INT,
    skill_id INT,
    PRIMARY KEY (course_id, skill_id),
    FOREIGN KEY (course_id) REFERENCES COURSE(course_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES SKILL(skill_id) ON DELETE CASCADE
);

CREATE TABLE PROJECT_SKILL (
    project_id INT,
    skill_id INT,
    PRIMARY KEY (project_id, skill_id),
    FOREIGN KEY (project_id) REFERENCES PROJECT(project_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES SKILL(skill_id) ON DELETE CASCADE
);

CREATE TABLE STUDENT_APPLICATION (
    app_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    internship_id INT,
    status VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES INTERNSHIP(internship_id) ON DELETE CASCADE
);


-- 2. DATA INSERTION


-- A. SKILLS (25 Skills)
INSERT INTO SKILL (skill_name, category) VALUES 
('Python', 'Programming'), ('Java', 'Programming'), ('C++', 'Programming'),
('Web Development', 'Programming'), ('JavaScript', 'Programming'), ('React', 'Programming'),
('SQL', 'Database'), ('MongoDB', 'Database'), ('Data Analysis', 'Data Science'),
('Machine Learning', 'Data Science'), ('Power BI', 'Data Science'),
('Graphic Design', 'Design'), ('UI/UX Design', 'Design'), ('Video Editing', 'Design'),
('Digital Marketing', 'Marketing'), ('SEO', 'Marketing'), ('Content Writing', 'Marketing'),
('Communication', 'Soft Skill'), ('Leadership', 'Soft Skill'), ('Problem Solving', 'Soft Skill'),
('Project Management', 'Business'), ('MS Office', 'Business'), ('Accounting', 'Business'),
('Flutter', 'Mobile Dev'), ('Cyber Security', 'IT Security');

-- B. COMPANIES 
INSERT INTO COMPANY (name, industry, location) VALUES 
('Systems Ltd', 'IT Services', 'Lahore'),
('Netsol Technologies', 'Software', 'Lahore'),
('Arbisoft', 'Software', 'Lahore'),
('Devsinc', 'Software', 'Lahore'),
('Interloop', 'Textile & IT', 'Faisalabad'),
('Masood Textile Mills', 'Textile & IT', 'Faisalabad'),
('Sitara Chemical', 'Industrial IT', 'Faisalabad'),
('CyberSoft', 'Software House', 'Faisalabad');

-- C. INTERNSHIPS (Matching Skills + Locations)

INSERT INTO INTERNSHIP (title, role, start_date, duration, company_id) VALUES 
('Python Developer Intern', 'Backend Dev', '2025-06-01', '3 Months', 1), -- Systems (LHR)
('Java Software Intern', 'Software Engineer', '2025-06-15', '6 Months', 2), -- Netsol (LHR)
('Web Development Intern', 'Frontend Dev', '2025-07-01', '3 Months', 4), -- Devsinc (LHR)
('React Native Intern', 'Mobile Dev', '2025-06-10', '3 Months', 3), -- Arbisoft (LHR)
('Data Analysis Intern', 'Data Analyst', '2025-08-01', '6 Months', 5), -- Interloop (FSD)
('IT Support Intern', 'Network Admin', '2025-05-20', '2 Months', 6), -- Masood (FSD)
('Graphic Design Intern', 'Designer', '2025-06-01', '3 Months', 7), -- Sitara (FSD)
('Digital Marketing Intern', 'Social Media', '2025-07-15', '2 Months', 8), -- CyberSoft (FSD)
('SEO Specialist Intern', 'SEO Expert', '2025-06-01', '3 Months', 8), -- CyberSoft (FSD)
('Machine Learning Intern', 'AI Engineer', '2025-09-01', '6 Months', 1), -- Systems (LHR)
('HR & Management Intern', 'HR Assistant', '2025-06-01', '2 Months', 5), -- Interloop (FSD)
('Cyber Security Intern', 'Security Analyst', '2025-07-01', '4 Months', 2); -- Netsol (LHR)

-- D. COURSES (Linked to Skills)
INSERT INTO COURSE (title, provider, duration) VALUES 
('Complete Python Bootcamp', 'Udemy', '10 Weeks'),
('Java Programming Masterclass', 'Coursera', '12 Weeks'),
('Full Stack Web Development', 'Udemy', '16 Weeks'),
('Google Data Analytics Cert', 'Coursera', '24 Weeks'),
('Graphic Design Specialist', 'CalArts', '8 Weeks'),
('Digital Marketing 101', 'Google Garage', '4 Weeks'),
('Flutter & Dart Guide', 'Udemy', '12 Weeks'),
('Project Management Professional', 'PMI', '6 Weeks'),
('Complete SEO Training', 'Udemy', '5 Weeks'),
('Cyber Security Basics', 'Cisco', '6 Weeks');

-- E. PROJECTS (Linked to Skills)
INSERT INTO PROJECT (title, complexity_level, description) VALUES 
('Hospital Management System', 'Intermediate', 'Build a desktop app using Java and SQL'),
('E-Commerce Website', 'Advanced', 'Full stack site using React and Node.js'),
('Sales Dashboard', 'Intermediate', 'Data visualization using Power BI'),
('Portfolio Website', 'Basic', 'Personal site using HTML/CSS/JS'),
('Face Recognition App', 'Advanced', 'AI project using Python and OpenCV'),
('Brand Identity Design', 'Basic', 'Create logo and branding kit'),
('Social Media Campaign', 'Basic', 'Run a mock campaign for a product'),
('Chat Application', 'Intermediate', 'Real-time chat using Flutter'),
('Network Security Audit', 'Advanced', 'Simulate a security audit'),
('Inventory System', 'Intermediate', 'Database project using SQL');

-- F. LINKING 

-- Link Courses to Skills 

INSERT INTO COURSE_SKILL (course_id, skill_id) VALUES 
(1, 1), -- Python Course -> Python
(2, 2), -- Java Course -> Java
(3, 4), -- Web Dev Course -> Web Dev
(4, 9), -- Data Analytics -> Data Analysis
(5, 12), -- Graphic Design -> Graphic Design
(6, 15), -- Digital Mkt -> Digital Marketing
(7, 24), -- Flutter -> Flutter
(8, 21), -- PM -> Project Management
(9, 16), -- SEO -> SEO
(10, 25); -- Cyber Sec -> Cyber Security

-- Link Projects to Skills
INSERT INTO PROJECT_SKILL (project_id, skill_id) VALUES 
(1, 2), -- Hospital Sys -> Java
(1, 7), -- Hospital Sys -> SQL
(2, 4), -- E-Commerce -> Web Dev
(2, 6), -- E-Commerce -> React
(3, 11), -- Dashboard -> Power BI
(4, 4), -- Portfolio -> Web Dev
(5, 1), -- Face Rec -> Python
(5, 10), -- Face Rec -> ML
(6, 12), -- Brand ID -> Graphic Design
(7, 15), -- Campaign -> Digital Mkt
(8, 24), -- Chat App -> Flutter
(9, 25), -- Audit -> Cyber Security
(10, 7); -- Inventory -> SQL
