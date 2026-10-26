USE company_db;

INSERT INTO departments (name) VALUES
('Cloud'),
('Development'),
('HR'),
('Database');

INSERT INTO employees (name,email,city,salary,department_id) VALUES
('Rahul Sharma','rahul@example.com','Pune',65000,1),
('Amit Kulkarni','amit@example.com','Mumbai',72000,1),
('Neha Deshmukh','neha@example.com','Pune',68000,1),
('Kiran Pawar','kiran@example.com','Nashik',61000,1),
('Priya Patil','priya@example.com','Pune',59000,2),
('Rohit Jadhav','rohit@example.com','Mumbai',75000,2);

INSERT INTO projects (name,budget,department_id) VALUES
('AWS Cloud Migration',500000,1),
('Internal DevOps Platform',300000,1),
('Employee Portal',200000,2);

INSERT INTO employee_projects (employee_id,project_id) VALUES
(1,1),(2,1),(3,1),(4,1),(1,2),(2,2),(5,3),(6,3);

INSERT INTO salaries (employee_id,salary,effective_date) VALUES
(1,65000,'2026-01-01'),
(2,72000,'2026-01-01'),
(3,68000,'2026-01-01'),
(4,61000,'2026-01-01'),
(5,59000,'2026-01-01'),
(6,75000,'2026-01-01');
