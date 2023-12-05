import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
from model.Appointment import Appointment


class Availabilities:
    def __init__(self, time, administrator):
        self.time = time
        self.administrator = administrator

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_availabilities_details = "SELECT Time, Administrator, Scheduler, Complete FROM Availabilities where Time = %s"
        try:
            cursor.execute(get_availabilities_details, self.time)
            for row in cursor:
                self.time = row['Time']
                self.administrator = row['Administrator']
                self.schedule = row['Schedule']
                self.complete = row['Complete']
                return self
              # print("Availabilities not found")
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None

    def get_time(self):
        return self.time

    def get_administrator(self):
        return self.administrator

    def get_schedule(self):
        return self.schedule

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availabilities = "INSERT INTO Availabilities VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_availabilities, (self.time, self.administrator, self.complete, self.schedule))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    def caregiver_available(date):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        select_caregivers = "SELECT Administrator FROM Availabilities WHERE Time = %s ORDER By Administrator"
        #Query the rows for availabilities
        try:
            cursor.execute(select_caregivers, date)
            for row in cursor:
                return row["Administrator"]
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

