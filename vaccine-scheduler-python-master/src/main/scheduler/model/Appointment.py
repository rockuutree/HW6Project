import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Appointment:
    def __init__(self, time, patient,administrator,  vaccine):
        self.time = time
        self.patient = patient
        self.administrator = administrator
        self.vaccine = vaccine

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = "SELECT Time, Patient, Administrator, Vaccine FROM Appointments WHERE Time = %s AND Patient = %s AND Administrator = %s AND Vaccine = %ss"
        try:
            cursor.execute(get_caregiver_details, self.username)
            for row in cursor:
                self.time = row['Time']
                self.patient = row['Patient']
                self.administrator = row['Administrator']
                self.vaccine = row['Vaccine']
                return self
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None

    def get_time(self):
        return self.time

    def get_patient(self):
        return self.patient

    def get_administrator(self):
        return self.administrator

    def get_vaccine(self):
        return self.vaccine


    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_caregivers = "INSERT INTO Caregivers VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_caregivers,
                           (self.time, self.patient, self.administrator,  self.vaccine))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    def show_appointments(user, patient) -> int:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        retrieve_appointments = "SELECT uid, vaccine, time, patient, administrator FROM Appointments WHERE " + \
            ("patient = %s" if patient else "administrator = %s" + " ORDER BY uid")

        try:
            cursor.execute(retrieve_appointments, user)
            count = 0
            for row in cursor:
                count +=1
                print(
                    f'Appointment ID: {row["uid"]}, Vaccine: {row["vaccine"]}, Time: {row["time"]}, {"Administrator" if patient else "Patient"}: {row["administrator" if patient else "patient"]}') 
            return count
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()    

    def get_appointment(uid):
 
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        retrieve_appointment = "SELECT Time, Administrator, Patient, Vaccine FROM Appointments WHERE uid = %s"
        
        try:
            cursor.execute(retrieve_appointment, uid)
            for row in cursor:
                return Appointment(row["Time"], row["Administrator"], row["Patient"], row["Vaccine"])
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()

    def delete_appointment(uid) -> int:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        delete = "DELETE FROM Appointments WHERE uid = %s"
        
        try:
            cursor.execute(delete,uid)
            conn.commit()
            return cursor.rowcount
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        
