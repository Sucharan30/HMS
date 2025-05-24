import mysql.connector
from tabulate import tabulate
import re
from datetime import datetime

def login_doctor(cursor, connection):
    attempts = 3
    while attempts > 0:

        email = input("Enter your email: ")
        password = input("Enter your password: ")
        
        query = "SELECT * FROM doctors WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        doctor = cursor.fetchone()
        
        if doctor:
            print("Login successful!")
            doctor_dashboard(cursor, connection, doctor[0])  # pass doctor ID
            break
        else:
            attempts -= 1
            print(f"Invalid credentials. You have {attempts} attempts left.")

    print("Returning to Doctors's Menu.")

def view_appointments(cursor, doctor_id):
    query = "SELECT * FROM appointments WHERE doctor_id = %s"
    cursor.execute(query, (doctor_id,))
    appointments = cursor.fetchall()

    print("Your appointments:")
    print(tabulate(appointments, headers=["Appointment ID", "Patient ID", "Doctor ID", "Date", "Time", "Appointment Reason","Medical History","Status", "Cancellation Reason"], tablefmt="grid"))

def accept_appointment(cursor, connection, doctor_id):
    query = "SELECT appointment_id FROM appointments WHERE doctor_id = %s"
    cursor.execute(query, (doctor_id,))
    appointments = cursor.fetchall()
    appointment_ids = [str(appointment[0]) for appointment in appointments]

    attempts = 3
    while attempts > 0:
        appointment_id = input("Enter the appointment ID you want to accept: ")
        if appointment_id in appointment_ids:
            query = "UPDATE appointments SET status = 'Accepted', cancellation_reason = NULL WHERE appointment_id = %s AND doctor_id = %s"
            cursor.execute(query, (appointment_id, doctor_id))
            connection.commit()
            print("Appointment accepted successfully!")
            return
        else:
            attempts -= 1
            print(f"Invalid appointment ID. You have {attempts} attempts left.")

    print("Too many invalid attempts. Returning to Doctor's Dashboard.")


def cancel_appointment(cursor, connection, doctor_id):
    query = "SELECT appointment_id FROM appointments WHERE doctor_id = %s"
    cursor.execute(query, (doctor_id,))
    appointments = cursor.fetchall()
    appointment_ids = [str(appointment[0]) for appointment in appointments]

    attempts = 3
    while attempts > 0:
        appointment_id = input("Enter the appointment ID you want to cancel: ")
        if appointment_id in appointment_ids:
            cancellation_reason = input("Enter the reason for cancellation: ")
            query = "UPDATE appointments SET status = 'Cancelled', cancellation_reason = %s WHERE appointment_id = %s AND doctor_id = %s"
            cursor.execute(query, (cancellation_reason, appointment_id, doctor_id))
            connection.commit()
            print("Appointment cancelled successfully!")
            break
        else:
            attempts -= 1
            print(f"Invalid appointment ID. You have {attempts} attempts left.")

    print("Too many invalid attempts. Returning to Doctor's Dashboard.")

def view_patient_details(cursor, doctor_id):
    query = """
    SELECT patients.id, patients.name, patients.age, patients.gender, patients.address, patients.phone, patients.email 
    FROM appointments 
    JOIN patients ON appointments.patient_id = patients.id 
    WHERE appointments.doctor_id = %s
    """
    cursor.execute(query, (doctor_id,))
    patients = cursor.fetchall()

    print("Your patients:")
    print(tabulate(patients, headers=["Patient ID", "Name", "Age", "Gender", "Address", "Phone", "Email"], tablefmt="grid"))

