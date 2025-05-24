import mysql.connector
from patient import register_patient, login_patient
from doctor import login_doctor
from nurse import login_nurse
from other_staff import  login_other_staff
from admin import admin_login

# Connect to the database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="#Omgdaddy77",
    database="hospital_db"
)
cursor = connection.cursor()

def doctor_actions(cursor, connection):
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

def nurse_actions(cursor, connection):
    while True:
        print("\n--- Nurse's Menu ---")
        print("1. Login")
        print("2. Back")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            login_nurse(cursor, connection)
        elif choice == 2:
            break
        else:
            print("Invalid choice, please try again.")

def other_staff_actions(cursor, connection):
    while True:
        print("\n--- Other Staff Menu ---")
        print("1. Login")
        print("2. Back")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            login_other_staff(cursor, connection)
        elif choice == 2:
            break
        else:
            print("Invalid choice, please try again.")

def patient_actions(cursor, connection):
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

def main():
    while True:
        print("\n--- Welcome to ROG Hospitals ---")
        print("1. Hey, are you an Admin?")
        print("2. Hey, are you a Doctor?")
        print("3. Hey, are you a Nurse?")
        print("4. Hey, are you Other Staff?")
        print("5. Hey, are you a Patient?")
        print("6. Exit")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            admin_login(cursor, connection)
        elif choice == 2:
            doctor_actions(cursor, connection)
        elif choice == 3:
            nurse_actions(cursor, connection)
        elif choice == 4:
            other_staff_actions(cursor, connection)
        elif choice == 5:
            patient_actions(cursor, connection)
        elif choice == 6:
            break
        else:
            print("Invalid choice, please try again.")

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()
