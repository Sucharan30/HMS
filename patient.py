import mysql.connector
from tabulate import tabulate
from datetime import datetime
import re

def register_patient(cursor, connection):
    while True:
        name = input("Enter your name: ")
        if re.match(r"^[a-zA-Z\s]+$", name):
            break
        print("Invalid name. Please enter alphabetic characters only.")
    
    while True:
        age = input("Enter your age: ")
        if age.isdigit() and 0 < int(age) < 120:
            age = int(age)
            break
        print("Invalid age. Please enter a valid number between 1 and 120.")
    
    gender = input("Enter your gender: ")
    
    while True:
        dob = input("Enter your date of birth (YYYY-MM-DD): ")
        try:
            datetime.strptime(dob, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid date format. Please enter in YYYY-MM-DD format.")
    
    address = input("Enter your address: ")
    
    while True:
        phone = input("Enter your phone number: ")
        if re.match(r"^\d{10}$", phone):
            break
        print("Invalid phone number. Please enter a 10-digit number.")
    
    while True:
        email = input("Enter your email: ")
        if re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,4}$", email):
            break
        print("Invalid email. Please enter a valid email address.")
    
    password = input("Enter your password: ")

    query = "INSERT INTO patients (name, age, gender, dob, address, phone, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (name, age, gender, dob, address, phone, email, password))
    connection.commit()
    print("Registration successful!")

def login_patient(cursor, connection):
    attempts = 3
    while attempts > 0:
        email = input("Enter your email: ")
        password = input("Enter your password: ")

        query = "SELECT * FROM patients WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        patient = cursor.fetchone()

        if patient:
            print("Login successful!")
            patient_dashboard(cursor, connection, patient[0])  # pass patient ID
            break
        else:
            attempts -= 1
            print(f"Invalid credentials. You have {attempts} attempts left.")

    print("Returning to patient's Menu.")

            

