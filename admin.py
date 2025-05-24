import mysql.connector
from tabulate import tabulate
import getpass

def admin_login(cursor, connection):
    while True:
        name = input("Enter admin name: ")
        password = getpass.getpass("Enter admin password: ")  # hides the password input
        query = "SELECT * FROM admin WHERE name = %s AND password = %s"
        cursor.execute(query, (name, password))
        admin = cursor.fetchone()

        if admin:
            print("Login successful!")
            admin_dashboard(cursor, connection)
            break
        else:
            print("Invalid credentials. Please try again.")

def view_all_appointments(cursor):
    query = """
    SELECT a.appointment_id, p.id AS patient_id, p.name AS patient_name, d.id AS doctor_id, d.name AS doctor_name, d.specialization AS doctor_specialization, 
           a.appointment_date, a.appointment_time, a.appointment_reason, a.medical_history, a.status, a.cancellation_reason 
    FROM appointments a
    JOIN doctors d ON a.doctor_id = d.id
    JOIN patients p ON a.patient_id = p.id
    """
    cursor.execute(query)
    appointments = cursor.fetchall()
    
    print(tabulate(appointments, headers=["Appointment ID", "Patient ID", "Patient Name", "Doctor ID", "Doctor Name", "Specialization", "Date", "Time", "Reason", "Medical History", "Status", "Cancellation Reason"], tablefmt="grid"))



def view_all_staff(cursor):
    query = "SELECT id, name, specialization, phone, email, password,years_of_experience FROM doctors"
    cursor.execute(query)
    doctors = cursor.fetchall()

    query = "SELECT id, name, shift, time_slot, phone, email, password, department FROM nurses"
    cursor.execute(query)
    nurses = cursor.fetchall()

    query = "SELECT id, name, role, department, phone, email, password FROM other_staff"
    cursor.execute(query)
    other_staff = cursor.fetchall()

    print("Doctors:")
    print(tabulate(doctors, headers=["ID", "Name", "Specialization","Phone", "Email", "Password","Years of Experience"], tablefmt="grid"))

    print("\nNurses:")
    print(tabulate(nurses, headers=["ID", "Name", "Shift","time_slot", "Phone", "Email", "Password", "Department"], tablefmt="grid"))

    print("\nOther Staff:")
    print(tabulate(other_staff, headers=["ID", "Name", "Role","Department", "Phone", "Email", "Password"], tablefmt="grid"))

def view_all_patients(cursor):
    query = "SELECT * FROM patients"
    cursor.execute(query)
    patients = cursor.fetchall()
    print(tabulate(patients, headers=["ID", "Name", "Age", "Gender", "DOB", "Address", "Phone", "Email","Password"], tablefmt="grid"))

def add_staff(cursor, connection):
    while True:
        print("Choose staff type to add:")
        print("1. Doctor")
        print("2. Nurse")
        print("3. Other Staff")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            name = input("Enter doctor's name: ")
            specialization = input("Enter doctor's specialization: ")
            phone = input("Enter doctor's phone number: ")
            email = input("Enter doctor's email: ")
            password = input("Enter doctor's password: ")
            years_of_experience=input("Enter doctor's experience: ")
            query = "INSERT INTO doctors (name, specialization, phone, email, password,years_of_experience) VALUES (%s, %s, %s, %s, %s,%s)"
            cursor.execute(query, (name, specialization, phone, email, password,years_of_experience))
            connection.commit()
            print("Doctor added successfully!")
            break
        elif choice == 2:
            name = input("Enter nurse's name: ")
            shift = input("Enter nurse's shift: ")
            time_slot = input("Enter nurse's time-slot: ")
            department=input("Enter nurse's department: ")
            phone = input("Enter nurse's phone number: ")
            email = input("Enter nurse's email: ")
            password = input("Enter nurse's password: ")
            query = "INSERT INTO nurses (name, shift,time_slot,department,phone, email, password) VALUES (%s, %s, %s, %s, %s,%s,%s)"
            cursor.execute(query, (name, shift,time_slot,department,phone, email, password))
            connection.commit()
            print("Nurse added successfully!")
            break
        elif choice == 3:
            name = input("Enter staff's name: ")
            role = input("Enter staff's role: ")
            department=input("Enter staff's department: ")
            phone = input("Enter staff's phone number: ")
            email = input("Enter staff's email: ")
            password = input("Enter staff's password: ")
            query = "INSERT INTO other_staff (name, role, department, phone, email, password) VALUES (%s, %s,%s, %s, %s, %s)"
            cursor.execute(query, (name, role,department, phone, email, password))
            connection.commit()
            print("Staff added successfully!")
            break
        else:
            print("Invalid choice. Please try again.")

