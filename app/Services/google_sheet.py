import json
import gspread
from datetime import datetime
from gspread.exceptions import WorksheetNotFound
from gspread.exceptions import SpreadsheetNotFound

def get_current_time():
    date_time = datetime.now()
    month = date_time.month
    day = date_time.day
    year = date_time.year
    time = date_time.strftime("%H:%M:%S")
    return time, day, month, year

class GoogleSheet:
    def __init__(self):
        self.sheet = None
        try:
            self.google_sheet = gspread.service_account(filename='service_account.json')
        except FileNotFoundError as e:
            print(f"Error loading service account: {e}")

    def push(self, sheet_name, finger_id):
        try:
            self.sheet = self.google_sheet.open(sheet_name)

            time, day, month, year = get_current_time()
            current_time = str(time)
            current_date = str(day) + "/" + str(month) + "/" + str(year)

            student_id, student_name = self.get_information(finger_id)

            try:
                work_sheet = self.sheet.worksheet("Điểm danh ngày " + str(current_date))
            except WorksheetNotFound:
                work_sheet = self.sheet.add_worksheet("Điểm danh ngày " + str(current_date), rows=130, cols=3)

            work_sheet.update_cell(finger_id, 1, student_id)
            work_sheet.update_cell(finger_id, 2, student_name)
            work_sheet.update_cell(finger_id, 3, current_time)
        except SpreadsheetNotFound:
            self.sheet = self.google_sheet.create(sheet_name)
            self.sheet.add_worksheet("DATA", 130, 3)

            with open('email.json') as f:
                data = json.load(f)
                email_list = data.get("emails", [])

            for email in email_list:
                self.sheet.share(email, perm_type='user', role='writer')

            return "JUST_CREATED_SHEET"

    def create_data(self, sheet_name, finger_id=None, student_name=None):
        try:
            self.sheet = self.google_sheet.open(sheet_name)
            return "ALREADY_EXISTED_SHEET"
        except SpreadsheetNotFound:
            self.sheet = self.google_sheet.create(sheet_name)
            self.sheet.add_worksheet("DATA", 130, 3)

            with open('email.json') as f:
                data = json.load(f)
                email_list = data.get("emails", [])

            for email in email_list:
                self.sheet.share(email, perm_type='user', role='writer')

            if finger_id and student_name:
                data_base = self.sheet.worksheet("DATA")
                data_base.update_cell(finger_id+1, 2, finger_id)
                data_base.update_cell(finger_id+1, 3, student_name)

            return "JUST_CREATED"

    def get_information(self, finger_id):
        try:
            data_base = self.sheet.worksheet("DATA")
            student_id = data_base.cell(finger_id+1, 2).value
            student_name = data_base.cell(finger_id+1, 3).value
            return student_id, student_name
        except SpreadsheetNotFound:
            return "NOT_FOUND_STUDENT"