import json
import gspread
from datetime import datetime
from gspread.exceptions import WorksheetNotFound, SpreadsheetNotFound
import logging

# Setup logging for errors
logging.basicConfig(level=logging.ERROR)

def get_current_time():
    """
    Returns the current time and date in the required format.
    """
    now = datetime.now()
    return now.strftime("%H:%M:%S"), now.strftime("%d/%m/%Y")

class GoogleSheet:
    DATA_SHEET_NAME = "DATA"

    def __init__(self):
        self.sheet = None
        self.google_sheet = None
        try:
            self.google_sheet = gspread.service_account(filename='../service_account.json')
        except Exception as e:
            logging.error(f"Error initializing Google Sheets client: {e}")

    def open_sheet(self, sheet_name):
        """
        Opens the Google Sheet with the given name.
        If the sheet is not found, it will create a new one.
        """
        try:
            if not self.sheet:
                self.sheet = self.google_sheet.open(sheet_name)
        except SpreadsheetNotFound:
            self.create_data(sheet_name)

    def push(self, sheet_name, finger_id):
        """
        Pushes attendance information for the given finger_id to the corresponding sheet.
        Creates a new worksheet if the current date's sheet doesn't exist.
        """
        try:
            self.open_sheet(sheet_name)
            time, date = get_current_time()
            student_id, student_name = self.get_information(sheet_name, finger_id)

            if student_id and student_name:
                sheet_title = f"Điểm danh ngày {date}"
                try:
                    work_sheet = self.sheet.worksheet(sheet_title)
                except WorksheetNotFound:
                    work_sheet = self.sheet.add_worksheet(sheet_title, rows=130, cols=3)

                values = [[student_id, student_name, time]]
                work_sheet.update(f'A{finger_id}:C{finger_id}', values)  # Batch update for efficiency
        except Exception as e:
            logging.error(f"Error pushing data: {e}")

    def create_data(self, sheet_name, finger_id=None, student_name=None):
        """
        Creates a new Google Sheet if not found and adds a 'DATA' worksheet.
        If student info is provided, it updates the 'DATA' sheet with the student's details.
        """
        try:
            self.sheet = self.google_sheet.open(sheet_name)
        except SpreadsheetNotFound:
            self.sheet = self.google_sheet.create(sheet_name)
            self.sheet.add_worksheet(self.DATA_SHEET_NAME, rows=130, cols=2)

            # Share the sheet with email addresses from email.json
            with open('../email.json') as f:
                data = json.load(f)
                email_list = data.get("emails", [])

            for email in email_list:
                self.sheet.share(email, perm_type='user', role='writer')

        if finger_id and student_name:
            self.update_data_sheet(finger_id, student_name)

    def update_data_sheet(self, finger_id, student_name):
        """
        Updates the 'DATA' worksheet with the given finger_id and student_name.
        """
        try:
            data_base = self.sheet.worksheet(self.DATA_SHEET_NAME)
            data_base.update(f'A{finger_id}:B{finger_id}', [[finger_id, student_name]])
        except Exception as e:
            logging.error(f"Error updating data sheet: {e}")

    def delete(self, sheet_name, finger_id):
        """
        Deletes a student's data by clearing their row in the 'DATA' worksheet.
        """
        try:
            self.open_sheet(sheet_name)
            data_base = self.sheet.worksheet(self.DATA_SHEET_NAME)
            data_base.update(f'A{finger_id}:B{finger_id}', [["", ""]])
        except Exception as e:
            logging.error(f"Error deleting data: {e}")

    def get_information(self, sheet_name, finger_id):
        try:
            sheet = self.google_sheet.open(sheet_name)
            data_base = sheet.worksheet("DATA")
            # Ensure finger_id is consistently a string
            finger_id = str(finger_id)  # or int(finger_id) depending on your data type

            student_id = data_base.cell(int(finger_id), 1).value
            student_name = data_base.cell(int(finger_id), 2).value

            return student_id, student_name
        except Exception as e:
            logging.error(f"Error getting student information: {e}")
            return None, None