def reassign_doctor_appointments(cursor, old_doctor_id, new_doctor_id):
    query = "UPDATE appointments SET doctor_id = %s WHERE doctor_id = %s"
    cursor.execute(query, (new_doctor_id, old_doctor_id))

def remove_staff(cursor, connection):
    while True:
        print("Choose staff type to remove:")
        print("1. Doctor")
        print("2. Nurse")
        print("3. Other Staff")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            attempts = 3
            while attempts > 0:
                staff_id = input("Enter the ID of the doctor to be removed: ")
                cursor.execute("SELECT * FROM doctors WHERE id = %s", (staff_id,))
                doctor = cursor.fetchone()
                if not doctor:
                    attempts -= 1
                    print(f"Invalid ID. You have {attempts} attempts left.")
                    continue

                cursor.execute("SELECT * FROM appointments WHERE doctor_id = %s", (staff_id,))
                appointments = cursor.fetchall()
                if appointments:
                    while attempts > 0:
                        new_doctor_id = input("Enter the ID of the new doctor to reassign appointments to: ")
                        cursor.execute("SELECT * FROM doctors WHERE id = %s", (new_doctor_id,))
                        new_doctor = cursor.fetchone()
                        if not new_doctor:
                            attempts -= 1
                            print(f"Invalid ID. You have {attempts} attempts left.")
                            continue
                        reassign_doctor_appointments(cursor, staff_id, new_doctor_id)
                        print(f"All appointments reassigned to doctor ID {new_doctor_id}")
                        break

                query = "DELETE FROM doctors WHERE id = %s"
                cursor.execute(query, (staff_id,))
                connection.commit()
                print("Doctor removed successfully!")
                break
            if attempts == 0:
                print("Too many invalid attempts. Returning to the main dashboard.")
                return

        elif choice == 2:
            attempts = 3
            while attempts > 0:
                staff_id = input("Enter the ID of the nurse to be removed: ")
                cursor.execute("SELECT * FROM nurses WHERE id = %s", (staff_id,))
                nurse = cursor.fetchone()
                if not nurse:
                    attempts -= 1
                    print(f"Invalid ID. You have {attempts} attempts left.")
                    continue

                # Check if the nurse has assigned treatments
                cursor.execute("SELECT * FROM Treatment WHERE Nurse_ID = %s", (staff_id,))
                treatments = cursor.fetchall()
                if treatments:
                    while attempts > 0:
                        new_nurse_id = input("Enter the ID of the new nurse to reassign duties to: ")
                        cursor.execute("SELECT * FROM nurses WHERE id = %s", (new_nurse_id,))
                        new_nurse = cursor.fetchone()
                        if not new_nurse:
                            attempts -= 1
                            print(f"Invalid ID. You have {attempts} attempts left.")
                            continue
                        cursor.execute("UPDATE Treatment SET Nurse_ID = %s WHERE Nurse_ID = %s", (new_nurse_id, staff_id))
                        connection.commit()
                        print(f"All duties reassigned to nurse ID {new_nurse_id}")
                        break

                query = "DELETE FROM nurses WHERE id = %s"
                cursor.execute(query, (staff_id,))
                connection.commit()
                print("Nurse removed successfully!")
                break
            if attempts == 0:
                print("Too many invalid attempts. Returning to the main dashboard.")
                return

        elif choice == 3:
            attempts = 3
            while attempts > 0:
                staff_id = input("Enter the ID of the staff to be removed: ")
                cursor.execute("SELECT * FROM other_staff WHERE id = %s", (staff_id,))
                other_staff = cursor.fetchone()
                if not other_staff:
                    attempts -= 1
                    print(f"Invalid ID. You have {attempts} attempts left.")
                    continue

                query = "DELETE FROM other_staff WHERE id = %s"
                cursor.execute(query, (staff_id,))
                connection.commit()
                print("Staff removed successfully!")
                break
            if attempts == 0:
                print("Too many invalid attempts. Returning to the main dashboard.")
                return

        else:
            print("Invalid choice. Please try again.")


