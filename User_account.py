import tkinter as tk
import random
import mysql.connector
from tkinter import *
from tkinter import messagebox
import Database_Connection as dc

def get_db_connection():
    return dc.con()

def create_user_account():
    query1 = "INSERT INTO user_account VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
    query2 = "INSERT INTO balance VALUES(%s, 0, %s)"
    mydb = get_db_connection()
    mycursor = mydb.cursor()

    root = Tk()
    root.attributes("-fullscreen", True)
    root.title('Create User Account')

    hed = Label(root, text="Create User Account", bg="#4361ee",
                fg="#e9ecef", font="Times 60 underline bold")
    hed.pack(fill=X)

    base_frame = Frame(root, bg="#4cc9f0")

    name_label = Label(base_frame, text="Name:", bg="#023047",
                    fg="#ced4da", font='Times 30 bold', width=12)
    name_label.grid(row=0, column=0, padx=5, pady=(5, 30))
    name_entry = Entry(base_frame, font='Times 30 bold',
                    width=10, bg='#023047', fg='#ced4da')
    name_entry.grid(row=0, column=1, padx=(0, 100), pady=(5, 30))

    Address_label = Label(base_frame, text="Address:",
                        bg="#023047", fg="#ced4da", font='Times 30 bold', width=11)
    Address_label.grid(row=0, column=2, padx=(100, 5), pady=(5, 30))
    Address_entry = Entry(base_frame, font='Times 30 bold',
                        width=10, bg='#023047', fg='#ced4da')
    Address_entry.grid(row=0, column=3, pady=(5, 30), padx=(0, 5))

    dob_label = Label(base_frame, text="DOB (YYYY-MM-DD):",
                    bg="#023047", fg="#ced4da", font='Times 30 bold')
    dob_label.grid(row=1, column=0, padx=5, pady=(5, 30))
    dob_entry = Entry(base_frame, font='Times 30 bold',
                    width=10, bg='#023047', fg='#ced4da')
    dob_entry.grid(row=1, column=1, padx=(0, 100), pady=(5, 30))

    Contact_label = Label(base_frame, text="Contact:", bg="#023047",
                        fg="#ced4da", font='Times 30 bold', width=12)
    Contact_label.grid(row=1, column=2, padx=(100, 5), pady=(5, 30))
    Contact_entry = Entry(base_frame, font='Times 30 bold',
                        width=10, bg='#023047', fg='#ced4da')
    Contact_entry.grid(row=1, column=3, padx=(0, 5), pady=(5, 30))

    Aadhar_label = Label(base_frame, text="Aadhar:",
                        bg="#023047", fg="#ced4da", font='Times 30 bold', width=11)
    Aadhar_label.grid(row=2, column=0, padx=5, pady=(5, 30))
    Aadhar_entry = Entry(base_frame, font='Times 30 bold',
                        width=10, bg='#023047', fg='#ced4da')
    Aadhar_entry.grid(row=2, column=1, pady=(5, 30), padx=(0, 100))
    gender_options = ["Male", "Female", "Other"]
    gender_variable = StringVar(root)
    gender_variable.set(gender_options[0])  # Default value

    gender_label = Label(base_frame, text="Gender:", bg="#023047", fg="#ced4da", font='Times 30 bold', width=12)
    gender_label.grid(row=2, column=2, padx=(100, 5), pady=(5, 30))
    gender_dropdown = OptionMenu(base_frame, gender_variable, *gender_options)
    gender_dropdown.config(width=10, font='Times 30 bold', bg='#023047', fg='#ced4da')
    gender_dropdown.grid(row=2, column=3, padx=(0, 5), pady=(5, 30))

    account_type_options = ["Savings (7%)", "Current (2%)"]
    account_type_variable = StringVar(root)
    account_type_variable.set(account_type_options[0])  # Default value

    account_type_label = Label(base_frame, text="Account Type:", bg="#023047", fg="#ced4da", font='Times 30 bold', width=11)
    account_type_label.grid(row=3, column=0, padx=5, pady=(5, 30))
    account_type_dropdown = OptionMenu(base_frame, account_type_variable, *account_type_options)
    account_type_dropdown.config(width=10, font='Times 30 bold', bg='#023047', fg='#ced4da')
    account_type_dropdown.grid(row=3, column=1, pady=(5, 30), padx=(0, 100))
    def generate_unique_account_number(mydb, mycursor):
        while True:
            account_number = str(random.randint(100000000, 999999999))

            # Check if the account number already exists
            check_query = "SELECT COUNT(*) FROM user_account WHERE account_number = %s"
            mycursor.execute(check_query, (account_number,))
            count = mycursor.fetchone()[0]

            if count == 0:
                return account_number
    
    def fetch_value():
        name = name_entry.get()
        account_no = generate_unique_account_number(mydb, mycursor)
        address = Address_entry.get()
        dob = dob_entry.get()
        contact = Contact_entry.get()
        aadhar = Aadhar_entry.get()
        gender = gender_variable.get()
        account_type = account_type_variable.get()
        def interest():
            int_rate=0
            if account_type=="Savings (7%)":
                int_rate=7.0
            if account_type=="Current (2%)":
                int_rate=2.0
            return int_rate
        interest=interest()
        # Validate input fields
        if not name or not address or not dob or not contact or not aadhar or not gender or not account_type:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        try:
            # Validate contact and Aadhar numbers
            if len(contact) != 13 or len(aadhar) != 12:
                messagebox.showerror("Error", "Invalid contact or Aadhar number.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid contact or Aadhar number.")
            return

        data1 = (name, account_no, gender, aadhar, dob, address, account_type, contact)
        data2 = (account_no, interest)

        try:
            mycursor.execute(query1, data1)
            mycursor.execute(query2, data2)
            mydb.commit()
            messagebox.showinfo("Success", f"Account created successfully!\n Your account number is: {account_no}")
            root.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", "Database error: " + str(err))

    base_frame.pack(pady=(65, 50))

    submit = Button(root,
                    bg="#4361ee", fg="#e9ecef",
                    text='Create Account',
                    anchor=CENTER,
                    font='Times 25 bold',
                    justify=CENTER,
                    activebackground="#e9ecef",
                    activeforeground="#4361ee",
                    height=2,
                    bd=5,
                    width=25,
                    command=fetch_value
                    )
    submit.pack()

    root.bind("<Escape>", lambda event: root.destroy())
    root.bind("<Return>", lambda event: fetch_value())
    root.configure(bg="#4cc9f0")
    mainloop()

def call_function():
    create_user_account()
