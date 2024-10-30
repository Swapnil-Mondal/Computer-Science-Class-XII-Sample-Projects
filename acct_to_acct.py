import tkinter as tk
from tkinter import *
import Database_Connection as dc
from tkinter import messagebox
import mysql.connector

def get_db_connection():
    return dc.con()

def transfer_money():
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    root = Toplevel()
    root.attributes("-fullscreen", True)
    root.title('Account to Account Transfer')
    hed = Label(root, text="Account to Account Transfer", bg="#4361ee",
                fg="#e9ecef", font="Times 60 underline bold")
    hed.pack(fill=X)

    base_frame = Frame(root, bg="#4cc9f0")
    
    from_account_label = Label(base_frame, text="From A/C No:", 
                               bg="#7209b7", fg="#ced4da", font='Times 30 bold', width=11)
    from_account_label.grid(row=0, column=0, padx=(0, 5))
    from_account_entry = Entry(base_frame, font='Times 30 bold',
                               width=12, bg='#7209b7', fg='#ced4da')
    from_account_entry.grid(row=0, column=1)
    
    to_account_label = Label(base_frame, text="To A/C No:", 
                             bg="#7209b7", fg="#ced4da", font='Times 30 bold', width=11)
    to_account_label.grid(row=1, column=0, padx=(0, 5))
    to_account_entry = Entry(base_frame, font='Times 30 bold',
                             width=12, bg='#7209b7', fg='#ced4da')
    to_account_entry.grid(row=1, column=1)
    
    amount_label = Label(base_frame, text="Enter Amount:", 
                         bg="#7209b7", fg="#ced4da", font='Times 30 bold', width=11)
    amount_label.grid(row=2, column=0, padx=(0, 5))
    amount_entry = Entry(base_frame, font='Times 30 bold',
                         width=12, bg='#7209b7', fg='#ced4da')
    amount_entry.grid(row=2, column=1)
    
    base_frame.pack(pady=20, padx=20)
    
    result_label = Label(root, text="", bg="#4cc9f0", fg="#000000", font='Times 30 bold')
    result_label.pack(pady=20)
    
    def submit():
        try:
            from_account_no = from_account_entry.get()
            to_account_no = to_account_entry.get()
            amount = float(amount_entry.get())
            
            # Check if the source account has sufficient balance
            check_balance_query = "SELECT current_balance FROM balance WHERE account_number = %s"
            mycursor.execute(check_balance_query, (from_account_no,))
            from_account_balance = mycursor.fetchone()[0]
            
            if from_account_balance < amount:
                result_label.config(text=f"Error: Insufficient balance in account {from_account_no}")
                return
            
            # Deduct the amount from the source account
            deduct_query = "UPDATE balance SET current_balance = current_balance - %s WHERE account_number = %s"
            mycursor.execute(deduct_query, (amount, from_account_no))
            
            # Add the amount to the destination account
            add_query = "UPDATE balance SET current_balance = current_balance + %s WHERE account_number = %s"
            mycursor.execute(add_query, (amount, to_account_no))
            
            # Record the transactions
            from_transaction_query = "INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, CONCAT('TRANSFER OUT TO ', %s), %s)"
            to_transaction_query = "INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, CONCAT('TRANSFER IN FROM ', %s), %s)"
            mycursor.execute(from_transaction_query, (from_account_no, to_account_no, amount))
            mycursor.execute(to_transaction_query, (to_account_no, from_account_no, amount))
            
            mydb.commit()
            result_label.config(text=f"Amount of INR {amount} transferred successfully from A/C {from_account_no} to A/C {to_account_no}")
        except mysql.connector.Error as err:
            result_label.config(text=f"Error: {err}")
        except Exception as e:
            result_label.config(text=f"Unexpected error: {e}")
        finally:
            if mydb.is_connected():
                mycursor.close()
                mydb.close()
    submit_btn = Button(root, text="Submit", command=submit, font='Times 30 bold', bg='#023047', fg='#ced4da')
    submit_btn.pack(pady=20)

    root.bind("<Escape>", lambda event: root.destroy())
    root.bind("<Return>", lambda event: submit())
    root.configure(bg="#4cc9f0")
    root.mainloop()

if __name__ == "__main__":
    transfer_money()