def update_staff_details(cursor, connection):
    while True:
        print("Choose staff type to update:")
        print("1. Doctor")
        print("2. Nurse")
        print("3. Other Staff")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            attempts = 3
            while attempts > 0:
                staff_id = input("Enter the ID of the doctor to be updated: ")
                cursor.execute("SELECT * FROM doctors WHERE id = %s", (staff_id,))
                doctor = cursor.fetchone()
                if not doctor:
                    attempts -= 1
                    print(f"Invalid ID. You have {attempts} attempts left.")
                    continue

                name = input("Enter new name: ")
                specialization = input("Enter new specialization: ")
                phone = input("Enter new phone number: ")
                email = input("Enter new email: ")
                password = input("Enter new password: ")
                years_of_experience = input("Enter new experience: ")
                query = "UPDATE doctors SET name = %s, specialization = %s, phone = %s, email = %s, password = %s, years_of_experience = %s WHERE id = %s"
                cursor.execute(query, (name, specialization, phone, email, password, years_of_experience, staff_id))
                connection.commit()
                print("Doctor details updated successfully!")
                break

            if attempts == 0:
                print("Too many invalid attempts. Returning to the main dashboard.")
                return

        elif choice == 2:
            attempts = 3
            while attempts > 0:
                staff_id = input("Enter the ID of the nurse to be updated: ")
                cursor.execute("SELECT * FROM nurses WHERE id = %s", (staff_id,))
                nurse = cursor.fetchone()
                if not nurse:
                    attempts -= 1
                    print(f"Invalid ID. You have {attempts} attempts left.")
                    continue

                name = input("Enter new name: ")
                shift = input("Enter new shift: ")
                time_slot = input("Enter nurse's time-slot: ")
                department = input("Enter nurse's department: ")
                phone = input("Enter new phone number: ")
                email = input("Enter new email: ")
                password = input("Enter new password: ")
                query = "UPDATE nurses SET name = %s, shift = %s, time_slot = %s, department = %s, phone = %s, email = %s, password = %s WHERE id = %s"
                cursor.execute(query, (name, shift, time_slot, department, phone, email, password, staff_id))
                connection.commit()
                print("Nurse details updated successfully!")
                break

            if attempts == 0:
                print("Too many invalid attempts. Returning to the main dashboard.")
                return

        elif choice == 3:
            attempts = 3
            while attempts > 0:
                staff_id = input("Enter the ID of the staff to be updated: ")
                cursor.execute("SELECT * FROM other_staff WHERE id = %s", (staff_id,))
                other_staff = cursor.fetchone()
                if not other_staff:
                    attempts -= 1
                    print(f"Invalid ID. You have {attempts} attempts left.")
                    continue

                name = input("Enter new name: ")
                role = input("Enter new role: ")
                department = input("Enter new department: ")
                phone = input("Enter new phone number: ")
                email = input("Enter new email: ")
                password = input("Enter new password: ")
                query = "UPDATE other_staff SET name = %s, role = %s, department = %s, phone = %s, email = %s, password = %s WHERE id = %s"
                cursor.execute(query, (name, role, department, phone, email, password, staff_id))
                connection.commit()
                print("Staff details updated successfully!")
                break

            if attempts == 0:
                print("Too many invalid attempts. Returning to the main dashboard.")
                return

        else:
            print("Invalid choice. Please try again.")


