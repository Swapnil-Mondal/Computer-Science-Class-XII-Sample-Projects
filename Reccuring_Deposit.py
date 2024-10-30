import tkinter as tk
from tkinter import *
import Database_Connection as dc  
from tkinter import messagebox
import mysql.connector
from datetime import date, timedelta
import threading

def get_db_connection():
    return dc.con()

def calculate_maturity_date(amount, term, interest_rate):
    """Calculates the maturity date based on principal, term, and interest rate."""
    maturity_date = date.today() + timedelta(days=int(term * 30.4375))  # Consider leap years
    return maturity_date

def calc_final_amount(amount, term, interest_rate):
    """Calculates the final maturity amount based on principal, term, and interest rate."""
    final_amount = amount * (1 + interest_rate / 100) ** term
    return round(final_amount, 2)

def create_recurring_deposit(account_no, monthly_amount, term, interest_rate):
    """Creates a new recurring deposit record in the database and deducts the first installment."""
    maturity_date = calculate_maturity_date(monthly_amount * term * 12, term, interest_rate)
    final_amount = calc_final_amount(monthly_amount * term * 12, term, interest_rate)

    try:
        mydb = get_db_connection()
        mycursor = mydb.cursor()

        # Insert the RD record
        insert_query = """INSERT INTO rd (account_number, monthly_amount, term, maturity_date, interest, final_amt)
                                    VALUES (%s, %s, %s, %s, %s, %s)"""
        data = (account_no, monthly_amount, term, maturity_date, interest_rate, final_amount)
        mycursor.execute(insert_query, data)
        mydb.commit()

        messagebox.showinfo("Success", f"Recurring Deposit created successfully.\nAccount Number: {account_no}\nMaturity Amount: INR {final_amount:.2f}\nMaturity Date: {maturity_date.strftime('%Y-%m-%d')}")

        # Deduct the first installment immediately
        deduct_installment(account_no, monthly_amount)

    except mysql.connector.Error as err:
        messagebox.showerror("Error", "Database error: " + str(err))
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

def deduct_installment(account_no, installment_amount):
    """Deducts the installment amount from the balance and checks for maturity."""
    try:
        mydb = get_db_connection()
        mycursor = mydb.cursor()

        deduct_query = "UPDATE balance SET current_balance = current_balance - %s WHERE account_number = %s"
        trans_query = "INSERT INTO transactions (account_number,transaction_type,amount) VALUES (%s,'WITHDRAWAL (RD)',%s)"
        mycursor.execute(deduct_query, (installment_amount, account_no))
        mycursor.execute(trans_query, (account_no,installment_amount))
        mydb.commit()

        # Check if maturity date has passed
        check_maturity_query = "SELECT maturity_date FROM rd WHERE account_number = %s"
        mycursor.execute(check_maturity_query, (account_no,))
        maturity_date = mycursor.fetchone()[0]
        check_date = date.today()

        if check_date == maturity_date:
            # Maturity reached, deposit final amount to current_balance
            final_amount_query = "SELECT final_amt FROM rd WHERE maturity_date = %s"
            mycursor.execute(final_amount_query, (check_date,))
            final_amount = mycursor.fetchone()[0]

            deposit_query = "UPDATE balance SET current_balance = current_balance + %s WHERE account_number = %s"
            trans_query = "INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, 'DEPOSIT (RD Maturity)', %s)"
            mycursor.execute(deposit_query, (final_amount, account_no))
            mycursor.execute(trans_query, (account_no, final_amount))

            # Delete RD record as it's matured
            delete_query = "DELETE FROM rd WHERE maturity_date = %s"
            mycursor.execute(delete_query, (check_date,))

            messagebox.showinfo("RD Matured", f"Recurring Deposit for account {account_no} has matured. Final amount credited to your account.")

    except mysql.connector.Error as err:
        print(f"Error deducting installment or processing maturity: {err}")

    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

def schedule_installments(account_no, installment_amount, term):
    """Schedule the installment deduction from the balance in a separate thread."""
    installment_thread = threading.Thread(target=deduct_installment, args=(account_no, installment_amount), daemon=True)
    installment_thread.start()

def rd_interface():
    root = Tk()
    root.attributes("-fullscreen", True)
    root.title('Recurring Deposit')

    hed = Label(root, text="Recurring Deposit", bg="#4361ee", fg="#e9ecef", font="Times 60 underline bold")
    hed.pack(fill=X)

    base_frame = Frame(root, bg="#4cc9f0")

    account_label = Label(base_frame, text="Account No:", bg="#023047", fg="#ced4da", font='Times 30 bold', width=12)
    account_label.grid(row=0, column=0, padx=5, pady=(5, 30))
    account_entry = Entry(base_frame, font='Times 30 bold', width=10, bg='#023047', fg='#ced4da')
    account_entry.grid(row=0, column=1, padx=(0, 100), pady=(5, 30))

    monthly_amount_label = Label(base_frame, text="Monthly Amount:", bg="#023047", fg="#ced4da", font='Times 30 bold', width=12)
    monthly_amount_label.grid(row=1, column=0, padx=5, pady=(5, 30))
    monthly_amount_entry = Entry(base_frame, font='Times 30 bold', width=10, bg='#023047', fg='#ced4da')
    monthly_amount_entry.grid(row=1, column=1, padx=(0, 100), pady=(5, 30))

    term_options = [6, 8, 12, 15, 20, 24]  # Term options in months
    term_variable = StringVar(root)
    term_variable.set(term_options[0])
    term_dropdown = OptionMenu(base_frame, term_variable, *term_options)
    term_label = Label(base_frame, text="Term (months):", bg="#023047", fg="#ced4da", font='Times 30 bold', width=12)
    term_label.grid(row=2, column=0, padx=5, pady=(5, 30))
    term_dropdown.config(width=10, font='Times 30 bold', bg='#023047', fg='#ced4da')
    term_dropdown.grid(row=2, column=1, padx=(0, 100), pady=(5, 30))

    rate_options = [1, 1.5, 2, 2.5, 3, 5, 7.5, 10]  # Interest rate options
    rate_variable = StringVar(root)
    rate_variable.set(rate_options[0])
    rate_dropdown = OptionMenu(base_frame, rate_variable, *rate_options)
    rate_label = Label(base_frame, text="Interest Rate:", bg="#023047", fg="#ced4da", font='Times 30 bold', width=12)
    rate_label.grid(row=3, column=0, padx=5, pady=(5, 30))
    rate_dropdown.config(width=10, font='Times 30 bold', bg='#023047', fg='#ced4da')
    rate_dropdown.grid(row=3, column=1, padx=(0, 100), pady=(5, 30))

    def create_rd_and_start_processing():
        account_no = int(account_entry.get())
        monthly_amount = float(monthly_amount_entry.get())
        term = int(term_variable.get())
        interest_rate = float(rate_variable.get())

        create_recurring_deposit(account_no, monthly_amount, term, interest_rate)

        messagebox.showinfo("Success", "Recurring Deposit created successfully.")

    base_frame.pack(pady=(65, 50))
    submit_button = Button(root, text='Create RD', bg="#4361ee", fg="#e9ecef", font='Times 25 bold', command=create_rd_and_start_processing)
    submit_button.pack(pady=(10, 0))
    root.bind("<Escape>", lambda event: root.destroy())
    root.bind("<Return>", lambda event: create_rd_and_start_processing())
    root.configure(bg="#4cc9f0")
    root.mainloop()

if __name__ == "__main__":
    rd_interface()
