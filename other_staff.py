import mysql.connector
from tabulate import tabulate


def login_other_staff(cursor, connection):
    email = input("Enter your email: ")
    password = input("Enter your password: ")

    query = "SELECT * FROM other_staff WHERE email = %s AND password = %s"
    cursor.execute(query, (email, password))
    other_staff = cursor.fetchone()

    if other_staff:
        print("Login successful!")
        other_staff_dashboard(other_staff)
    else:
        print("Invalid credentials!")

def other_staff_dashboard(staff):
    print("\n--- Other Staff Dashboard ---")
    other_staff_details = [
        ["ID", staff[0]],
        ["Name", staff[1]],
        ["Role", staff[2]],
        ["Department", staff[3]],
        ["Phone", staff[4]],
        ["Email", staff[5]],
        ["Password", staff[6]],
    ]
    print(tabulate(other_staff_details, tablefmt="grid"))

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
    
    cursor.close()
    connection.close()