def search_doctor_by_specialization(cursor):
    specialization = input("Enter the specialization to search: ")
    query = "SELECT id, name, specialization, phone, email, password FROM doctors WHERE specialization = %s"
    cursor.execute(query, (specialization,))
    doctors = cursor.fetchall()
    print(tabulate(doctors, headers=["ID", "Name", "Specialization", "phone", "email", "password"], tablefmt="grid"))

def search_nurse_by_time_slots(cursor):
    start_slot = input("Enter the start of the time-slot to search (e.g., 7:00 PM): ")
    end_slot = input("Enter the end of the time-slot to search (e.g., 12:00 AM): ")
    
    query = """
    SELECT id, name, shift, time_slot, phone, email, password, department
    FROM nurses
    WHERE 
    (STR_TO_DATE(SUBSTRING_INDEX(time_slot, ' - ', 1), '%h:%i %p') >= STR_TO_DATE(%s, '%h:%i %p')
    AND STR_TO_DATE(SUBSTRING_INDEX(time_slot, ' - ', 1), '%h:%i %p') <= STR_TO_DATE(%s, '%h:%i %p'))
    OR 
    (STR_TO_DATE(SUBSTRING_INDEX(time_slot, ' - ', -1), '%h:%i %p') >= STR_TO_DATE(%s, '%h:%i %p')
    AND STR_TO_DATE(SUBSTRING_INDEX(time_slot, ' - ', -1), '%h:%i %p') <= STR_TO_DATE(%s, '%h:%i %p'))
    OR
    (STR_TO_DATE(SUBSTRING_INDEX(time_slot, ' - ', 1), '%h:%i %p') <= STR_TO_DATE(%s, '%h:%i %p')
    AND STR_TO_DATE(SUBSTRING_INDEX(time_slot, ' - ', -1), '%h:%i %p') >= STR_TO_DATE(%s, '%h:%i %p'))
    """
    
    cursor.execute(query, (start_slot, end_slot, start_slot, end_slot, start_slot, end_slot))
    nurses = cursor.fetchall()
    print(tabulate(nurses, headers=["ID", "Name", "Shift", "time_slot", "phone", "email", "password", "department"], tablefmt="grid"))


def admin_dashboard(cursor, connection):
    while True:
        print("\n--- Admin Dashboard ---")
        print("1. View All Appointments")
        print("2. View All Staff")
        print("3. View All Patients")
        print("4. Add Staff")
        print("5. Remove Staff")
        print("6. Update Staff Details")
        print("7. Search Doctor by Specialization")
        print("8. Search Nurse by Shifts")
        print("9. Logout")
        choice = input("Enter your choice: ")
        if choice.isdigit():
            choice = int(choice)
            if choice == 1:
                view_all_appointments(cursor)
            elif choice == 2:
                view_all_staff(cursor)
            elif choice == 3:
                view_all_patients(cursor)
            elif choice == 4:
                add_staff(cursor, connection)
            elif choice == 5:
                remove_staff(cursor, connection)
            elif choice == 6:
                update_staff_details(cursor, connection)
            elif choice == 7:
                search_doctor_by_specialization(cursor)
            elif choice == 8:
                search_nurse_by_time_slots(cursor)
            elif choice == 9:
                break
            else:
                print("Invalid choice. Please try again.")

# Connection setup and function call
if __name__ == "__main__":
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="#Omgdaddy77",
        database="hospital_db"
    )
    cursor = connection.cursor()
    admin_login(cursor, connection)
    cursor.close()
    connection.close()

