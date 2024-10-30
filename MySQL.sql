create database project_dbms;
use  project_dbms;
CREATE TABLE User_account(name VARCHAR(50), 
    account_number BIGINT PRIMARY KEY,
    gender VARCHAR(1),
    aadhar_id VARCHAR(12),
    DOB DATE,
    address VARCHAR(100),
    account_type VARCHAR(10),
    contact VARCHAR(13)
  );

 create table balance(account_number bigint primary key,current_balance decimal(10,2),constraint fk_balance_user_account foreign key (account_number) references user_account (account_number) on delete cascade on update cascade);

CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    account_number bigint NOT NULL,
    transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    transaction_type ENUM('DEPOSIT', 'WITHDRAWAL') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (account_number) REFERENCES user_account (account_number)
);
CREATE TABLE fd (account_number BIGINT,amount DECIMAL(15,2),term FLOAT,maturity_date DATE,interest DECIMAL(15,2),final_amt DECIMAL(15,2),CONSTRAINT fk_fd_user_account FOREIGN KEY (account_number) REFERENCES user_account(account_number) ON DELETE CASCADE ON UPDATE CASCADE);

create table rd(account_number bigint,monthly_amount decimal(10,2),term float,maturity_date date,interest decimal(5,2),final_amt decimal(10,2),installment_period int, constraint fk_rd_user_account foreign key (account_number) references user_account (account_number) on delete cascade on update cascade);

create table loans(account_number bigint primary key,amount decimal(10,2),term decimal(5,2),interest_rate decimal(10,2),start_date date,end_date date,final_pay decimal(10,2),installment_period int,installment_amt decimal(10,2), constraint fk_loans_user_account foreign key (account_number) references user_account(account_number) on delete cascade on update cascade);
show tables;