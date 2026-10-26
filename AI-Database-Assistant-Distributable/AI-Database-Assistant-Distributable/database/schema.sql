CREATE DATABASE IF NOT EXISTS company_db;
USE company_db;

CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    city VARCHAR(100),
    salary DECIMAL(12,2),
    department_id INT,
    CONSTRAINT fk_employees_department
        FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    budget DECIMAL(14,2),
    department_id INT,
    CONSTRAINT fk_projects_department
        FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE employee_projects (
    employee_id INT,
    project_id INT,
    PRIMARY KEY (employee_id, project_id),
    CONSTRAINT fk_ep_employee
        FOREIGN KEY (employee_id) REFERENCES employees(id),
    CONSTRAINT fk_ep_project
        FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE salaries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    salary DECIMAL(12,2),
    effective_date DATE,
    CONSTRAINT fk_salaries_employee
        FOREIGN KEY (employee_id) REFERENCES employees(id)
);
