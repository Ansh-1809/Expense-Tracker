import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import csv

# ---------- LOGIN WINDOW ----------

def register():
    username = entry_username.get()
    password = entry_password.get()

    if username == "" or password == "":
        messagebox.showerror("Error", "All fields are required!")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Success", "Registration Successful!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")
    finally:
        conn.close()
# 
def login():
    username = entry_username.get()
    password = entry_password.get()

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        messagebox.showinfo("Success", f"Welcome {username}!")
        login_window.destroy()
        open_expense_tracker()
    else:
        messagebox.showerror("Error", "Invalid username or password.")

# ---------- EXPENSE TRACKER WINDOW ----------

# Store transactions globally
transactions = [] 

def open_expense_tracker():
    tracker = tk.Tk()
    tracker.title("Expense Tracker")
    tracker.geometry("600x500")

    # Load previous transactions from CSV
    def load_from_csv():
        try:
            with open('transactions.csv', mode='r') as file:
                reader = csv.DictReader(file)
                global transactions
                transactions = [row for row in reader]
                update_transaction_listbox()
        except FileNotFoundError:
            pass

    # Save transactions to CSV
    def save_to_csv():
        with open('transactions.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["date", "description", "amount", "category"])
            writer.writeheader()
            writer.writerows(transactions)

    # Add new transaction
    def add_transaction():
        date = simpledialog.askstring("Input", "Enter date (YYYY-MM-DD):", parent=tracker)
        description = simpledialog.askstring("Input", "Enter description:", parent=tracker)
        try:
            amount = float(simpledialog.askstring("Input", "Enter amount:", parent=tracker))
        except (ValueError, TypeError):
            messagebox.showerror("Invalid input", "Amount must be a number.")
            return
        category = simpledialog.askstring("Input", "Enter category:", parent=tracker)

        if not (date and description and category):
            messagebox.showerror("Error", "All fields are required.")
            return

        transaction = {"date": date, "description": description, "amount": amount, "category": category}
        transactions.append(transaction)
        save_to_csv()
        update_transaction_listbox()

    # Update the Listbox with transactions
    def update_transaction_listbox():
        listbox.delete(0, tk.END)  # Clear existing list
        for t in transactions:
            listbox.insert(tk.END, f"{t['date']} | {t['description']} | {t['amount']} | {t['category']}")

    # Sort transactions by a chosen criterion
    def sort_transactions(criteria):
        if criteria == "date":
            sorted_transactions = sorted(transactions, key=lambda x: x["date"])
        elif criteria == "amount":
            sorted_transactions = sorted(transactions, key=lambda x: float(x["amount"]))
        elif criteria == "category":
            sorted_transactions = sorted(transactions, key=lambda x: x["category"])
        else:
            sorted_transactions = transactions
        return sorted_transactions

    # Show sorted transactions in the listbox
    def sort_and_update():
        sort_criteria = sort_criteria_var.get()
        sorted_transactions = sort_transactions(sort_criteria)
        global transactions
        transactions = sorted_transactions
        update_transaction_listbox()

    # Main frame
    frame = tk.Frame(tracker)
    frame.pack(pady=10)

    # Add and Sort Buttons
    add_button = tk.Button(frame, text="Add Transaction", command=add_transaction)
    add_button.grid(row=0, column=0, padx=10)

    sort_label = tk.Label(frame, text="Sort by:")
    sort_label.grid(row=0, column=1, padx=5)

    sort_criteria_var = tk.StringVar(value="date")
    sort_date_button = tk.Radiobutton(frame, text="Date", variable=sort_criteria_var, value="date", command=sort_and_update)
    sort_date_button.grid(row=0, column=2, padx=5)

    sort_amount_button = tk.Radiobutton(frame, text="Amount", variable=sort_criteria_var, value="amount", command=sort_and_update)
    sort_amount_button.grid(row=0, column=3, padx=5)

    sort_category_button = tk.Radiobutton(frame, text="Category", variable=sort_criteria_var, value="category", command=sort_and_update)
    sort_category_button.grid(row=0, column=4, padx=5)

    # Listbox to display transactions
    listbox = tk.Listbox(tracker, width=70, height=20)
    listbox.pack(pady=10)

    # Load existing transactions
    load_from_csv()

    tracker.mainloop()

# ---------- MAIN LOGIN WINDOW ----------

login_window = tk.Tk()
login_window.title("Login Page")
login_window.geometry("300x250")

# Username and Password Labels and Entries
label_username = tk.Label(login_window, text="Username")
label_username.pack(pady=5)
entry_username = tk.Entry(login_window)
entry_username.pack(pady=5)

label_password = tk.Label(login_window, text="Password")
label_password.pack(pady=5)
entry_password = tk.Entry(login_window, show="*")
entry_password.pack(pady=5)

# Login and Register Buttons
button_login = tk.Button(login_window, text="Login", command=login)
button_login.pack(pady=10)

button_register = tk.Button(login_window, text="Register", command=register)
button_register.pack(pady=5)

login_window.mainloop()
