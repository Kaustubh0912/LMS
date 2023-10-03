import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import mysql.connector  # Import MySQL connector

def issuer_card():
    Cid = simpledialog.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?\t\t\t')

    if not Cid:
        messagebox.showerror('Issuer ID cannot be empty!', 'Can\'t keep Issuer ID empty, it must have a value')
    else:
        return Cid

def display_records():
    global cursor
    global tree

    tree.delete(*tree.get_children())

    cursor.execute('SELECT * FROM Library')
    data = cursor.fetchall()

    for records in data:
        tree.insert('', 'end', values=records)

def clear_fields():
    global bk_status, bk_id, bk_name, author_name, card_id

    bk_status.set('Available')
    bk_id.set('')
    bk_name.set('')
    author_name.set('')
    card_id.set('')

    try:
        tree.selection_remove(tree.selection()[0])
    except:
        pass

def clear_and_display():
    clear_fields()
    display_records()

def view_record():
    global bk_name, bk_id, bk_status, author_name, card_id
    global tree

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

def add_record():
    global bk_name, bk_id, author_name, bk_status, card_id

    if bk_status.get() == 'Issued':
        card_id.set(issuer_card())
    else:
        card_id.set('N/A')

    surety = messagebox.askyesno('Are you sure?', 'Are you sure this is the data you want to enter?\nPlease note that Book ID cannot be changed in the future')

    if surety:
        try:
            cursor.execute(
                'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID) VALUES (%s, %s, %s, %s, %s)',
                (bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get()))
            db.commit()

            clear_and_display()

            messagebox.showinfo('Record added', 'The new record was successfully added to your database')
        except mysql.connector.IntegrityError:
            messagebox.showerror('Book ID already in use!','The Book ID you are trying to enter is already in the database, please alter that book\'s record or check any discrepancies on your side')

# def update_record():
#     def update():
#         global bk_status, bk_name, bk_id, author_name, card_id

#         if bk_status.get() == 'Issued':
#             card_id.set(issuer_card())
#         else:
#             card_id.set('N/A')

#         cursor.execute('UPDATE Library SET BK_NAME=%s, BK_STATUS=%s, AUTHOR_NAME=%s, CARD_ID=%s WHERE BK_ID=%s',(bk_name.get(), bk_status.get(), author_name.get(), card_id.get(), bk_id.get()))
#         db.commit()

#         clear_and_display()

#         edit.destroy()
#         bk_id_entry.config(state='normal')
#         clear.config(state='normal')

#     bk_id_entry.config(state='disable')
#     clear.config(state='disable')

#     edit = tk.Button(left_frame, text='Update Record', font=btn_font, bg=btn_hlb_bg, width=20, command=update)
#     edit.place(x=50, y=375)

def remove_record():
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
            cursor.execute('UPDATE Library SET BK_STATUS=%s, CARD_ID=%s WHERE BK_ID=%s', ('Available', 'N/A', BK_id))
            db.commit()
        else:
            messagebox.showinfo('Cannot be returned', 'The book status cannot be set to Available unless it has been returned')
    else:
        cursor.execute('UPDATE Library SET BK_STATUS=%s, CARD_ID=%s WHERE BK_ID=%s', ('Issued', issuer_card(), BK_id))
        db.commit()

    clear_and_display()
def search_books():
    global tree, cursor

    # Get the search keyword from the Entry widget
    search_keyword = search_entry.get()

    # Clear the current displayed records
    tree.delete(*tree.get_children())

    # Perform a SQL query to search for books
    cursor.execute(
        "SELECT * FROM Library WHERE BK_NAME LIKE %s OR BK_ID LIKE %s OR AUTHOR_NAME LIKE %s",
        (f"%{search_keyword}%", f"%{search_keyword}%", f"%{search_keyword}%")
    )
    
    data = cursor.fetchall()

    for records in data:
        tree.insert('', 'end', values=records)


# Variables
lf_bg = 'LightSkyBlue'  # Left Frame Background Color
rtf_bg = 'DeepSkyBlue'  # Right Top Frame Background Color
rbf_bg = 'DodgerBlue'  # Right Bottom Frame Background Color
btn_hlb_bg = 'SteelBlue'  # Background color for Head Labels and Buttons

lbl_font = ('Georgia', 13)  # Font for all labe
entry_font = ('Times New Roman', 12)  # Font for all Entry widgets
btn_font = ('Gill Sans MT', 13)