def book_appointment(cursor, connection, patient_id):
    cursor.execute("SELECT id, name, specialization, years_of_experience FROM doctors")
    doctors = cursor.fetchall()

    print("Available doctors:")
    print(tabulate(doctors, headers=["ID", "Name", "Specialization", "Years of Experience"], tablefmt="grid"))

    attempts = 3
    while attempts > 0:
        doctor_id = input("Enter the doctor ID you want to book an appointment with: ")
        if doctor_id.isdigit() and any(doctor_id == str(doc[0]) for doc in doctors):
            doctor_id = int(doctor_id)
            break
        else:
            attempts -= 1
            print(f"Invalid Doctor ID. You have {attempts} attempts left.")
    
    if attempts == 0:
        print("Too many invalid attempts. Returning to patient's Dashboard.")
        return

    while True:
        appointment_date = input("Enter appointment date (YYYY-MM-DD): ")
        try:
            datetime.strptime(appointment_date, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid date format. Please enter in YYYY-MM-DD format.")

    while True:
        appointment_time = input("Enter appointment time (HH:MM:SS): ")
        try:
            datetime.strptime(appointment_time, '%H:%M:%S')
            break
        except ValueError:
            print("Invalid time format. Please enter in HH:MM:SS format.")

    appointment_reason = input("Enter the reason for appointment: ")
    medical_history = input("Enter any relevant medical history: ")

    query = "INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, appointment_reason, medical_history, status) VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled')"
    cursor.execute(query, (patient_id, doctor_id, appointment_date, appointment_time, appointment_reason, medical_history))
    connection.commit()
    print("Appointment booked successfully!")



def view_appointments(cursor, patient_id):
    query = """
    SELECT appointment_id, patient_id, doctor_id, appointment_date, appointment_time, appointment_reason, medical_history, status, COALESCE(cancellation_reason, '') 
    FROM appointments 
    WHERE patient_id = %s
    """
    cursor.execute(query, (patient_id,))
    appointments = cursor.fetchall()
    
    print("Your appointments:")
    print(tabulate(appointments, headers=["Appointment ID", "Patient ID", "Doctor ID", "Date", "Time", "Reason", "Medical History", "Status", "Cancellation Reason"], tablefmt="grid"))


def cancel_appointment(cursor, connection, patient_id):
    query = "SELECT appointment_id FROM appointments WHERE patient_id = %s"
    cursor.execute(query, (patient_id,))
    appointments = cursor.fetchall()
    appointment_ids = [str(appointment[0]) for appointment in appointments]

    attempts = 3
    while attempts > 0:
        appointment_id = input("Enter the appointment ID you want to cancel: ")
        if appointment_id in appointment_ids:
            query = "DELETE FROM appointments WHERE appointment_id = %s AND patient_id = %s"
            cursor.execute(query, (appointment_id, patient_id))
            connection.commit()
            print("Appointment cancelled successfully!")
            return
        else:
            attempts -= 1
            print(f"Invalid appointment ID. You have {attempts} attempts left.")

    print("Too many invalid attempts. Returning to patient's Dashboard.")



def reschedule_appointment(cursor, connection, patient_id):
    query = "SELECT appointment_id FROM appointments WHERE patient_id = %s"
    cursor.execute(query, (patient_id,))
    appointments = cursor.fetchall()
    appointment_ids = [str(appointment[0]) for appointment in appointments]

    attempts = 3
    while attempts > 0:
        appointment_id = input("Enter the appointment ID you want to reschedule: ")
        if appointment_id in appointment_ids:
            break
        else:
            attempts -= 1
            print(f"Invalid appointment ID. You have {attempts} attempts left.")
    
    if attempts == 0:
        print("Too many invalid attempts. Returning to patient's Dashboard.")
        return

    while True:
        new_date = input("Enter the new appointment date (YYYY-MM-DD): ")
        try:
            datetime.strptime(new_date, '%Y-%m-%d')
            break
        except ValueError:
            print("Invalid date format. Please enter in YYYY-MM-DD format.")

    while True:
        new_time = input("Enter the new appointment time (HH:MM:SS): ")
        try:
            datetime.strptime(new_time, '%H:%M:%S')
            break
        except ValueError:
            print("Invalid time format. Please enter in HH:MM:SS format.")

    query = "UPDATE appointments SET appointment_date = %s, appointment_time = %s WHERE appointment_id = %s AND patient_id = %s"
    cursor.execute(query, (new_date, new_time, appointment_id, patient_id))
    connection.commit()
    print("Appointment rescheduled successfully!")

def view_treatment(cursor, patient_id):
    query = """
    SELECT t.Treatment_ID, t.Doctor_ID, d.name AS Doctor_Name, t.Diagnosis, t.Treatment_Plan, t.Treatment_Cost, t.Start_Date, t.End_Date,
           t.Room_ID, t.Nurse_ID, t.Treatment_Status, t.Cancellation_Reason
    FROM Treatment t
    JOIN doctors d ON t.Doctor_ID = d.id
    JOIN Room r ON t.Room_ID = r.RoomID
    JOIN nurses n ON t.Nurse_ID = n.id
    WHERE t.Patient_ID = %s
    """
    cursor.execute(query, (patient_id,))
    treatments = cursor.fetchall()

    if not treatments:
        print("No treatments found for this patient.")
    else:
        print("Your treatments:")
        print(tabulate(treatments, headers=["Treatment ID", "Doctor ID", "Doctor Name", "Diagnosis", "Treatment Plan", "Treatment Cost", "Start Date", "End Date", "Room ID", "Nurse ID", "Treatment Status", "Cancellation Reason"], tablefmt="grid"))

def accept_treatment(cursor, connection, patient_id):
    query = "SELECT Treatment_ID, Diagnosis, Treatment_Plan FROM Treatment WHERE Patient_ID = %s AND Treatment_Status = 'SCHEDULED'"
    cursor.execute(query, (patient_id,))
    treatments = cursor.fetchall()

    if not treatments:
        print("No scheduled treatments to accept.")
        return

    print("Scheduled treatments:")
    print(tabulate(treatments, headers=["Treatment ID", "Diagnosis", "Treatment Plan"], tablefmt="grid"))

    treatment_id = input("Enter the Treatment ID you want to accept: ")

    query = "SELECT Treatment_ID FROM Treatment WHERE Treatment_ID = %s AND Patient_ID = %s AND Treatment_Status = 'SCHEDULED'"
    cursor.execute(query, (treatment_id, patient_id))
    treatment_exists = cursor.fetchone()

    if treatment_exists:
        query = "UPDATE Treatment SET Treatment_Status = 'ACCEPTED' WHERE Treatment_ID = %s AND Patient_ID = %s"
        cursor.execute(query, (treatment_id, patient_id))
        connection.commit()
        print("Treatment accepted successfully!")
    else:
        print("Invalid Treatment ID.")

def cancel_treatment(cursor, connection, patient_id):
    query = "SELECT Treatment_ID, Diagnosis, Treatment_Plan FROM Treatment WHERE Patient_ID = %s AND Treatment_Status = 'SCHEDULED'"
    cursor.execute(query, (patient_id,))
    treatments = cursor.fetchall()

    if not treatments:
        print("No scheduled treatments to cancel.")
        return

    print("Scheduled treatments:")
    print(tabulate(treatments, headers=["Treatment ID", "Diagnosis", "Treatment Plan"], tablefmt="grid"))

    treatment_id = input("Enter the Treatment ID you want to cancel: ")

    query = "SELECT Treatment_ID FROM Treatment WHERE Treatment_ID = %s AND Patient_ID = %s AND Treatment_Status = 'SCHEDULED'"
    cursor.execute(query, (treatment_id, patient_id))
    treatment_exists = cursor.fetchone()

    if treatment_exists:
        cancellation_reason = input("Enter the reason for cancellation: ")
        query = "UPDATE Treatment SET Treatment_Status = 'CANCELLED', Cancellation_Reason = %s WHERE Treatment_ID = %s AND Patient_ID = %s"
        cursor.execute(query, (cancellation_reason, treatment_id, patient_id))
        connection.commit()
        print("Treatment cancelled successfully!")
    else:
        print("Invalid Treatment ID.")

def view_room_and_nurse_details(cursor, patient_id):
    query = """
    SELECT t.Treatment_ID, t.Room_ID, r.RoomType, r.Cost AS Room_Cost, t.Nurse_ID, n.name AS Nurse_Name, n.shift, n.time_slot
    FROM Treatment t
    JOIN Room r ON t.Room_ID = r.RoomID
    JOIN nurses n ON t.Nurse_ID = n.id
    WHERE t.Patient_ID = %s AND (t.Treatment_Status = 'SCHEDULED' OR t.Treatment_Status = 'ACCEPTED')
    """
    cursor.execute(query, (patient_id,))
    details = cursor.fetchall()
    if not details:
        print("No scheduled or accepted treatments to show details for.")
    else:
        print("Room and Nurse details for your scheduled or accepted treatments:")
        print(tabulate(details, headers=["Treatment ID", "Room ID", "Room Type", "Room Cost", "Nurse ID", "Nurse Name", "Shift", "Time Slot"], tablefmt="grid"))


def view_total_bill(cursor, patient_id):
    query = """
    SELECT t.Treatment_ID, t.Treatment_Cost, r.Cost AS Room_Cost, (t.Treatment_Cost + r.Cost) AS Total_Cost
    FROM Treatment t
    JOIN Room r ON t.Room_ID = r.RoomID
    WHERE t.Patient_ID = %s AND (t.Treatment_Status = 'SCHEDULED' OR t.Treatment_Status = 'ACCEPTED')
    """
    cursor.execute(query, (patient_id,))
    bills = cursor.fetchall()
    if not bills:
        print("No scheduled or accepted treatments to calculate bills for.")
    else:
        print("Total bill for your scheduled or accepted treatments:")
        print(tabulate(bills, headers=["Treatment ID", "Treatment Cost", "Room Cost", "Total Cost"], tablefmt="grid"))



def patient_dashboard(cursor, connection, patient_id):
    while True:
        print("\n--- Patient Dashboard ---")
        print("1. Book Appointment")
        print("2. View Appointments")
        print("3. Cancel Appointment")
        print("4. Reschedule Appointment")
        print("5. View Treatments")
        print("6. Accept Treatment")
        print("7. Cancel Treatment")
        print("8. View Room and Nurse Details")  # New option
        print("9. View Total Bill")  # New option
        print("10. Logout")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            book_appointment(cursor, connection, patient_id)
        elif choice == 2:
            view_appointments(cursor, patient_id)
        elif choice == 3:
            cancel_appointment(cursor, connection, patient_id)
        elif choice == 4:
            reschedule_appointment(cursor, connection, patient_id)
        elif choice == 5:
            view_treatment(cursor, patient_id)
        elif choice == 6:
            accept_treatment(cursor, connection, patient_id)
        elif choice == 7:
            cancel_treatment(cursor, connection, patient_id)
        elif choice == 8:
            view_room_and_nurse_details(cursor, patient_id)
        elif choice == 9:
            view_total_bill(cursor, patient_id)
        elif choice == 10:
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="#Omgdaddy77",
        database="hospital_db"
    )
    cursor = connection.cursor()

    while True:
        print("\n--- Patient Menu ---")
        print("1. Register")
        print("2. Login")
        print("3. Back")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            register_patient(cursor, connection)
        elif choice == 2:
            login_patient(cursor, connection)
        elif choice == 3:
            break
        else:
            print("Invalid choice, please try again.")

    cursor.close()
    connection.close()
