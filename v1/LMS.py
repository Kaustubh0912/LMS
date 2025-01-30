import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from datetime import datetime, timedelta

class LibraryManagementSystem:
    def __init__(self):
        self.db = self.connect_to_database()
        self.cursor = self.db.cursor()
        self.create_tables()
        self.login_page()

    def connect_to_database(self):
        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="K@ustubh0912",
                database="library"
            )
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            raise

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Library (
                BK_NAME VARCHAR(255),
                BK_ID VARCHAR(255) PRIMARY KEY,
                AUTHOR_NAME VARCHAR(255),
                BK_STATUS VARCHAR(255),
                CARD_ID VARCHAR(255),
                COURSE_CODE VARCHAR(255),
                TIMESTAMP DATETIME,
                RETURN_DATE DATETIME
            )
        ''')
        self.db.commit()

    def login_page(self):
        self.log_pg = tk.Tk()
        self.log_pg.geometry("1280x720")
        self.log_pg.configure(bg="LightBlue")
        self.log_pg.title("Login")

        lblTitle = tk.Label(self.log_pg, text="Login Page", font=("arial", 50, "bold"), fg="black", bg="LightBlue")
        lblTitle.pack()

        bordercolor = tk.Frame(self.log_pg, bg="black", width=800, height=400)
        bordercolor.pack()

        mainframe = tk.Frame(bordercolor, bg="#1a75ff", width=800, height=400)
        mainframe.pack(padx=20, pady=20)

        tk.Label(mainframe, text="Username", font=("arial", 30, "bold"), bg="#1a75ff").place(x=100, y=50)
        tk.Label(mainframe, text="Password", font=("arial", 30, "bold"), bg="#1a75ff").place(x=100, y=150)

        self.entry_username = tk.Entry(mainframe, width=12, bd=2, font=("arial", 30))
        self.entry_username.place(x=400, y=50)
        self.entry_password = tk.Entry(mainframe, width=12, bd=2, font=("arial", 30), show="*")
        self.entry_password.place(x=400, y=150)

        login_btn = tk.Button(mainframe, text="LOGIN", font="arial", bg="LightBlue", width=30, command=self.login)
        login_btn.place(x=250, y=250)
        self.log_pg.mainloop()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        try:
            self.cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            admin_data = self.cursor.fetchone()
            self.cursor.execute("SELECT * FROM students WHERE username = %s", (username,))
            student_data = self.cursor.fetchone()

            if admin_data and password == admin_data[2]:
                messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
                self.log_pg.destroy()
                self.admin_panel()
            elif student_data and password == student_data[2]:
                messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
                self.log_pg.destroy()
                self.student_page()
            else:
                messagebox.showerror("Login Failed", "Incorrect username or password")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def admin_panel(self):
        self.root = tk.Tk()
        self.root.title('Library Management System - Admin Panel')
        self.root.geometry('1280x720')

        self.setup_ui()
        self.root.mainloop()

    def student_page(self):
        self.root = tk.Tk()
        self.root.title('Library Management System - Student Panel')
        self.root.geometry('1280x720')

        self.setup_ui(is_student=True)
        self.root.mainloop()

    def setup_ui(self, is_student=False):
        # Frames
        left_frame = tk.Frame(self.root, bg='SkyBlue')
        left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

        RT_frame = tk.Frame(self.root, bg='#0099ff')
        RT_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)

        RB_frame = tk.Frame(self.root, bg='LightSkyBlue')
        RB_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

        # StringVars
        self.bk_status = tk.StringVar(value='Available')
        self.bk_name = tk.StringVar()
        self.bk_id = tk.StringVar()
        self.author_name = tk.StringVar()
        self.card_id = tk.StringVar()
        self.course_code = tk.StringVar()
        self.search_entry = tk.StringVar()

        # Left Frame - Input Fields
        tk.Label(left_frame, text='Book Name', bg='SkyBlue', font=('Georgia', 13)).place(x=150, y=25)
        tk.Entry(left_frame, width=25, font=('Times New Roman', 12), textvariable=self.bk_name).place(x=90, y=55)

        tk.Label(left_frame, text='Book ID', bg='SkyBlue', font=('Georgia', 13)).place(x=165, y=105)
        tk.Entry(left_frame, width=25, font=('Times New Roman', 12), textvariable=self.bk_id).place(x=90, y=135)

        tk.Label(left_frame, text='Author Name', bg='SkyBlue', font=('Georgia', 13)).place(x=145, y=185)
        tk.Entry(left_frame, width=25, font=('Times New Roman', 12), textvariable=self.author_name).place(x=90, y=215)

        tk.Label(left_frame, text='Course Code', bg='SkyBlue', font=('Georgia', 13)).place(x=145, y=265)
        tk.Entry(left_frame, width=25, font=('Times New Roman', 12), textvariable=self.course_code).place(x=90, y=295)

        tk.Label(left_frame, text='Status of the Book', bg='SkyBlue', font=('Georgia', 13)).place(x=125, y=335)
        tk.OptionMenu(left_frame, self.bk_status, 'Available', 'Issued').place(x=125, y=370)

        # Buttons
        tk.Button(left_frame, text='Add new record', font=('Gill Sans MT', 13), bg='#6699ff', width=20, command=self.add_record).place(x=90, y=435)
        tk.Button(left_frame, text='Clear fields', font=('Gill Sans MT', 13), bg='#6699ff', width=20, command=self.clear_fields).place(x=90, y=495)

        if not is_student:
            tk.Button(RT_frame, text='Delete book record', font=('Gill Sans MT', 13), bg='#6699ff', width=17, command=self.remove_record).place(x=8, y=30)
            tk.Button(RT_frame, text='Delete full inventory', font=('Gill Sans MT', 13), bg='#6699ff', width=17, command=self.delete_inventory).place(x=178, y=30)
            tk.Button(RT_frame, text='Change Book Availability', font=('Gill Sans MT', 13), bg='#6699ff', width=19, command=self.change_availability).place(x=348, y=30)
            tk.Button(RT_frame, text='Issued Books', font=('Gill Sans MT', 13), bg='#6699ff', width=19, command=self.issued_books).place(x=538, y=30)

        # Search Bar
        tk.Label(RT_frame, text='Search Books:', font=('Georgia', 13), bg='#0099ff').place(x=430, y=100)
        tk.Entry(RT_frame, width=30, font=('Times New Roman', 12), textvariable=self.search_entry).place(x=550, y=100)
        tk.Button(RT_frame, text='Search', font=('Gill Sans MT', 10), bg='#6699ff', width=10, command=self.search_books).place(x=800, y=101)

        # Treeview
        self.tree = ttk.Treeview(RB_frame, selectmode='browse', columns=('Book Name', 'Book ID', 'Author', 'Status', 'Issuer Card ID', 'Course Code', 'Time', 'Return'))
        self.tree.heading('Book Name', text='Book Name', anchor='center')
        self.tree.heading('Book ID', text='Book ID', anchor='center')
        self.tree.heading('Author', text='Author', anchor='center')
        self.tree.heading('Status', text='Status', anchor='center')
        self.tree.heading('Issuer Card ID', text='Issuer Card ID', anchor='center')
        self.tree.heading('Course Code', text='Course Code', anchor='center')
        self.tree.heading('Time', text='Time', anchor='center')
        self.tree.heading('Return', text='Return', anchor='center')

        self.tree.column('#0', width=0, stretch='no')
        self.tree.column('#1', width=225, stretch='no')
        self.tree.column('#2', width=70, stretch='no')
        self.tree.column('#3', width=150, stretch='no')
        self.tree.column('#4', width=105, stretch='no')
        self.tree.column('#5', width=132, stretch='no')
        self.tree.column('#6', width=130, stretch='no')
        self.tree.column('#7', width=120, stretch='no')
        self.tree.column('#8', width=0, stretch='no')

        self.tree.place(y=30, x=0, relheight=0.9, relwidth=1)

        # Display records
        self.display_records()

    def add_record(self):
        if self.bk_status.get() == 'Issued':
            self.card_id.set(self.issuer_card())
        else:
            self.card_id.set('N/A')

        surety = messagebox.askyesno('Are you sure?', 'Are you sure this is the data you want to enter?')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if surety:
            try:
                self.cursor.execute(
                    'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID, COURSE_CODE, TIMESTAMP, RETURN_DATE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (self.bk_name.get(), self.bk_id.get(), self.author_name.get(), self.bk_status.get(), self.card_id.get(), self.course_code.get(), current_time, current_time)
                )
                self.db.commit()
                self.clear_and_display()
                messagebox.showinfo('Record added', 'The new record was successfully added to your database')
            except mysql.connector.IntegrityError:
                messagebox.showerror('Book ID already in use!', 'The Book ID you are trying to enter is already in the database')

    def remove_record(self):
        if not self.tree.selection():
            messagebox.showerror('Error!', 'Please select an item from the database')
            return

        current_item = self.tree.focus()
        values = self.tree.item(current_item)
        selection = values["values"]
        self.cursor.execute('DELETE FROM Library WHERE BK_ID=%s', (selection[1],))
        self.db.commit()
        self.tree.delete(current_item)
        messagebox.showinfo('Done', 'The record you wanted deleted was successfully deleted.')
        self.clear_and_display()

    def delete_inventory(self):
        if messagebox.askyesno('Are you sure?', 'Are you sure you want to delete the entire inventory?'):
            self.tree.delete(*self.tree.get_children())
            self.cursor.execute('DELETE FROM Library')
            self.db.commit()

    def change_availability(self):
        if not self.tree.selection():
            messagebox.showerror('Error!', 'Please select a book from the database')
            return

        current_item = self.tree.focus()
        values = self.tree.item(current_item)
        BK_id = values['values'][1]
        BK_status = values["values"][3]

        if BK_status == 'Issued':
            surety = messagebox.askyesno('Is return confirmed?', 'Has the book been returned to you?')
            if surety:
                return_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.cursor.execute('UPDATE Library SET BK_STATUS=%s, CARD_ID=%s, TIMESTAMP=%s, RETURN_DATE=%s WHERE BK_ID=%s', ('Available', 'N/A', return_time, None, BK_id))
                self.db.commit()
            else:
                messagebox.showinfo('Cannot be returned', 'The book status cannot be set to Available unless it has been returned')
        else:
            issue_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            issue_card = self.issuer_card()
            if issue_card is not None:
                return_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
                self.cursor.execute('UPDATE Library SET BK_STATUS=%s, CARD_ID=%s, TIMESTAMP=%s, RETURN_DATE=%s WHERE BK_ID=%s', ('Issued', issue_card, issue_time, return_date, BK_id))
                self.db.commit()
        self.clear_and_display()

    def search_books(self):
        search_keyword = self.search_entry.get()
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute(
            "SELECT * FROM Library WHERE BK_NAME LIKE %s OR BK_ID LIKE %s OR AUTHOR_NAME LIKE %s OR COURSE_CODE LIKE %s",
            (f"%{search_keyword}%", f"%{search_keyword}%", f"%{search_keyword}%", f"%{search_keyword}%")
        )
        data = self.cursor.fetchall()
        for records in data:
            self.tree.insert('', 'end', values=records)

    def issued_books(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute("SELECT * FROM Library WHERE BK_STATUS LIKE %s", ('Issued',))
        data = self.cursor.fetchall()
        for records in data:
            self.tree.insert('', 'end', values=records)

    def clear_fields(self):
        self.bk_status.set('Available')
        self.bk_id.set('')
        self.bk_name.set('')
        self.author_name.set('')
        self.card_id.set('')
        self.course_code.set('')
        try:
            selected_item = self.tree.selection()[0]
            self.tree.selection_remove(selected_item)
        except IndexError:
            pass

    def clear_and_display(self):
        self.clear_fields()
        self.display_records()

    def display_records(self):
        self.tree.delete(*self.tree.get_children())
        self.cursor.execute('SELECT * FROM Library')
        data = self.cursor.fetchall()
        for records in data:
            self.tree.insert('', 'end', values=records)

    def issuer_card(self):
        Cid = simpledialog.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?')
        if not Cid:
            messagebox.showerror('Issuer ID cannot be empty!', 'Can\'t keep Issuer ID empty, it must have a value')
        else:
            return Cid

if __name__ == "__main__":
    app = LibraryManagementSystem()