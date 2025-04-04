import datetime
from tkinter import *
import tkinter.messagebox as mb
from tkinter import ttk
from tkcalendar import DateEntry
import sqlite3
import random
import page_after_login

def book_appointment():
    global tree
    global name_strvar, email_strvar, contact_strvar, gender_strvar, dob, stream_strvar

    # Creating the universal font variables
    headlabelfont = ("Noto Sans CJK TC", 15, 'bold')
    labelfont = ('Garamond', 14)
    entryfont = ('Garamond', 12)

    # Connecting to the Database where all information will be stored
    connector = sqlite3.connect('Appointment.db')
    cursor = connector.cursor()
    connector.execute(
        "CREATE TABLE IF NOT EXISTS APPOINTMENT_MANAGEMENT (PATIENT_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, NAME TEXT, EMAIL TEXT, PHONE_NO TEXT, GENDER TEXT, DOB TEXT, STREAM TEXT, DOCTOR_NAME TEXT)"
    )

    # List of available doctor names
    doctor_names = ["Dr. John Doe", "Dr. Jane Smith", "Dr. Robert Johnson", "Dr. Emily Davis", "Dr. Michael Wilson"]

    # Creating the functions
    def reset_fields():
        global name_strvar, email_strvar, contact_strvar, gender_strvar, dob, stream_strvar
        for i in ['name_strvar', 'email_strvar', 'contact_strvar', 'gender_strvar', 'stream_strvar']:
            exec(f"{i}.set('')")
        dob.set_date(datetime.datetime.now().date())

    def reset_form():
        global tree
        tree.delete(*tree.get_children())
        reset_fields()

    def display_records():
        tree.delete(*tree.get_children())
        curr = connector.execute('SELECT * FROM APPOINTMENT_MANAGEMENT')
        data = curr.fetchall()
        for records in data:
            tree.insert('', END, values=(records[0], records[1], records[3], records[4], records[5], records[6], records[-1]))

    def get_available_doctor():
        # Randomly select a doctor from the list
        return random.choice(doctor_names)

    def add_record():
        global name_strvar, email_strvar, contact_strvar, gender_strvar, dob, stream_strvar

        # Get user input
        patient_name = name_strvar.get()
        email = email_strvar.get()
        contact = contact_strvar.get()
        gender = gender_strvar.get()
        DOB = dob.get_date()
        stream = stream_strvar.get()

        # Validate patient's name
        if not patient_name or not patient_name.isalpha():
            mb.showerror('Error!', "Please enter a valid name with alphabets only.")
            return

        if not contact or not contact.isdigit() or len(contact) != 10:
            mb.showerror('Error!', "Please enter a valid 10-digit contact number.")
            return

        if not patient_name or not contact or not gender or not DOB or not stream:
            mb.showerror('Error!', "Please fill all the missing fields!!")
            return

        # Check if the appointment date is in the future
        if DOB < datetime.datetime.now().date():
            mb.showerror('Error!', "Please select a date in the future for the appointment.")
            return

        # Check if the appointment time is between 1 to 24 hours
        try:
            stream = int(stream)
            if not (1 <= stream <= 24):
                raise ValueError("Invalid time")
        except ValueError:
            mb.showerror('Error!', "Please enter a valid time between 1 to 24 hours.")
            return

        # Get an available doctor
        doctor_name = get_available_doctor()

        # Check if the appointment time is available
        existing_appointments = connector.execute(
            "SELECT DOCTOR_NAME FROM APPOINTMENT_MANAGEMENT WHERE DOB=? AND STREAM=?",
            (DOB, stream)
        ).fetchall()

        available_doctors = [f"Dr. {i}" for i in doctor_names]

        booked_doctors = [record[0] for record in existing_appointments]

        available_doctors = [doctor for doctor in available_doctors if doctor not in booked_doctors]

        if not available_doctors:
            mb.showerror('Error!', "All doctors are fully booked at the selected date and time.")
            return
        # Randomly assign the appointment to one of the available doctors
        doctor_name = random.choice(available_doctors)

        # Get the last inserted appointment ID
        last_id = connector.execute("SELECT MAX(PATIENT_ID) FROM APPOINTMENT_MANAGEMENT").fetchone()[0]
        # If there are no previous records, start from ID 1
        if last_id is None:
            last_id = 0

        # Increment the appointment ID
        new_id = last_id + 1
        try:
            
            # Insert the record into the database with the selected doctor's name
            connector.execute(
                'INSERT INTO APPOINTMENT_MANAGEMENT (NAME, EMAIL, PHONE_NO, GENDER, DOB, STREAM, DOCTOR_NAME) VALUES (?,?,?,?,?,?,?)',
                (patient_name, email, contact, gender, DOB, stream, doctor_name)
            )
            connector.commit()
            mb.showinfo('Record added', f"Record of {patient_name} was successfully added with Doctor: {doctor_name}")
            reset_fields()
            display_records()
        except Exception as e:
            mb.showerror('Error', f'An error occurred: {e}')

    def back():
        main.destroy()
        page_after_login.page_after_login()

    def remove_record():
        if not tree.selection():
            mb.showerror('Error!', 'Please select an item from the database')
        else:
            current_item = tree.focus()
            values = tree.item(current_item)
            selection = values["values"]
            tree.delete(current_item)
            connector.execute('DELETE FROM APPOINTMENT_MANAGEMENT WHERE PATIENT_ID=%d' % selection[0])
            connector.commit()
            mb.showinfo('Done', 'The record you wanted deleted was successfully deleted.')

    def view_record():
        global name_strvar, email_strvar, contact_strvar, gender_strvar, dob, stream_strvar
        if not tree.selection():
            mb.showerror('Error!', 'Please select a record to view')
        else:
            current_item = tree.focus()
            values = tree.item(current_item)
            selection = values["values"]

            name_strvar.set(selection[1])
            email_strvar.set(selection[2])
            contact_strvar.set(selection[3])
            gender_strvar.set(selection[4])
            date = datetime.date(int(selection[5][:4]), int(selection[5][5:7]), int(selection[5][8:]))
            dob.set_date(date)
            stream_strvar.set(selection[6])

    # Initializing the GUI window
    main = Tk()
    main.title('APPOINTMENT MANAGEMENT SYSTEM')
    main.geometry('1166x718')
    main.resizable(0, 0)
    main.state('zoomed')

    # Creating the background and foreground color variables
    lf_bg = 'MediumSpringGreen'  # bg color for the left_frame
    cf_bg = 'PaleGreen'  # bg color for the center_frame

    # Creating the StringVar or IntVar variables
    name_strvar = StringVar()
    email_strvar = StringVar()
    contact_strvar = StringVar()
    gender_strvar = StringVar()
    stream_strvar = StringVar()

    # Placing the components in the main window
    Label(main, text="HOSPITAL EASE", font=headlabelfont, bg='SpringGreen').pack(side=TOP, fill=X)
    left_frame = Frame(main, bg=lf_bg)
    left_frame.place(x=0, y=30, relheight=1, relwidth=0.2)
    center_frame = Frame(main, bg=cf_bg)
    center_frame.place(relx=0.2, y=30, relheight=1, relwidth=0.2)
    right_frame = Frame(main, bg="Gray35")
    right_frame.place(relx=0.4, y=30, relheight=1, relwidth=0.6)

    # Placing components in the left frame
    Label(left_frame, text="Name", font=labelfont, bg=lf_bg).place(relx=0.375, rely=0.05)
    Label(left_frame, text="Contact Number", font=labelfont, bg=lf_bg).place(relx=0.175, rely=0.18)
    Label(left_frame, text="Gender", font=labelfont, bg=lf_bg).place(relx=0.3, rely=0.44)
    Label(left_frame, text="Date of Appointment", font=labelfont, bg=lf_bg).place(relx=0.1, rely=0.57)
    Label(left_frame, text="Time", font=labelfont, bg=lf_bg).place(relx=0.3, rely=0.7)
    Entry(left_frame, width=19, textvariable=name_strvar, font=entryfont).place(x=20, rely=0.1)
    Entry(left_frame, width=19, textvariable=contact_strvar, font=entryfont).place(x=20, rely=0.23)
    Entry(left_frame, width=19, textvariable=stream_strvar, font=entryfont).place(x=20, rely=0.75)
    OptionMenu(left_frame, gender_strvar, 'Male', 'Female').place(x=45, rely=0.49, relwidth=0.5)
    dob = DateEntry(left_frame, font=("Arial", 12), width=15)
    dob.place(x=20, rely=0.62)
    Button(left_frame, text='Book Appointment', font=labelfont, command=add_record, width=18).place(relx=0.025, rely=0.85)

    # Placing components in the center frame
    Button(center_frame, text='Cancel Appointment', font=labelfont, command=remove_record, width=15).place(relx=0.1, rely=0.25)
    Button(center_frame, text='View Appointment', font=labelfont, command=view_record, width=15).place(relx=0.1, rely=0.35)
    Button(center_frame, text='Reset Fields', font=labelfont, command=reset_fields, width=15).place(relx=0.1, rely=0.45)
    Button(center_frame, text='Back', font=labelfont, command=back, width=15).place(relx=0.1, rely=0.65)

    # Placing components in the right frame
    Label(right_frame, text='Appointment Record', font=headlabelfont, bg='DarkGreen', fg='LightCyan').pack(side=TOP, fill=X)
    tree = ttk.Treeview(right_frame, height=100, selectmode=BROWSE,
                        columns=('Patient ID', "Name", "Contact Number", "Gender", "Date of Birth", "Stream", "Doctor Name"))
    X_scroller = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
    Y_scroller = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
    X_scroller.pack(side=BOTTOM, fill=X)
    Y_scroller.pack(side=RIGHT, fill=Y)
    tree.config(yscrollcommand=Y_scroller.set, xscrollcommand=X_scroller.set)
    tree.heading('Patient ID', text='ID', anchor=CENTER)
    tree.heading('Name', text='Name', anchor=CENTER)
    tree.heading('Contact Number', text='Phone No', anchor=CENTER)
    tree.heading('Gender', text='Gender', anchor=CENTER)
    tree.heading('Date of Birth', text='Date', anchor=CENTER)
    tree.heading('Stream', text='TIME', anchor=CENTER)
    tree.heading('Doctor Name', text='Doctor Name', anchor=CENTER)  # Increase the width here
    tree.column('#0', width=0, stretch=NO)
    tree.column('#1', width=40, stretch=NO)
    tree.column('#2', width=140, stretch=NO)
    tree.column('#3', width=200, stretch=NO)
    tree.column('#4', width=80, stretch=NO)
    tree.column('#5', width=80, stretch=NO)
    tree.column('#6', width=120, stretch=NO)  # Adjusted width here
    tree.column('#7', width=80, stretch=NO)
    tree.place(y=30, relwidth=1, relheight=0.9, relx=0)
    display_records()

    # Finalizing the GUI window
    main.update()
    main.mainloop()
