import mysql.connector
from tabulate import tabulate
from datetime import datetime
import re

def login_nurse(cursor, connection):
    email = input("Enter your email: ")
    password = input("Enter your password: ")

    query = "SELECT * FROM nurses WHERE email = %s AND password = %s"
    cursor.execute(query, (email, password))
    nurse = cursor.fetchone()

    if nurse:
        print("Login successful!")
        nurse_dashboard(nurse)
    else:
        print("Invalid credentials!")

def nurse_dashboard(nurse):
    print("\n--- Nurse Dashboard ---")
    nurse_details = [
        ["ID", nurse[0]],        
        ["Name", nurse[1]],
        ["Shift", nurse[2]],
        ["Phone", nurse[3]],
        ["Email", nurse[4]],
        ["Password", nurse[5]],
        ["Department", nurse[6]],
        ["Time-Slot", nurse[7]]
    ]
    print(tabulate(nurse_details, tablefmt="grid"))

if __name__ == "__main__":
    # Connect to the database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="#Omgdaddy77",
        database="hospital_db"
    )
    cursor = connection.cursor()
    while True:
        print("\n--- Nurse Menu ---")
        print("1. Login")
        print("2. Back")
        choice = int(input("Enter your choice: "))

        if choice == 1:
            login_nurse(cursor, connection)
        elif choice == 2:
            break
        else:
            print("Invalid choice, please try again.")
    
    cursor.close()
    connection.close()
