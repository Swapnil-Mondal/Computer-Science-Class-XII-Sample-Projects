import tkinter as tk
import Database_Connection as dc
import mysql.connector
import threading
import time
from queue import Queue
from tkinter import *
balance_update_queue = Queue()
def get_db_connection():
    return dc.con()
def insert_in_transactions(account_no):
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    fetch_query = "SELECT interest_rate, current_balance FROM balance WHERE account_number = %s"
    mycursor.execute(fetch_query, (account_no,))
    result = mycursor.fetchone()
    if result:
        return int(result[0]), int(result[1])
    
def update_balances(balance_var, account_no):
    while True:
        try:
            mydb = get_db_connection()
            mycursor = mydb.cursor()

            # Fetch the current balance and interest rate
            interest, balance = insert_in_transactions(account_no)

            # Calculate the interest and update the balance
            new_balance1 = balance + (balance * interest / 100 / 365)
            new_balance = round(new_balance1, 2)
            update_query = "UPDATE balance SET current_balance = %s WHERE account_number = %s"
            mycursor.execute(update_query, (new_balance, account_no))
            mydb.commit()

            # Insert the interest amount into the transactions table
            trans_query = "INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, 'DEPOSIT (INT)', %s)"
            mycursor.execute(trans_query, (account_no, new_balance - balance))
            mydb.commit()

            # Update the balance label
            balance_var.set(f"Current balance: INR {new_balance}")
            print(f"Updated balance for account {account_no}: {new_balance}")
            balance_update_queue.put(new_balance)

        except mysql.connector.Error as err:
            print(f"Error updating balances: {err}")
        finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
        time.sleep(60)

def check_balance():
    global root1, balance_update_thread
    root1 = Toplevel()
    root1.attributes("-fullscreen", True)
    root1.title('Check Balance')

    hed = Label(root1, text="Check Balance", bg="#4361ee", fg="#e9ecef", font="Times 60 underline bold")
    hed.pack(fill=X)

    base_frame = Frame(root1, bg="#4cc9f0")

    account_number_label = Label(base_frame, text="Enter A/C No:", bg="#7209b7", fg="#ced4da", font='Times 30 bold', width=11)
    account_number_label.grid(row=0, column=0, padx=(0, 5))
    account_number_entry = Entry(base_frame, font='Times 30 bold', width=12, bg='#7209b7', fg='#ced4da')
    account_number_entry.grid(row=0, column=1)

    base_frame.pack(pady=20, padx=20)

    result_label = Label(root1, text="", bg="#4cc9f0", fg="#000000", font='Times 30 bold')
    result_label.pack(pady=20)
    def submit():
        global balance_update_thread
        try:
            account_no = account_number_entry.get()
            balance_var = tk.StringVar()
            root1.update_idletasks()
            balance_var.set("Fetching...")
            result_label.config(textvariable=balance_var)
            if balance_update_thread is None or not balance_update_thread.is_alive():
                balance_update_thread = threading.Thread(target=update_balances, args=(balance_var, account_no), daemon=True)
                balance_update_thread.start()
        except mysql.connector.Error as err:
            result_label.config(text=f"Error: {err}")
        except Exception as e:
            result_label.config(text=f"Unexpected error: {e}")

    balance_update_thread = None
    submit_btn = Button(root1, text="SUBMIT", command=submit, font='Times 30 bold', bg='#023047', fg='#ced4da')
    submit_btn.pack(pady=20)

    root1.bind("<Escape>", lambda event: root1.destroy())
    root1.bind("<Return>", lambda event: submit())
    root1.configure(bg="#4cc9f0")

    def process_balance_update(balance_var):
        if not balance_update_queue.empty():
            new_balance = balance_update_queue.get()
            print(f"Updating balance: {new_balance}")
            balance_var.set(f"Current balance: INR {new_balance}")
            root1.update_idletasks()  # Force update the GUI
        root1.after(100, process_balance_update, balance_var)

    process_balance_update(balance_var=tk.StringVar())

    root1.mainloop()

if __name__ == "__main__":
    check_balance()