def add_treatment(cursor, connection, doctor_id):
    query = "SELECT appointment_id, patient_id FROM appointments WHERE doctor_id = %s AND status = 'Accepted'"
    cursor.execute(query, (doctor_id,))
    appointments = cursor.fetchall()

    if not appointments:
        print("No patients with accepted appointments.")
        return

    print("Patients with accepted appointments:")
    print(tabulate(appointments, headers=["Appointment ID", "Patient ID"], tablefmt="grid"))

    attempts = 3
    while attempts > 0:
        appointment_id = input("Enter the Appointment ID to add treatment: ")
        patient_id = input("Enter the Patient ID to add treatment: ")

        # Check if the appointment is valid and the patient exists
        query = "SELECT id FROM patients WHERE id = %s"
        cursor.execute(query, (patient_id,))
        patient_exists = cursor.fetchone()

        query = "SELECT appointment_id FROM appointments WHERE appointment_id = %s"
        cursor.execute(query, (appointment_id,))
        appointment_exists = cursor.fetchone()

        query = "SELECT appointment_id FROM Treatment WHERE appointment_id = %s"
        cursor.execute(query, (appointment_id,))
        treatment_exists = cursor.fetchone()

        if patient_exists and appointment_exists and not treatment_exists:
            diagnosis = input("Enter Diagnosis: ")
            treatment_plan = input("Enter Treatment Plan: ")
            treatment_cost = float(input("Enter Treatment Cost: "))
            start_date = input("Enter Start Date (YYYY-MM-DD): ")
            end_date = input("Enter End Date (YYYY-MM-DD): ")

            # Select Room ID
            cursor.execute("SELECT RoomID, RoomType, Cost FROM Room WHERE AvailabilityStatus = 'Available'")
            rooms = cursor.fetchall()
            print("Available rooms:")
            print(tabulate(rooms, headers=["Room ID", "Room Type", "Cost"], tablefmt="grid"))

            room_attempts = 3
            while room_attempts > 0:
                room_id = input("Enter the Room ID to allot: ")
                if any(room_id == str(room[0]) for room in rooms):
                    break
                else:
                    room_attempts -= 1
                    print(f"Invalid Room ID. You have {room_attempts} attempts left.")

            if room_attempts == 0:
                print("Too many invalid attempts. Returning to Doctor's Dashboard.")
                return

            # Select Nurse ID
            cursor.execute("SELECT id, name, shift, time_slot FROM nurses")
            nurses = cursor.fetchall()
            print("Available nurses:")
            print(tabulate(nurses, headers=["Nurse ID", "Nurse Name", "Nurse Shift", "Nurse time slot"], tablefmt="grid"))

            nurse_attempts = 3
            while nurse_attempts > 0:
                nurse_id = input("Enter the Nurse ID to allot: ")
                if any(nurse_id == str(nurse[0]) for nurse in nurses):
                    break
                else:
                    nurse_attempts -= 1
                    print(f"Invalid Nurse ID. You have {nurse_attempts} attempts left.")

            if nurse_attempts == 0:
                print("Too many invalid attempts. Returning to Doctor's Dashboard.")
                return

            query = "INSERT INTO Treatment (Patient_ID, Doctor_ID, Diagnosis, Treatment_Plan, Treatment_Cost, Start_Date, End_Date, appointment_id, Room_ID, Nurse_ID, Treatment_Status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'SCHEDULED')"
            cursor.execute(query, (patient_id, doctor_id, diagnosis, treatment_plan, treatment_cost, start_date, end_date, appointment_id, room_id, nurse_id))
            connection.commit()
            print("Treatment added successfully!")
            return
        else:
            attempts -= 1
            print(f"Invalid Patient ID or Appointment ID, or treatment already exists for this appointment. You have {attempts} attempts left.")

    print("Too many invalid attempts. Returning to Doctor's Dashboard.")

