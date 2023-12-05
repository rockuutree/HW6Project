from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Availabilities import Availabilities
from model.Appointment import Appointment
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import uuid
import re


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def strong_password(password: str) -> bool:
    """
    Extra Credit
    """
    return re.match(
        '^(?=.{8,}$)(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@?#])', password) is not None

def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if (len(tokens) != 3):
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]

    #check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return
    
    #check 3: strong password
    if (not strong_password(password)):
        print("Password is weak")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ",  username)


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False




def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print(e)
        return

    if patient is None:
        print("Login failed.")
        return
    else:
        current_patient = patient
        print("Logged in as ", username)


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver

# Both patients and caregivers can perform this operation. 
# Output the username for the caregivers that are available for the date, along with the number of available doses left for each vaccine. Order by the username of the caregiver. Separate each attribute with a space. 
# If no user is logged in, print “Please login first!”.
# For all other errors, print "Please try again!".


def search_caregiver_schedule(tokens):
    """
    Part 2
    """

    #  search_caregiver_schedule <date>
    #  check 1: check if the current logged-in user 
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        #Output the username for the caregivers that are available for the date
        print("Caregivers:")
        if(Availabilities.caregiver_available(d) == 0):
            print("Please try again")
        # number of available doses left for each vaccine
        print("Vaccines")
        Vaccine.select_vaccines()
    except pymssql.Error as e:
        print("Please try again!")
        return
    pass
    

#reserve <date> <vaccine>
#Patients perform this operation to reserve an appointment.
#Caregivers can only see a maximum of one patient per day, meaning that if the reservation went through, the caregiver is no longer available for that date.
#If there are available caregivers, choose the caregiver by alphabetical order and print “Appointment ID: {appointment_id}, Caregiver username: {username}” for the reservation.
#If there’s no available caregiver, print “No Caregiver is available!”. If not enough vaccine doses are available, print "Not enough available doses!".
#If no user is logged in, print “Please login first!”. If the current user logged in is not a patient, print “Please login as a patient!”.
#For all other errors, print "Please try again!".


def reserve(tokens):

    """
    Part 2
    """

    global current_caregiver
    global current_patient

    #Checks if the user is logged in first
    if current_caregiver is None and current_patient is None:
        print("Please try again")
        return
    #  check 1: check if the current is a patient 
    if current_patient is None:
        print("Please login as patient first!")
        return
    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    vaccine = tokens[2]

    try:
        d = datetime.date(year, month, day)
        administrator = Availabilities.caregiver_available(d)
        if administrator is None:
            print("No Caregiver is available!")
            return
        
        try:
            vaccine_avail = Vaccine.ret_doses(vaccine)
            if vaccine_avail is None:
                print("Vaccine is not available")
                return
            vaccine_avail.decrease_available_doses(1)
        except ValueError:
            print("Not enough available doses!")

        uid = uuid.uuid1()

        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        remove_availability = "DELETE FROM Availabilities WHERE Time = %s AND Adminstrator = %s"  
        add_appoint = "INSERT INTO Appointments (uid, Patient, Adminstrator, Vaccine, Time) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(remove_availability, (d, administrator))
        cursor.execute(
            add_appoint, (uid, current_patient.username, administrator, vaccine, d))
        conn.commit()
        print("Successful Reservation. Appointment information:")
        print(f'Appointment {uid}, Caregiver username: {administrator}')
    except Exception as e:
        print("Please Try Again")
        print(e)
        return




def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    Extra Credit
    """
    #  check 1: check if the user is logged-in
    global current_caregiver
    global current_patient
    
    if current_patient is None and current_caregiver is None:
        print("Please log in!")
        return

    # check 2: the length for tokens need to be exactly 2 
    if len(tokens) != 2:
        print("Please log in!")
        return 
    
    # check 3: Cancel appointment & Return doses to original

    try:
        uid = tokens[1]
        appointment = Appointment.get_appointment(uid)

        if(Appointment.delete_appointment(uid) == 0):
            print("Appointment doesn't exist")
            return
        
        vaccine = Vaccine.get_vaccine_name(appointment.vaccine)

        try:
            vaccine.increase_available_doses(1)
        except:
            print("Please try again!");
            return
    except:
        print("Please try again!")
        return
    print("Cancelled the Appointment")




def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    """
    Part 2
    """

    global current_caregiver
    global current_patient

    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    
    try:
        user: Patient | Caregiver = current_patient if current_patient is not None else current_caregiver
        if(Appointment.show_appointments(user.get_username(), current_patient == user) == 0):
            print("No appointments")
    except:
        print("Please try again!")


def logout(tokens):
    """
    Part 2
    """

    try:
        global current_caregiver
        global current_patient
        if current_caregiver is None and current_patient is None:
            print("Please login first.")
        current_caregiver = None
        current_patient = None
        print("Successfully logged out!")
    except:
        print("Please try again!")
        return

def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
