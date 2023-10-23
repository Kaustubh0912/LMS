import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector
from datetime import *

global cursor, tree, bk_status, bk_name, bk_id, author_name, card_id, search_entry, db, course_code, username,show_extra_columns, lable_var
buttons=[]

def login():
    global username 
    username = entry_username.get()
    password = entry_password.get()

    try:
        # Connect to the MySQL database
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="K@ustubh0912",
            database="library"
        )

        cursor = db.cursor()

        # Execute a query to fetch user data based on the entered username
        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        admin_data = cursor.fetchone()
        cursor.execute("SELECT * FROM students WHERE username = %s", (username,))
        student_data = cursor.fetchone()

        if admin_data:
            if password == admin_data[2]:
                messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
                log_pg.destroy()
                admin_panel()
            else:
                messagebox.showerror("Login Failed", "Incorrect password")
        elif student_data:
            if password == student_data[2]:
                messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
                log_pg.destroy()
                student_page()
            else:
                messagebox.showerror("Login Failed", "Incorrect password")
        else:
            messagebox.showerror("Login Failed", "User not found")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

def issuer_card():
    # Function to get issuer's card ID
    Cid = simpledialog.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?\t\t\t')

    if not Cid:
        messagebox.showerror('Issuer ID cannot be empty!', 'Can\'t keep Issuer ID empty, it must have a value')
    else:
        return Cid

def display_records():
    # Function to display records in the treeview
    global cursor, tree
    tree.delete(*tree.get_children())
    cursor.execute('SELECT * FROM Library')
    data = cursor.fetchall()
    for records in data:
        tree.insert('', 'end', values=records)

def clear_fields():
    # Function to clear input fields
    global bk_status, bk_id, bk_name, author_name, card_id,course_code
    bk_status.set('Available')
    bk_id.set('')
    bk_name.set('')
    author_name.set('')
    card_id.set('')
    course_code.set('')
    try:
        selected_item = tree.selection()[0]
        tree.selection_remove(selected_item)
    except IndexError:
        pass

def clear_and_display():
    clear_fields()
    display_records()

def add_record():
    # Function to add a record
    global bk_name, bk_id, author_name, bk_status, card_id, db, course_code
    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
    else:
        card_id.set('N/A')
    surety = messagebox.askyesno('Are you sure?', 'Are you sure this is the data you want to enter?\nPlease note that Book ID cannot be changed in the future')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if surety:
        try:
            cursor.execute(
                'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID, COURSE_CODE, TIMESTAMP, RETURN_DATE) VALUES (%s, %s, %s, %s, %s,%s,%s,%s)',
                (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get(), course_code.get(), current_time, current_time))
            db.commit()
            clear_and_display()
            messagebox.showinfo('Record added', 'The new record was successfully added to your database')
        except mysql.connector.IntegrityError:
            messagebox.showerror('Book ID already in use!', 'The Book ID you are trying to enter is already in the database, please alter that book\'s record or check any discrepancies on your side')

def remove_record():
    # Function to remove a record
    if not tree.selection():
        messagebox.showerror('Error!', 'Please select an item from the database')
        return
    current_item = tree.focus()
    values = tree.item(current_item)
    selection = values["values"]
    cursor.execute('DELETE FROM Library WHERE BK_ID=%s', (selection[1],))
    db.commit()
    tree.delete(current_item)
    messagebox.showinfo('Done', 'The record you wanted deleted was successfully deleted.')
    clear_and_display()

def delete_inventory():
    # Function to delete the entire inventory
    if messagebox.askyesno('Are you sure?', 'Are you sure you want to delete the entire inventory?\n\nThis command cannot be reversed'):
        tree.delete(*tree.get_children())
    cursor.execute('DELETE FROM Library')
    db.commit()

def change_availability():
    global card_id, tree, cursor, db

    if not tree.selection():
        messagebox.showerror('Error!', 'Please select a book from the database')
        return

    current_item = tree.focus()
    values = tree.item(current_item)
    BK_id = values['values'][1]
    BK_status = values["values"][3]

    if BK_status == 'Issued':
        surety = messagebox.askyesno('Is return confirmed?', 'Has the book been returned to you?')
        if surety:
            return_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('UPDATE Library SET BK_STATUS=%s, CARD_ID=%s, TIMESTAMP=%s, RETURN_DATE=%s WHERE BK_ID=%s', ('Available', 'N/A', return_time, None, BK_id))
            db.commit()
        else:
            messagebox.showinfo('Cannot be returned', 'The book status cannot be set to Available unless it has been returned')
    else:
        issue_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        issue_card = issuer_card()
        if issue_card is not None:
            return_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('UPDATE Library SET BK_STATUS=%s, CARD_ID=%s, TIMESTAMP=%s, RETURN_DATE=%s WHERE BK_ID=%s', ('Issued', issue_card, issue_time, return_date, BK_id))
            db.commit()
    clear_and_display()