def view_treatments(cursor, doctor_id):
    query = """
    SELECT t.Treatment_ID, t.Patient_ID, p.name AS Patient_Name, t.Diagnosis, t.Treatment_Plan, t.Treatment_Cost, t.Start_Date, t.End_Date, 
           t.appointment_id, t.Room_ID, t.Nurse_ID, t.Treatment_Status, t.cancellation_reason 
    FROM Treatment t
    JOIN patients p ON t.Patient_ID = p.id
    JOIN Room r ON t.Room_ID = r.RoomID
    JOIN nurses n ON t.Nurse_ID = n.id
    WHERE t.Doctor_ID = %s
    """
    cursor.execute(query, (doctor_id,))
    treatments = cursor.fetchall()

    if not treatments:
        print("No treatments found for this doctor.")
    else:
        print("Your treatments:")
        print(tabulate(treatments, headers=["Treatment ID", "Patient ID", "Patient Name", "Diagnosis", "Treatment Plan", "Treatment Cost", "Start Date", "End Date", "Appointment ID", "Room ID", "Nurse ID","Treatment Status", "Cancellation Reason"], tablefmt="grid"))


def cancel_treatment(cursor, connection, doctor_id):
    query = "SELECT Treatment_ID, Patient_ID, Diagnosis, Treatment_Plan FROM Treatment WHERE Doctor_ID = %s"
    cursor.execute(query, (doctor_id,))
    treatments = cursor.fetchall()

    if not treatments:
        print("No treatments found for this doctor.")
        return

    print("Your treatments:")
    print(tabulate(treatments, headers=["Treatment ID", "Patient ID", "Diagnosis", "Treatment Plan"], tablefmt="grid"))

    attempts = 3
    while attempts > 0:
        treatment_id = input("Enter the Treatment ID you want to cancel: ")
        query = "SELECT Treatment_ID FROM Treatment WHERE Treatment_ID = %s AND Doctor_ID = %s"
        cursor.execute(query, (treatment_id, doctor_id))
        treatment_exists = cursor.fetchone()

        if treatment_exists:
            # Fetch and display available doctors
            cursor.execute("SELECT id, name, specialization FROM doctors WHERE id != %s", (doctor_id,))
            available_doctors = cursor.fetchall()
            print("Available doctors for reassignment:")
            print(tabulate(available_doctors, headers=["Doctor ID", "Name", "Specialization"], tablefmt="grid"))

            new_doctor_id = input("Enter the ID of the new doctor to reassign treatment to: ")
            query = "SELECT id FROM doctors WHERE id = %s"
            cursor.execute(query, (new_doctor_id,))
            new_doctor_exists = cursor.fetchone()

            if new_doctor_exists:
                query = "UPDATE Treatment SET Doctor_ID = %s WHERE Treatment_ID = %s"
                cursor.execute(query, (new_doctor_id, treatment_id))
                connection.commit()
                print(f"Treatment reassigned to doctor ID {new_doctor_id} and cancelled successfully!")
                return
            else:
                attempts -= 1
                print(f"Invalid new doctor ID. You have {attempts} attempts left.")
        else:
            attempts -= 1
            print(f"Invalid Treatment ID. You have {attempts} attempts left.")

    print("Too many invalid attempts. Returning to Doctor's Dashboard.")



def doctor_dashboard(cursor, connection, doctor_id):
    while True:
        print("\n--- Doctor's Dashboard ---")
        print("1. View Appointments")
        print("2. Accept Appointment")
        print("3. Cancel Appointment")
        print("4. View Patient Details")
        print("5. Add Treatment")
        print("6. View Treatments")
        print("7. Cancel Treatment")
        print("8. Logout")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            view_appointments(cursor, doctor_id)
        elif choice == 2:
            accept_appointment(cursor, connection, doctor_id)
        elif choice == 3:
            cancel_appointment(cursor, connection, doctor_id)
        elif choice == 4:
            view_patient_details(cursor, doctor_id)
        elif choice == 5:
            add_treatment(cursor, connection, doctor_id)
        elif choice == 6:
            view_treatments(cursor, doctor_id)
        elif choice == 7:
            cancel_treatment(cursor, connection, doctor_id)
        elif choice == 8:
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
        print("\n--- Doctor's Menu ---")
        print("1. Login")
        print("2. Back")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            login_doctor(cursor, connection)
        elif choice == 2:
            break
        else:
            print("Invalid choice, please try again.")

    cursor.close()
    connection.close()
