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
    maturity_date = date.today() + timedelta(days=int(term * 365.25))  # Consider leap years
    return maturity_date

def calc_final_amount(amount, term, interest_rate):
    """Calculates the final maturity amount based on principal, term, and interest rate."""
    final_amount = amount * (1 + interest_rate / 100) ** term
    return round(final_amount, 2)

def create_fixed_deposit(account_no, amount, term, interest_rate):
    """Creates a new fixed deposit record in the database and deducts the amount from the current balance."""
    maturity_date = calculate_maturity_date(amount, term, interest_rate)
    final_amount = calc_final_amount(amount, term, interest_rate)

    try:
        mydb = get_db_connection()
        mycursor = mydb.cursor()

        # Check if sufficient balance
        check_balance_query = "SELECT current_balance FROM balance WHERE account_number = %s"
        mycursor.execute(check_balance_query, (account_no,))
        current_balance = mycursor.fetchone()[0]
        if current_balance < amount:
            messagebox.showerror("Insufficient Balance", "You do not have enough balance to create an FD.")
            return  # Exit the function to prevent further processing
        # Deduct the amount from the current balance
        deduct_query = "UPDATE balance SET current_balance = current_balance - %s WHERE account_number = %s"
        trans_query = "INSERT INTO transactions (account_number,transaction_type,amount) VALUES (%s,'WITHDRAWAL (FD)',%s)"
        mycursor.execute(deduct_query, (amount, account_no))
        mycursor.execute(trans_query, (account_no, amount))

        # Insert the FD record
        insert_query = """INSERT INTO fd (account_number, amount, term, maturity_date, interest, final_amt) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
        data = (account_no, amount, term, maturity_date, interest_rate, final_amount)
        mycursor.execute(insert_query, data)

        mydb.commit()
        messagebox.showinfo("Success", f"Fixed Deposit created successfully.\nAccount Number: {account_no}\nMaturity Amount: INR {final_amount:.2f}\nMaturity Date: {maturity_date.strftime('%Y-%m-%d')}")

    except mysql.connector.Error as err:
        messagebox.showerror("Error", "Database error: " + str(err))
    except ValueError as e:
        messagebox.showerror("Error", str(e))
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
def process_matured_fds():
    try:
        mydb = get_db_connection()
        mycursor = mydb.cursor()

        # Check for matured FDs
        today = date.today()
        query = "SELECT * FROM fd WHERE maturity_date = %s"
        mycursor.execute(query, (today,))

        for fd in mycursor.fetchall():
            account_no = fd[0]
            amount = fd[1]
            term = fd[2]
            maturity_date = date.today()
            interest_rate = fd[4]
            final_amount = calc_final_amount(amount, term, interest_rate)

            # Update account balance
            update_balance_query = "UPDATE balance SET current_balance = current_balance + %s WHERE account_number = %s"
            update_transacton_query = "INSERT INTO transactions (account_number,transaction_type,amount) VALUES (%s,'DEPOSIT (FD)',%s)"
            delete_fd_record = "DELETE FROM fd WHERE maturity_date = %s"
            mycursor.execute(update_transaction_query, (account_no, final_amount))
            mycursor.execute(update_balance_query, (final_amount, account_no))
            mycursor.execute(delete_fd_record, (maturity_date,))
        mydb.commit()
    except mysql.connector.Error as err:
        messagebox.showerror(f"Database error: {err}")

    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

def fd_interface():
    root = Tk()
    root.attributes("-fullscreen", True)
    root.title('Fixed Deposit Management')

    hed = Label(root, text="Fixed Deposit Management", bg="#4361ee", fg="#e9ecef", font="Times 60 underline bold")
    hed.pack(fill=X)

    base_frame = Frame(root, bg="#4cc9f0")

    account_label = Label(base_frame, text="Account No:", bg="#023047", fg="#ced4da", font='Times 30 bold', width=12)
    account_label.grid(row=0, column=0, padx=5, pady=(5, 30))
    account_entry = Entry(base_frame, font='Times 30 bold', width=10, bg='#023047', fg='#ced4da')
    account_entry.grid(row=0, column=1, padx=(0, 100), pady=(5, 30))

    amount_label = Label(base_frame, text="Deposit Amount:", bg="#023047", fg="#ced4da", font='Times 30 bold', width=12)
    amount_label.grid(row=1, column=0, padx=5, pady=(5, 30))
    amount_entry = Entry(base_frame, font='Times 30 bold', width=10, bg='#023047', fg='#ced4da')
    amount_entry.grid(row=1, column=1, padx=(0, 100), pady=(5, 30))

    term_options = [1, 2, 3, 5, 7, 10]  # Term options in years
    term_variable = StringVar(root)
    term_variable.set(term_options[0])
    term_dropdown = OptionMenu(base_frame, term_variable, *term_options)
    term_label = Label(base_frame, text="Term (years):", bg="#023047", fg="#ced4da", font='Times 30 bold', width=12)
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

    def create_fd_and_start_processing():
        account_no = int(account_entry.get())
        amount = float(amount_entry.get())
        term = float(term_variable.get())
        interest_rate = float(rate_variable.get())
        final_amount=calc_final_amount(amount,term,interest_rate)
        maturity_date=calculate_maturity_date(amount,term,interest_rate)
        create_fixed_deposit(account_no, amount, term, interest_rate)

        # Start a background thread to process matured FDs
        maturity_thread = threading.Thread(target=process_matured_fds, daemon=True)
        maturity_thread.start()

    base_frame.pack(pady=(65, 50))
    submit_button = Button(root, text='Create FD and Start Processing', bg="#4361ee", fg="#e9ecef", font='Times 25 bold', command=create_fd_and_start_processing)
    submit_button.pack(pady=(10, 0))
    root.bind("<Escape>", lambda event: root.destroy())
    root.bind("<Return>", lambda event: create_fd_and_start_processing())
    root.configure(bg="#4cc9f0")
    root.mainloop()

if __name__ == "__main__":
    fd_interface()