def search_books():
    # Function to search for books
    global tree, cursor
    search_keyword = search_entry.get()
    tree.delete(*tree.get_children())
    cursor.execute(
        "SELECT * FROM Library WHERE BK_NAME LIKE %s OR BK_ID LIKE %s OR AUTHOR_NAME LIKE %s OR COURSE_CODE LIKE%s",
        (f"%{search_keyword}%", f"%{search_keyword}%", f"%{search_keyword}%",f"%{search_keyword}%")
    )
    data = cursor.fetchall()
    for records in data:
        tree.insert('', 'end', values=records)

def issued_books():
    # Function to display issued books
    global tree, cursor
    tree.delete(*tree.get_children())
    cursor.execute(
        "SELECT * FROM Library WHERE BK_STATUS LIKE %s ",
        ('Issued',)
    )
    data = cursor.fetchall()
    for records in data:
        tree.insert('', 'end', values=records)

def change_password():
    # Function to change the password
    global cursor, db

    # Prompt the user to enter the current password
    current_password = simpledialog.askstring('Current Password', 'Enter your current password:\t\t\t')
    
    if not current_password:
        messagebox.showerror('Password not provided', 'You must provide your current password to change it.')
        return

    # Fetch the user's current password from the database based on the logged-in user
    logged_in_user = username  # Assuming the username is stored here
    cursor.execute("SELECT password FROM admins WHERE username = %s", (logged_in_user,))
    user_data = cursor.fetchone()

    if user_data:
        stored_password = user_data[0]

        # Check if the entered current password matches the stored password
        if current_password == stored_password:
            # Prompt the user to enter and confirm the new password
            new_password = simpledialog.askstring('New Password', 'Enter your new password:\t\t\t')
            if new_password:
                confirm_new_password = simpledialog.askstring('Confirm New Password', 'Confirm your new password:\t\t\t')
                if new_password == confirm_new_password:
                    # Update the user's password in the database
                    cursor.execute("UPDATE admins SET password = %s WHERE username = %s", (new_password, logged_in_user))
                    db.commit()
                    messagebox.showinfo('Password Changed', 'Your password has been successfully changed.')
                else:
                    messagebox.showerror('Password Mismatch', 'New passwords do not match.')
            else:
                messagebox.showerror('Invalid Password', 'Invalid new password.')
        else:
            messagebox.showerror('Incorrect Password', 'The entered current password is incorrect.')
    else:
        messagebox.showerror('User not found', 'User not found in the database.')

def issued_by_student(cursor):
    # Function to display books issued by the current student (based on the username)
    global  tree, username, buttons, lable_var
    lable_var.set('ISSUED BOOKS')
    # Clear the Treeview widget
    tree.delete(*tree.get_children())
    toggle_extra_columns()
    toggle_visibility(buttons)
    # Execute a query to fetch books issued by the current student
    cursor.execute('SELECT * FROM Library WHERE CARD_ID = %s', (username,))
    data = cursor.fetchall()

    for record in data:
        # Assuming 'ISSUE_DATE' and 'RETURN_DATE' columns exist in your database
        tree.insert('', 'end', values=record)

def back_button():
    global cursor, tree, buttons, lable_var
    lable_var.set('AVAILABLE BOOKS')
    toggle_extra_columns()
    toggle_visibility(buttons)
    display_available_books() 

def toggle_extra_columns():
    global show_extra_columns, tree

    # Toggle the flag
    show_extra_columns = not show_extra_columns

    # Configure columns based on the flag
    if show_extra_columns:
        # Show the 'Issue Date' and 'Return Date' columns
        tree.column('#7', width=100, stretch='no')
        tree.column('#8', width=100, stretch='no')
        tree.heading('#7', text='Issue Date', anchor='center')
        tree.heading('#8', text='Return Date', anchor='center')
    else:
        # Hide the 'Issue Date' and 'Return Date' columns
        tree.column('#7', width=0)
        tree.column('#8', width=0)
        tree.heading('#7', text='', anchor='center')
        tree.heading('#8', text='', anchor='center')

