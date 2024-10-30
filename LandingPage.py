import tkinter as tk
from tkinter import *
from tkinter import ttk
import tkinter.font as tf
import time

# Import other modules (replace with actual paths)
import User_account as ua
import Delete_account as da
import SearchAccount as sa
import User_account as Update_ac
import Deposit_Money as dm
import Withdraw_Money as wm
import Check_Balance as cb
import Transaction_History as th
import Loan_Details as ld
import Loan as loan
import Fixed_Deposit as fd
import Reccuring_Deposit as rd
import acct_to_acct as ata

# Initialize the theme
root = Tk()
root.attributes("-fullscreen", True)
root.title('Bank Management System')
style = ttk.Style()
style.theme_use('clam')  # Choose your desired theme here (e.g., 'vista', 'alt')

# Heading Configurations (using ttk.Label for theme consistency)
hed = ttk.Label(root, text="Dayanand Anglo-Vedic Banking Trust", background="#4361ee", foreground="#e9ecef", font="Times 50 underline bold italic", anchor=CENTER)
hed.pack(fill=X)

# Bank details Heading Configurations
instruction = ttk.Label(root, text="BANK DETAILS:", background="#7209b7", foreground="#ced4da", font="Times 25 bold", anchor=NW, padding=15)
instruction.pack(pady=(20, 8), padx=100, fill=X)

fontstyle = tf.Font(family="Times", size=20, weight="bold")
instruction_Message = ttk.Label(root, text="""
    Branch Name:        Durgapur, West Bengal (713205)  
    IFSC:                      DVBT0123456
    Customer Care:     +91 82500 26376
    Working Hours:     10:00 AM - 06:00 PM
    Press "Escape(Esc)" Key to Exit.""", background="green", foreground="#000000", font=fontstyle, justify=LEFT, anchor=NW, padding=(30, 10))
instruction_Message.pack(pady=0, padx=100, fill=X)

services = ttk.Label(root, text="SERVICES:", background="#7209b7", foreground="#ced4da", font="Times 25 bold", anchor=NW, padding=15)
services.pack(pady=(20, 1), padx=100, fill=X)

# Create a scrollable frame with theme applied
scrollable_frame = ttk.Frame(root, style='.TFrame')
scrollable_frame.pack(pady=(20, 1), padx=100, fill=X)

# Create a canvas to hold the scrollable content
canvas = Canvas(scrollable_frame, bg="#4cc9f0")
canvas.pack(side="left", fill=X, expand=True)

# Create a scrollbar
style.configure("Vertical.TScrollbar", background="#4cc9f0", troughcolor="#7209b7")
scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Create a frame to hold the buttons
button_frame = Frame(canvas, bg="#4cc9f0", width=400)
canvas.create_window((0, 0), window=button_frame, anchor="nw")

style.configure("TButton", font=("Arial", 12), padding=10, background="#4CAF50")  # Adjust font, padding, and background color
style.configure("TLabel", font=("Arial", 12), padding=10, background="#f0f0f0")  # Adjust font and background color (optional)

# Button grid layout
button_grid = {
    (0, 0): "Create Account",
    (0, 1): "Delete Account",
    (1, 0): "Search Account",
    (1, 1): "Update Account",
    (2, 0): "Deposit Money",
    (2, 1): "Withdraw Money",
    (3, 0): "Check Balance",
    (3, 1): "Download Transactions",
    (4, 0): "Apply for Loan",
    (4, 1): "Loan Details",
    (5, 0): "Fixed Deposit",
    (5, 1): "Recurring Deposit",
    (6, 0): "Send Money"
}

# Button configuration
button_config = {
    "bg": "green",
    "fg": "black",
    "font": ("Times", 20, "bold"),
    "activebackground": "lightgreen",
    "activeforeground": "black",
    "width": 34,
    "height": 1,
    "highlightthickness": 0,
    "borderwidth": 0
}

for row in range(7):
    for col in range(2):
        button_text = button_grid.get((row, col), None)
        if button_text:
            button = Button(button_frame, text=button_text, **button_config, command=lambda row=row, col=col: handle_button_click(row, col))
            button.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

def handle_button_click(row, col):
    if row == 0 and col == 0:
        ua.call_function()
    elif row == 0 and col == 1:
        da.call_delete_user_account()
    elif row == 1 and col == 0:
        sa.call_search_user_account()
    elif row == 1 and col == 1:
        Update_ac.call_update_user_account()
    elif row == 2 and col == 0:
        dm.deposit_money()
    elif row == 2 and col == 1:
        wm.withdraw_money()
    elif row == 3 and col == 0:
        cb.check_balance()
    elif row == 3 and col == 1:
        th.transaction_history()
    elif row == 4 and col == 0:
        loan.loan_interface()
    elif row == 4 and col == 1:
        ld.show_loan_details()
    elif row == 5 and col == 0:
        fd.fd_interface()
    elif row == 5 and col == 1:
        rd.rd_interface()
    elif row == 6 and col == 0:
        ata.transfer_money()

root.bind("<Escape>", lambda event: root.destroy())
root.configure(bg="#4cc9f0")
root.mainloop()