# Initializing the main GUI window
root = tk.Tk()
root.title('PythonGeeks Library Management System')
root.geometry('1600x900')
root.resizable(0, 0)

tk.Label(root, text='LIBRARY MANAGEMENT SYSTEM', font=("Noto Sans CJK TC", 15, 'bold'), bg=btn_hlb_bg,
      fg='White').pack(side=tk.TOP, fill=tk.X)

# StringVars
bk_status = tk.StringVar()
bk_name = tk.StringVar()
bk_id = tk.StringVar()
author_name = tk.StringVar()
card_id = tk.StringVar()

# Frames
left_frame = tk.Frame(root, bg=lf_bg)
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)

RT_frame = tk.Frame(root, bg=rtf_bg)
RT_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)

RB_frame = tk.Frame(root)
RB_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

# Left Frame
tk.Label(left_frame, text='Book Name', bg=lf_bg, font=lbl_font).place(x=98, y=25)
tk.Entry(left_frame, width=25, font=entry_font, textvariable=bk_name).place(x=45, y=55)

tk.Label(left_frame, text='Book ID', bg=lf_bg, font=lbl_font).place(x=110, y=105)
bk_id_entry = tk.Entry(left_frame, width=25, font=entry_font, textvariable=bk_id)
bk_id_entry.place(x=45, y=135)

tk.Label(left_frame, text='Author Name', bg=lf_bg, font=lbl_font).place(x=90, y=185)
tk.Entry(left_frame, width=25, font=entry_font, textvariable=author_name).place(x=45, y=215)

tk.Label(left_frame, text='Status of the Book', bg=lf_bg, font=lbl_font).place(x=75, y=265)
dd = tk.OptionMenu(left_frame, bk_status, *['Available', 'Issued'])
dd.configure(font=entry_font, width=12)
dd.place(x=75, y=300)

submit = tk.Button(left_frame, text='Add new record', font=btn_font, bg=btn_hlb_bg, width=20, command=add_record)
submit.place(x=50, y=375)

clear = tk.Button(left_frame, text='Clear fields', font=btn_font, bg=btn_hlb_bg, width=20, command=clear_fields)
clear.place(x=50, y=435)

# Right Top Frame
tk.Button(RT_frame, text='Delete book record', font=btn_font, bg=btn_hlb_bg, width=17, command=remove_record).place(x=8,y=30)
tk.Button(RT_frame, text='Delete full inventory', font=btn_font, bg=btn_hlb_bg, width=17, command=delete_inventory).place(x=178, y=30)
# tk.Button(RT_frame, text='Update book details', font=btn_font, bg=btn_hlb_bg, width=17,command=update_record).place(x=348, y=30)
tk.Button(RT_frame, text='Change Book Availability', font=btn_font, bg=btn_hlb_bg, width=19,command=change_availability).place(x=518, y=30)

# Right Bottom Frame
tk.Label(RB_frame, text='BOOK INVENTORY', bg=rbf_bg, font=("Noto Sans CJK TC", 15, 'bold')).pack(side=tk.TOP, fill=tk.X)
search_label = tk.Label(RT_frame, text='Search Books:', font=lbl_font, bg=rtf_bg)
search_label.place(x=300, y=0)

search_entry = tk.Entry(RT_frame, width=30, font=entry_font)
search_entry.place(x=425, y=0)

search_button = tk.Button(RT_frame, text='Search books', font=('Gill Sans MT', 10), bg='LightSkyBlue', width=15, command=search_books)
search_button.place(x=300, y=0)

tree = ttk.Treeview(RB_frame, selectmode='browse', columns=('Book Name', 'Book ID', 'Author', 'Status', 'Issuer Card ID'))

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

tree.column('#0', width=0, stretch='no')
tree.column('#1', width=225, stretch='no')
tree.column('#2', width=70, stretch='no')
tree.column('#3', width=150, stretch='no')
tree.column('#4', width=105, stretch='no')
tree.column('#5', width=132, stretch='no')

tree.place(y=30, x=0, relheight=0.9, relwidth=1)

# Database connection
db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='K@ustubh0912',
    database='library'
)
cursor = db.cursor()

# Create the table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS Library (
                    BK_NAME VARCHAR(255),
                    BK_ID VARCHAR(255) PRIMARY KEY,
                    AUTHOR_NAME VARCHAR(255),
                    BK_STATUS VARCHAR(255),
                    CARD_ID VARCHAR(255))''')
db.commit()

clear_and_display()

# Finalizing the window
root.update()
root.mainloop()