def toggle_visibility(buttons):
    for b in buttons:
        if b.winfo_ismapped():
            # Button is currently visible, hide it
            b.pack_forget()
        else:
            # Button is currently hidden, show it
            b.pack()

def display_available_books():
    # Function to display available books in the Treeview
    global cursor, tree
    tree.delete(*tree.get_children())  # Clear the Treeview
    cursor.execute('SELECT * FROM Library WHERE BK_STATUS = %s', ('Available',))
    data = cursor.fetchall()
    for records in data:
        tree.insert('', 'end', values=records)

def admin_panel():
    global bk_status,bk_id,bk_name,author_name,card_id,tree,cursor,db,course_code,search_entry
    lf_bg = 'SkyBlue'  # Left Frame Background Color
    rtf_bg = '#0099ff'  # Right Top Frame Background Color
    rbf_bg = 'LightSkyBlue'  # Right Bottom Frame Background Color
    btn_hlb_bg = '#6699ff'  # Background color for Head Labels and Buttons

    lbl_font = ('Georgia', 13)  # Font for all labels
    entry_font = ('Times New Roman', 12)  # Font for all Entry widgets
    btn_font = ('Gill Sans MT', 13)

    # Initializing the main GUI window
    root = tk.Tk()
    root.title('Library Management System')
    root.geometry('1280x720')

    tk.Label(root, text='LIBRARY MANAGEMENT SYSTEM', font=("Noto Sans CJK TC", 15, 'bold'), bg="LightSkyBlue", fg='black').pack(side=tk.TOP, fill=tk.X)

    # StringVars
    bk_status = tk.StringVar()
    bk_name = tk.StringVar()
    bk_id = tk.StringVar()
    author_name = tk.StringVar()
    card_id = tk.StringVar()
    course_code=tk.StringVar()

    # Frames
    left_frame = tk.Frame(root, bg=lf_bg)
    left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

    RT_frame = tk.Frame(root, bg=rtf_bg)
    RT_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)

    RB_frame = tk.Frame(root, bg=rbf_bg)
    RB_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

    # Left Frame
    tk.Label(left_frame, text='Book Name', bg=lf_bg, font=lbl_font).place(x=150, y=25)
    tk.Entry(left_frame, width=25, font=entry_font, textvariable=bk_name).place(x=90, y=55)

    tk.Label(left_frame, text='Book ID', bg=lf_bg, font=lbl_font).place(x=165, y=105)
    bk_id_entry = tk.Entry(left_frame, width=25, font=entry_font, textvariable=bk_id)
    bk_id_entry.place(x=90, y=135)

    tk.Label(left_frame, text='Author Name', bg=lf_bg, font=lbl_font).place(x=145, y=185)
    tk.Entry(left_frame, width=25, font=entry_font, textvariable=author_name).place(x=90, y=215)
    
    tk.Label(left_frame, text='Course Code', bg=lf_bg, font=lbl_font).place(x=145, y=265)
    tk.Entry(left_frame, width=25, font=entry_font, textvariable=course_code).place(x=90, y=295)

    tk.Label(left_frame, text='Status of the Book', bg=lf_bg, font=lbl_font).place(x=125, y=335)
    dd = tk.OptionMenu(left_frame, bk_status, *['Available', 'Issued'])
    dd.configure(font=entry_font, width=12)
    dd.place(x=125, y=370)

    submit = tk.Button(left_frame, text='Add new record', font=btn_font, bg=btn_hlb_bg, width=20, command=add_record)
    submit.place(x=90, y=435)

    clear = tk.Button(left_frame, text='Clear fields', font=btn_font, bg=btn_hlb_bg, width=20, command=clear_fields)
    clear.place(x=90, y=495)

    # Right Top Frame
    tk.Button(RT_frame, text='Delete book record', font=btn_font, bg=btn_hlb_bg, width=17, command=remove_record).place(x=8, y=30)
    tk.Button(RT_frame, text='Delete full inventory', font=btn_font, bg=btn_hlb_bg, width=17, command=delete_inventory).place(x=178, y=30)
    tk.Button(RT_frame, text='Change Book Availability', font=btn_font, bg=btn_hlb_bg, width=19, command=change_availability).place(x=348, y=30)
    tk.Button(RT_frame, text='Issued Books', font=btn_font, bg=btn_hlb_bg, width=19, command=issued_books).place(x=538, y=30)
    search_label = tk.Label(RT_frame, text='Search Books:', font=lbl_font, bg=rtf_bg)
    search_label.place(x=430, y=100)
    
    search_entry = tk.Entry(RT_frame, width=30, font=entry_font)
    search_entry.place(x=550, y=100)

    search_image = tk.PhotoImage(file="D:\LMS\search.png")
    search_button = tk.Button(RT_frame, image=search_image, font=('Gill Sans MT', 10), bg=btn_hlb_bg, width=20, command=search_books)
    search_button.place(x=800, y=101)

    change_password_btn = tk.Button(left_frame, text='Change Password', font=btn_font, bg=btn_hlb_bg, width=20, command=change_password)
    change_password_btn.place(x=90, y=555)

    # Right Bottom Frame
    tk.Label(RB_frame, text='BOOK INVENTORY', bg=rbf_bg, font=("Noto Sans CJK TC", 15, 'bold')).pack(side=tk.TOP, fill=tk.X)

    tree = ttk.Treeview(RB_frame, selectmode='browse', columns=('Book Name', 'Book ID', 'Author', 'Status', 'Issuer Card ID','Course Code','Time','Return'))

    XScrollbar = ttk.Scrollbar(tree, orient='horizontal', command=tree.xview)
    YScrollbar = ttk.Scrollbar(tree, orient='vertical', command=tree.yview)
    XScrollbar.pack(side='bottom', fill='x')
    YScrollbar.pack(side='right', fill='y')

    tree.config(xscrollcommand=XScrollbar.set, yscrollcommand=YScrollbar.set)

    tree.heading('Book Name', text='Book Name', anchor='center')
    tree.heading('Book ID', text='Book ID', anchor='center')
    tree.heading('Author', text='Author', anchor='center')
    tree.heading('Status', text='Status of the Book', anchor='center')
    tree.heading('Issuer Card ID', text='Card ID of the Issuer', anchor='center')
    tree.heading('Course Code',text='Course Code',anchor='center')
    tree.heading('Time',text='TIME',anchor='center')

    tree.column('#0', width=0, stretch='no')
    tree.column('#1', width=225, stretch='no')
    tree.column('#2', width=70, stretch='no')
    tree.column('#3', width=150, stretch='no')
    tree.column('#4', width=105, stretch='no')
    tree.column('#5', width=132, stretch='no')
    tree.column('#6', width=130,stretch='no')
    tree.column('#7', width=120,stretch='no')
    tree.column('#8', width=0,stretch='no')


    tree.place(y=30, x=0, relheight=0.9, relwidth=1)

    
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='K@ustubh0912',
        database='library'
    )
    cursor = db.cursor()
    cursor.execute('''
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
    db.commit()
    clear_and_display()
    root.update()
    root.mainloop()

def student_page():
    global bk_status, bk_id, bk_name, author_name, card_id, tree, cursor, db, course_code, search_entry, show_extra_columns, buttons, lable_var

    show_extra_columns = False
    lf_bg = 'SkyBlue'  # Left Frame Background Color
    rtf_bg = '#0099ff'  # Right Top Frame Background Color
    rbf_bg = 'LightSkyBlue'  # Right Bottom Frame Background Color
    btn_hlb_bg = '#6699ff'  # Background color for Head Labels and Buttons

    lbl_font = ('Georgia', 13)  # Font for all labels
    entry_font = ('Times New Roman', 12)  # Font for all Entry widgets
    btn_font = ('Gill Sans MT', 13)

    # Initializing the main GUI window
    root = tk.Tk()
    root.title('Library Management System')
    root.geometry('1280x720')

    tk.Label(root, text='LIBRARY MANAGEMENT SYSTEM', font=("Noto Sans CJK TC", 15, 'bold'), bg="LightSkyBlue", fg='black').pack(side=tk.TOP, fill=tk.X)

    # StringVars
    bk_status = tk.StringVar()
    bk_name = tk.StringVar()
    bk_id = tk.StringVar()
    author_name = tk.StringVar()
    card_id = tk.StringVar()
    course_code = tk.StringVar()
    lable_var=tk.StringVar()

    # Frames
    RT_frame = tk.Frame(root, bg=rtf_bg)
    RT_frame.place(relx=0, y=30, relheight=0.2, relwidth=1)

    RB_frame = tk.Frame(root, bg=rbf_bg)
    RB_frame.place(relx=0, rely=0.24, relheight=0.785, relwidth=1)

    # Right Bottom Frame
    inital='AVAILABLE BOOKS'
    lable_var.set(inital)
    tk.Label(RB_frame, textvariable=lable_var, bg=rbf_bg, font=("Noto Sans CJK TC", 15, 'bold')).pack(side=tk.TOP, fill=tk.X)    
    # Right Top Frame
    issued_books_btn = tk.Button(RT_frame, text='Issued Books', font=btn_font, bg=btn_hlb_bg, width=17, command=lambda: issued_by_student(cursor))
    issued_books_btn.place(x=865, y=30)

    chg_pass_btn = tk.Button(RT_frame, text='Change Password', font=btn_font, bg=btn_hlb_bg, width=17,command=change_password)
    chg_pass_btn.place(x=178, y=30)

    back_btn = tk.Button(RT_frame, text='Back', font=btn_font, bg=btn_hlb_bg, width=17,command=back_button)
    buttons = [issued_books_btn, chg_pass_btn, back_btn]

    search_label = tk.Label(RT_frame, text='Search Books:', font=lbl_font, bg=rtf_bg)
    search_label.place(x=430, y=100)
    
    search_entry = tk.Entry(RT_frame, width=30, font=entry_font)
    search_entry.place(x=550, y=100)

    search_image = tk.PhotoImage(file="D:\LMS\search.png")
    search_button = tk.Button(RT_frame, image=search_image, font=('Gill Sans MT', 10), bg=btn_hlb_bg, width=20, command=search_books)
    search_button.place(x=800, y=101)

    # Create the Treeview and Scrollbars
    tree = ttk.Treeview(RB_frame, selectmode='browse', columns=('Book Name', 'Book ID', 'Author', 'Status', 'Issuer Card ID','Course Code','Time','Return'))

    XScrollbar = ttk.Scrollbar(tree, orient='horizontal', command=tree.xview)
    YScrollbar = ttk.Scrollbar(tree, orient='vertical', command=tree.yview)
    XScrollbar.pack(side='bottom', fill='x')
    YScrollbar.pack(side='right', fill='y')

    tree.config(xscrollcommand=XScrollbar.set, yscrollcommand=YScrollbar.set)

    tree.heading('Book Name', text='Book Name', anchor='center')
    tree.heading('Book ID', text='Book ID', anchor='center')
    tree.heading('Author', text='Author', anchor='center')
    tree.heading('Status', text='Status of the Book', anchor='center')
    tree.heading('Issuer Card ID',text='',anchor='center')
    tree.heading('Course Code', text='Course Code', anchor='center')

    tree.column('#0', width=0, stretch='no')
    tree.column('#1', width=225, stretch='no')
    tree.column('#2', width=70, stretch='no')
    tree.column('#3', width=150, stretch='no')
    tree.column('#4', width=0, stretch='no')
    tree.column('#5', width=0, stretch='no')
    tree.column('#6',width=150,stretch='no')
    tree.column('#7', width=0, stretch='no')
    tree.column('#8', width=0, stretch='no')


    tree.place(y=30, x=30, relheight=0.9, relwidth=1)

    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='K@ustubh0912',
        database='library'
    )
    cursor = db.cursor()
    cursor.execute('''
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
    db.commit()
    display_available_books()
    root.update()
    root.mainloop()

def login_page():
    # Function to create the login page
    global log_pg,entry_username, entry_password
    log_pg = tk.Tk()
    log_pg.geometry("1280x720")
    log_pg.configure(bg="LightBlue")
    log_pg.title("Login")
    
    lblTitle = tk.Label(text="Login Page", font=("arial", 50, "bold"), fg="black", bg="LightBlue")
    lblTitle.pack()
    
    bordercolor = tk.Frame(log_pg, bg="black", width=800, height=400)
    bordercolor.pack()
    
    mainframe = tk.Frame(bordercolor, bg="#1a75ff", width=800, height=400)
    mainframe.pack(padx=20, pady=20)
    
    tk.Label(mainframe, text="Username", font=("arial", 30, "bold"), bg="#1a75ff").place(x=100, y=50)
    tk.Label(mainframe, text="Password", font=("arial", 30, "bold"), bg="#1a75ff").place(x=100, y=150)
    
    username = tk.StringVar()
    password = tk.StringVar()
    
    entry_username = tk.Entry(mainframe, textvariable=username, width=12, bd=2, font=("arial", 30))
    entry_username.place(x=400, y=50)
    entry_password = tk.Entry(mainframe, textvariable=password, width=12, bd=2, font=("arial", 30), show="*")
    entry_password.place(x=400, y=150)
    
    login_btn = tk.Button(mainframe, text="LOGIN", font="arial", bg="LightBlue", width=30, command=login)
    login_btn.place(x=250, y=250)
    log_pg.mainloop()

login_page()
