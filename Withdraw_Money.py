import tkinter as tk
import mysql.connector
from tkinter import *
import Database_Connection as dc

def get_db_connection():
    return dc.con()

def withdraw_money():
    mydb = get_db_connection()

    mycursor = mydb.cursor()

    root = Toplevel()
    root.attributes("-fullscreen", True)
    root.title('Withdraw Money')

    hed = Label(root, text="Withdraw Money", bg="#4361ee",
                fg="#e9ecef", font="Times 60 underline bold")
    hed.pack(fill=X)

    base_frame = Frame(root, bg="#4cc9f0")

    account_number_label = Label(base_frame, text="Enter A/C No:",
                                 bg="#7209b7", fg="#ced4da", font='Times 30 bold', width=11)
    account_number_label.grid(row=0, column=0, padx=(0, 5))

    account_number_entry = Entry(base_frame, font='Times 30 bold',
                                 width=12, bg='#7209b7', fg='#ced4da')
    account_number_entry.grid(row=0, column=1)

    amount_label = Label(base_frame, text="Enter Amount:",
                         bg="#7209b7", fg="#ced4da", font='Times 30 bold', width=11)
    amount_label.grid(row=1, column=0, padx=(0, 5))

    amount_entry = Entry(base_frame, font='Times 30 bold',
                         width=12, bg='#7209b7', fg='#ced4da')
    amount_entry.grid(row=1, column=1)

    base_frame.pack(pady=20, padx=20)

    result_label = Label(root, text="", bg="#4cc9f0", fg="#000000", font='Times 30 bold')
    result_label.pack(pady=20)

    def submit():
        try:
            account_no = account_number_entry.get()
            amount = float(amount_entry.get())

            query = "SELECT current_balance FROM balance WHERE account_number = %s"
            mycursor.execute(query, (account_no,))
            balance = mycursor.fetchone()[0]

            if balance >= amount:
                query = "UPDATE balance SET current_balance = current_balance - %s WHERE account_number = %s"
                values = (amount, account_no)
                transaction_query = "INSERT INTO transactions (account_number, transaction_type, amount) VALUES (%s, 'WITHDRAWAL', %s)"
                transaction_values = (account_no, amount)
                mycursor.execute(transaction_query, transaction_values)
                mydb.commit()
                mydb.commit()
                mycursor.execute(query, values)
                mydb.commit()
                result_label.config(text=f"Amount {amount} withdrawn successfully")
            else:
                result_label.config(text="Insufficient balance")
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
    withdraw_money()
