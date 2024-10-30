import tkinter as tk
from tkinter import ttk, Scrollbar, messagebox
import Database_Connection as dc
from mysql.connector import Error

def get_db_connection():
    return dc.con()

def fetch_loan_by_account_number(account_number):
    mydb = get_db_connection()
    mycursor = mydb.cursor()
    query = "SELECT account_number, amount, term, interest_rate, start_date, end_date, final_pay, installment_period, installment_amt, remaining_amt FROM loans WHERE account_number = %s"

    try:
        mycursor.execute(query, (account_number,))
        result = mycursor.fetchone()
        return result

    except Error as err:
        messagebox.showerror("Error", "Database error: " + str(err))
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

def show_loan_details():
    root = tk.Tk()
    root.title('Loan Details')

    account_number_label = tk.Label(root, text="Enter Account Number:")
    account_number_label.pack(pady=10)

    account_number_entry = tk.Entry(root)
    account_number_entry.pack(pady=10)

    def search_loan():
        account_number = account_number_entry.get()
        loan_details = fetch_loan_by_account_number(account_number)

        if loan_details:
            # Clear the Treeview if it already has data
            loan_details_tree.delete(*loan_details_tree.get_children())

            # Insert the fetched loan details into the Treeview
            loan_details_tree.insert("", tk.END, values=loan_details)
        else:
            messagebox.showinfo("No Loan Found", "No loan found for the given account number.")

    search_button = tk.Button(root, text="Search", command=search_loan)
    search_button.pack(pady=10)

    # Create scrollbars
    vscrollbar = Scrollbar(root, orient="vertical")
    vscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    hscrollbar = Scrollbar(root, orient="horizontal")
    hscrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # Create Treeview with scrollbars
    loan_details_tree = ttk.Treeview(root, columns=("account_no", "amount", "term", "interest_rate", "start_date", "end_date", "final_pay", "installment_period", "installment_amt", "remaining_amt"), show="headings", yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)
    loan_details_tree.heading("#0", text="Account No.")
    loan_details_tree.heading("account_no", text="Account No.")
    loan_details_tree.heading("amount", text="Amount")
    loan_details_tree.heading("term", text="Term (Years)")
    loan_details_tree.heading("interest_rate", text="Interest Rate (%)")
    loan_details_tree.heading("start_date", text="Start Date")
    loan_details_tree.heading("end_date", text="End Date")
    loan_details_tree.heading("final_pay", text="Final Payment")
    loan_details_tree.heading("installment_period", text="Installment Period (Months)")
    loan_details_tree.heading("installment_amt", text="Installment Amount")
    loan_details_tree.heading("remaining_amt", text="Remaining Amount")

    # Configure scrollbars
    vscrollbar.config(command=loan_details_tree.yview)
    hscrollbar.config(command=loan_details_tree.xview)

    # Adjust column widths as needed
    loan_details_tree.column("#0", width=100)
    loan_details_tree.column("account_no", width=100)
    loan_details_tree.column("amount", width=100)
    loan_details_tree.column("term", width=50)
    loan_details_tree.column("interest_rate", width=80)
    loan_details_tree.column("start_date", width=100)
    loan_details_tree.column("end_date", width=100)
    loan_details_tree.column("final_pay", width=100)
    loan_details_tree.column("installment_period", width=120)
    loan_details_tree.column("installment_amt", width=120)
    loan_details_tree.column("remaining_amt", width=120)

    loan_details_tree.pack(fill=tk.BOTH, expand=True)

    root.mainloop()

if __name__ == "__main__":
    show_loan_details()
