import tkinter as tk
from tkinter import *
import mysql.connector
import Database_Connection as dc
import reportlab as rprt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

def get_db_connection():
  return dc.con()

def transaction_history():
  mydb = get_db_connection()
  mycursor = mydb.cursor()

  root = Toplevel()
  root.attributes("-fullscreen", True)
  root.title('Transaction History')

  hed = Label(root, text="Transaction History", bg="#4361ee", fg="#e9ecef", font="Times 60 underline bold")
  hed.pack(fill=X)

  base_frame = Frame(root, bg="#4cc9f0")

  account_number_label = Label(base_frame, text="Enter A/C No:", bg="#7209b7", fg="#ced4da", font='Times 30 bold', width=11)
  account_number_label.grid(row=0, column=0, padx=(0, 5))
  account_number_entry = Entry(base_frame, font='Times 30 bold', width=12, bg='#7209b7', fg='#ced4da')
  account_number_entry.grid(row=0, column=1)

  base_frame.pack(pady=20, padx=20)

  result_label = Label(root, text="", bg="#4cc9f0", fg="#000000", font='Times 30 bold')
  result_label.pack(pady=20)

  def submit():
        try:
            account_no = account_number_entry.get()
            query = "SELECT transaction_date, transaction_type, amount FROM transactions WHERE account_number = %s ORDER BY transaction_date DESC"
            values = (account_no,)
            mycursor.execute(query, values)
            records = mycursor.fetchall()

            if records:
                filename = f"transaction_history_{account_no}.pdf"
                logo = r"F:\DAV Project\Bank Management System\OIP.jpeg"
                # Calculate table data and style
                table_data = [["Date", "Type", "Amount"]]
                for record in records:
                    table_data.append([str(record[0]), record[1], str(record[2])])
                table_style = [
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),  # Header background color
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
                              ]
                table_width = [2.0 * inch, 2.0 * inch, 2.0 * inch]

                # Create a new Canvas with dynamic height
                table = Table(table_data, colWidths=table_width)
                table.setStyle(table_style)
                table_height = table.wrapOn(None, 30, 0)[1]  # Calculate table height
                page_height = 775  # Letter paper height
                pdf = canvas.Canvas(filename, pagesize=(letter[0], page_height + table_height))

                # Add logo, title, etc. (adjust positions as needed)
                pdf.drawImage(logo, 200, 800, width=100, height=100)
                txt = "TRANSACTION HISTORY"
                font_name = "Helvetica-Bold"
                font_size = 16
                txt_width = pdf.stringWidth(txt, font_name, font_size)
                page_width = letter[0]
                x_position = (page_width - txt_width) / 2
                pdf.setFont(font_name, font_size)
                pdf.drawString(x_position, page_height - 25, txt)

                # Draw the table
                table.wrapOn(pdf, x_position - 20, page_height - table_height - 50)  # Adjust y-position as needed
                table.drawOn(pdf, x_position - 20, page_height - table_height - 50)

                pdf.save()

                result_label.config(text=f"Transaction history for account {account_no} downloaded as PDF.")
            else:
                result_label.config(text="No transactions found for this account.")
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

  # Bind the Enter key to the submit button
  root.bind("<Return>", lambda event: submit())

  root.bind("<Escape>", lambda event: root.destroy())
  root.configure(bg="#4cc9f0")
  root.mainloop()

if __name__ == "__main__":
  transaction_history()
