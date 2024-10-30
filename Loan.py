import tkinter as tk
from tkinter import *
import Database_Connection as dc
from tkinter import messagebox
import mysql.connector
import threading
import datetime
import time
from dateutil.relativedelta import relativedelta

def get_db_connection():
    return dc.con()

def calculate_installments(amount, term, rate, period):
    total_months = term * 12
    monthly_interest_rate = rate / 12 / 100
    installment_amt = amount * monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -total_months)
    total_installments = total_months // period
    return round(installment_amt, 2), total_installments

def calc_final_pay(amount,term,rate):
    si=amount*rate*term/100
    fp=amount+si
    return fp

def deduct_installment(account_no, installment_amt, period):
    while True:
        try:
            mydb = get_db_connection()
            mycursor = mydb.cursor()
            query = "UPDATE balance SET current_balance = current_balance - %s WHERE account_number = %s"
            query2 = "UPDATE loans SET remaining_amt = remaining_amt - %s WHERE account_number = %s"
            query3 = "INSERT INTO transactions (account_number,transaction_type,amount) VALUES (%s,'WITHDRAWAL (LOAN)',%s)"
            mycursor.execute(query, (installment_amt, account_no))
            mycursor.execute(query2, (installment_amt, account_no))
            mycursor.execute(query3, (account_no, installment_amt))
            mydb.commit()
            print(f"Installment of {installment_amt} deducted from account {account_no}")

            # Check for full payment
            check_query = "SELECT remaining_amt FROM loans WHERE account_number = %s"
            mycursor.execute(check_query, (account_no,))
            remaining_amt = mycursor.fetchone()[0]

            if remaining_amt == 0:
                # Clear loan record
                clear_query = "DELETE FROM loans WHERE account_number = %s"
                mycursor.execute(clear_query, (account_no,))
                mydb.commit()
                print(f"Loan for account {account_no} cleared successfully.")
                messagebox.showinfo("Success", "Loan cleared off successfully!")
                break  # Stop deducting installments

        except mysql.connector.Error as err:
            print(f"Error deducting installment: {err}")
        finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
        time.sleep(period * 30 * 24 * 60 * 60)  # Convert period to seconds


def loan_interface():
    root = Tk()
    root.attributes("-fullscreen", True)
    root.title('Loan Management')

    hed = Label(root, text="Loan Management", bg="#4361ee", fg="#e9ecef", font="Times 60 underline bold")
    hed.pack(fill=X)

    base_frame = Frame(root, bg="#4cc9f0")

    account_label = Label(base_frame, text="Account No:", bg="#023047", fg="#ced4da", font='Times 30 bold', width=12)
    account_label.grid(row=0, column=0, padx=5, pady=(5, 30))
    account_entry = Entry(base_frame, font='Times 30 bold', width=10, bg='#023047', fg='#ced4da')
    account_entry.grid(row=0, column=1, padx=(0, 100), pady=(5, 30))

    amount_label = Label(base_frame, text="Loan Amount:", bg="#023047", fg="#ced4da", font='Times 30 bold', width=12)
    amount_label.grid(row=1, column=0, padx=5, pady=(5, 30))
    amount_entry = Entry(base_frame, font='Times 30 bold', width=10, bg='#023047', fg='#ced4da')
    amount_entry.grid(row=1, column=1, padx=(0, 100), pady=(5, 30))

    term_options=[1,2,3,5,7,10]
    term_variable=StringVar(root)
    term_variable.set(term_options[0])
    term_dropdown=OptionMenu(base_frame,term_variable,*term_options)
    term_label = Label(base_frame, text="Term (years):", bg="#023047",
                        fg="#ced4da", font='Times 30 bold', width=12)
    term_label.grid(row=2, column=0, padx=5, pady=(5, 30))
    term_dropdown.config(width=10, font='Times 30 bold', bg='#023047', fg='#ced4da')
    term_dropdown.grid(row=2, column=1, padx=(0, 100), pady=(5, 30))
    
    rate_options=[1,1.5,2,2.5,3,5]
    rate_variable=StringVar(root)
    rate_variable.set(rate_options[0])
    rate_dropdown=OptionMenu(base_frame,rate_variable,*rate_options)
    rate_label = Label(base_frame, text="Interest Rate:", bg="#023047",
                        fg="#ced4da", font='Times 30 bold', width=12)
    rate_label.grid(row=3, column=0, padx=5, pady=(5, 30))
    rate_dropdown.config(width=10, font='Times 30 bold', bg='#023047', fg='#ced4da')
    rate_dropdown.grid(row=3, column=1, padx=(0, 100), pady=(5, 30))

    period_options=[1,2,3,4,6,8,10,12]
    period_variable=StringVar(root)
    period_variable.set(period_options[0])
    period_dropdown=OptionMenu(base_frame,period_variable,*period_options)
    period_label = Label(base_frame, text="Installment Period (months):", bg="#023047", fg="#ced4da", font='Times 30 bold', width=25)
    period_label.grid(row=4, column=0, padx=5, pady=(5, 30))
    period_dropdown.config(width=10, font='Times 30 bold', bg='#023047', fg='#ced4da')
    period_dropdown.grid(row=4, column=1, padx=(0, 100), pady=(5, 30))

    def fetch_value():
        account_no = int(account_entry.get())
        amount = float(amount_entry.get())
        term = float(term_variable.get())
        rate = float(rate_variable.get())
        period = int(period_variable.get())
        start_date = datetime.date.today()
        end_date = start_date + relativedelta(years=term)

        installment_amt, total_installments = calculate_installments(amount, term, rate, period)
        final_pay=calc_final_pay(amount,term,rate)
        mydb = get_db_connection()
        mycursor = mydb.cursor()
        # Check initial balance before granting loan
        query = "SELECT current_balance FROM balance WHERE account_number = %s"
        mycursor.execute(query, (account_no,))
        initial_balance = mycursor.fetchone()[0]

        if initial_balance < installment_amt:
            messagebox.showerror("Error", "Loan cannot be granted to accounts with low balance.")
            return  # Exit function if balance is negative
        try:
            query = """INSERT INTO loans (account_number, amount, term, interest_rate, start_date, end_date, final_pay, installment_period, installment_amt, remaining_amt) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            data = (account_no, amount, term, rate, start_date, end_date, final_pay, period, installment_amt, final_pay)
            mycursor.execute(query, data)
            mydb.commit()
            messagebox.showinfo("Success", f"Loan granted successfully.\nAccount Number: {account_no}\nInstallment Amount: INR {installment_amt}")
            # Start installment deduction thread
            installment_thread = threading.Thread(target=deduct_installment, args=(account_no, installment_amt, period), daemon=True)
            installment_thread.start()
            root.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", "Database error: " + str(err))
        finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()

    base_frame.pack(pady=(65, 50))
    submit = Button(root, text='Grant Loan', bg="#4361ee", fg="#e9ecef", font='Times 25 bold', command=fetch_value)
    submit.pack()
    root.bind("<Escape>", lambda event: root.destroy())
    root.bind("<Return>", lambda event: fetch_value())
    root.configure(bg="#4cc9f0")
    mainloop()

if __name__ == "__main__":
    loan_interface()
