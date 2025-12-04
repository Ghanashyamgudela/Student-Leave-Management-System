create database student;
use student;
create table student_details(
id_num varchar(7) not null primary key,
name varchar(20),
email varchar(20),
phone varchar(10),
password varchar(8)
);
create table faculty(
 id_num varchar(10) not null primary key,
 name varchar(20),
 email varchar(20),
 phone varchar(10),
 password varchar(8),
 hod varchar(1) default 'n'
);
create table leave_application(
	num int auto_increment primary key,
    id_num varchar(7),
    from_date varchar(15),
    to_date varchar(15),
    reason varchar(200),
    status varchar(1) default 'c'
);
create user 'manager'@'localhost' identified by 'leave';
grant all privileges on college.* to 'manager'@'localhost';

select * from student_details;
insert into faculty values('f1','f1','f1@gmail.com','f1','f1','n'),
('f2','f2','f2@gmail.com','f2','f2','n'),('h1','h1','h1@gmail.com','h1','h1','y');
select * from faculty;
select * from leave_application;
CREATE table comments(
	num int,
    comment varchar(25)
);
SELECT num FROM leave_application where id_num='5';
INSERT INTO comments VALUES ((SELECT num FROM leave_application where id_num='5'), "aaa");
select * from comments
CREATE TABLE leave_application (
    num INT AUTO_INCREMENT PRIMARY KEY,
    id_num VARCHAR(20) NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status CHAR(1) DEFAULT 'c',   -- c = created, b = under HoD review, a = approved, r = rejected
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (id_num) REFERENCES student_details(id_num)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
select * from admins
INSERT INTO admins (username, password) VALUES ('admin', 'admin123');
select * from leave_requests;
CREATE TABLE leave_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    reason VARCHAR(255) NOT NULL,
    from_date DATE NOT NULL,
    to_date DATE NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
);
CREATE TABLE student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);
select * from student;
CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);
INSERT INTO admin (username, password) VALUES ('admin', 'admin123');
INSERT INTO admin (username, password) VALUES ('admin@gmail.com', 'admin1234');

select * from student;

use student;
ALTER TABLE student
  ADD COLUMN is_verified BOOLEAN DEFAULT 0,
  ADD COLUMN verification_token VARCHAR(255);
SELECT email, is_verified FROM student;

