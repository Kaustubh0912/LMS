import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector

# Global variables
global cursor, tree, bk_status, bk_name, bk_id, author_name, card_id, search_entry, db, course_code, username

def create_database_if_not_exists():
    # Function to create the database and user table if they don't exist
    try:
        # Connect to MySQL without specifying a database
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="K@ustubh0912"
        )

        cursor = db.cursor()

        # Create the database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS library")

        # Use the database
        cursor.execute("USE library")

        # Create the user table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
def login():
    global username 
    username= entry_username.get()
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
        user_data = cursor.fetchone()

        if user_data:
            # Check if the entered password matches the password stored in the database
            if password == user_data[2]:
                messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
                log_pg.destroy()
                admin_panel()
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

def view_record():
    # Function to view a record
    global bk_name, bk_id, bk_status, author_name, card_id, tree,course_code
    if not tree.focus():
        messagebox.showerror('Select a row!', 'To view a record, you must select it in the table. Please do so before continuing.')
        return
    current_item_selected = tree.focus()
    values_in_selected_item = tree.item(current_item_selected)
    selection = values_in_selected_item['values']
    bk_name.set(selection[0])
    bk_id.set(selection[1])
    author_name.set(selection[2])
    bk_status.set(selection[3])
    card_id.set(selection[4])
    course_code.set(selection[5])

def add_record():
    # Function to add a record
    global bk_name, bk_id, author_name, bk_status, card_id, db, course_code
    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
    else:
        card_id.set('N/A')
    surety = messagebox.askyesno('Are you sure?', 'Are you sure this is the data you want to enter?\nPlease note that Book ID cannot be changed in the future')
    if surety:
        try:
            cursor.execute(
                'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID, COURSE_CODE) VALUES (%s, %s, %s, %s, %s,%s)',
                (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get(), course_code.get()))
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
    # Function to change book availability
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
            cursor.execute('UPDATE Library SET BK_STATUS=%s, CARD_ID=%s WHERE BK_ID=%s', ('Available', 'N/A', BK_id))
            db.commit()
        else:
            messagebox.showinfo('Cannot be returned', 'The book status cannot be set to Available unless it has been returned')
    else:
        cursor.execute('UPDATE Library SET BK_STATUS=%s, CARD_ID=%s WHERE BK_ID=%s', ('Issued', issuer_card(), BK_id))
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
    root.resizable(0, 0)

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

    tree = ttk.Treeview(RB_frame, selectmode='browse', columns=('Book Name', 'Book ID', 'Author', 'Status', 'Issuer Card ID','Course Code'))

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

    tree.column('#0', width=0, stretch='no')
    tree.column('#1', width=225, stretch='no')
    tree.column('#2', width=70, stretch='no')
    tree.column('#3', width=150, stretch='no')
    tree.column('#4', width=105, stretch='no')
    tree.column('#5', width=132, stretch='no')
    tree.column('#6', width=130,stretch='no')

    tree.place(y=30, x=0, relheight=0.9, relwidth=1)

    
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='K@ustubh0912',
        database='library'
    )
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Library (
                        BK_NAME VARCHAR(255),
                        BK_ID VARCHAR(255) PRIMARY KEY,
                        AUTHOR_NAME VARCHAR(255),
                        BK_STATUS VARCHAR(255),
                        CARD_ID VARCHAR(255),
                        COURSE_CODE VARCHAR(255))''')
    db.commit()
    clear_and_display()
    root.update()
    root.mainloop()

def login_page():
    # Function to create the login page
    global log_pg
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
    global entry_username, entry_password
    entry_username = tk.Entry(mainframe, textvariable=username, width=12, bd=2, font=("arial", 30))
    entry_username.place(x=400, y=50)
    entry_password = tk.Entry(mainframe, textvariable=password, width=12, bd=2, font=("arial", 30), show="*")
    entry_password.place(x=400, y=150)
    
    login_btn = tk.Button(mainframe, text="LOGIN", font="arial", bg="LightBlue", width=30, command=login)
    login_btn.place(x=250, y=250)
    log_pg.mainloop()

create_database_if_not_exists()
login_page()
