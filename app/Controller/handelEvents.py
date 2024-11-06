from app.Model.devices import Camera
from PyQt5.QtWidgets import QMessageBox
from app.Model.devices import FingerPrint
import app.Model.file_manager as FileManager
from app.Services.google_sheet import GoogleSheet
import logging
import time

# Setup logging for errors
logging.basicConfig(level=logging.ERROR)

class ViewEvents:
    def __init__(self, ui):
        self.ui = ui
        self.camera = None
        self.fingerPrint = None
        self.google_sheet = GoogleSheet()
        self.gui_init()
        self.events_connect()
        self.last_checkin_time = {}

    def gui_init(self):
        """
        Initializes the GUI elements.
        """
        self.ui.fingerPrintCOMInput.setEnabled(False)
        self.ui.stopButton.setEnabled(False)
        self.ui.fingerPrintView.setVisible(False)
        self.ui.cameraView.setVisible(True)

    def events_connect(self):
        """
        Connects UI buttons and selectors to their corresponding event handlers.
        """
        try:
            self.ui.stopButton.clicked.connect(self.stop_button_clicked)
            self.ui.startButton.clicked.connect(self.start_button_clicked)
            self.ui.addFingerButton.clicked.connect(self.add_finger_button_clicked)
            self.ui.modelSelectButton.clicked.connect(self.model_select_button_clicked)
            self.ui.deleteFingerButton.clicked.connect(self.delete_finger_button_clicked)
            self.ui.registerTypeSelector.currentIndexChanged.connect(self.register_type_changed)
        except Exception as e:
            logging.error(f"Error connecting events: {e}")

    def enable_buttons(self, enable_start: bool, enable_stop: bool):
        """
        Enables or disables the start and stop buttons and related controls.
        """
        self.ui.startButton.setEnabled(enable_start)
        self.ui.stopButton.setEnabled(enable_stop)
        self.ui.cameraSelector.setEnabled(enable_start)
        self.ui.modelPathInput.setEnabled(enable_start)
        self.ui.classNameInput.setEnabled(enable_start)
        self.ui.modelSelectButton.setEnabled(enable_start)
        self.ui.fingerPrintCOMInput.setEnabled(enable_start)
        self.ui.registerTypeSelector.setEnabled(enable_start)

    def start_button_clicked(self):
        """
        Starts the camera or fingerprint capture based on the selected registration type.
        """
        class_name = self.ui.classNameInput.text()
        if not class_name:
            QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng nhập tên lớp!")
            return

        if self.ui.registerTypeSelector.currentIndex() == 0:  # Camera mode
            if not self.ui.modelPathInput.text():
                QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng nhập đường dẫn mô hình!")
                return
            self.start_camera()
        else:  # Fingerprint mode
            if not self.ui.fingerPrintCOMInput.text():
                QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng nhập cổng COM!")
                return
            self.start_fingerprint()

    def start_camera(self):
        """
        Starts the camera for registration.
        """
        try:
            self.camera = Camera(self.ui.cameraSelector.currentIndex())
            self.camera.update_image_signal.connect(self.on_update_image_view)
            self.camera.send_information_signal.connect(self.information_signal_from_camera)
            self.camera.start()
            self.enable_buttons(False, True)
        except Exception as e:
            QMessageBox.warning(self.ui, "Lỗi", str(e))
            self.stop_button_clicked()

    def start_fingerprint(self):
        """
        Starts the fingerprint capture for registration.
        """
        try:
            self.fingerPrint = FingerPrint(self.ui.fingerPrintCOMInput.text())
            self.fingerPrint.finger_print_read_signal.connect(self.on_fingerprint_read)
            self.fingerPrint.start()
            self.enable_buttons(False, True)
        except Exception as e:
            QMessageBox.warning(self.ui, "Lỗi", str(e))

    def stop_button_clicked(self):
        """
        Stops the camera or fingerprint process.
        """
        self.enable_buttons(True, False)

        if self.ui.registerTypeSelector.currentIndex() == 0 and self.camera:
            self.camera.stop()
            self.camera = None
        elif self.fingerPrint:
            self.fingerPrint.stop()
            self.fingerPrint = None

    def model_select_button_clicked(self):
        """
        Opens a file dialog to select the model path.
        """
        model_path = FileManager.load_folder()
        if model_path:
            self.ui.modelPathInput.setText(model_path)

    def add_finger_button_clicked(self):
        """
        Adds a new fingerprint to the system.
        """
        IDs = self.ui.addFingerIDInput.text()
        name = self.ui.studentNameInput.text()

        if not IDs:
            QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng nhập ID!")
            return

        try:
            self.fingerPrint.send("a"+IDs)
            self.google_sheet.create_data(self.ui.classNameInput.text(), IDs, name)
        except Exception as e:
            QMessageBox.warning(self.ui, "Lỗi", str(e))

    def delete_finger_button_clicked(self):
        """
        Deletes an existing fingerprint from the system.
        """
        IDs = self.ui.deleteFingerIDInput.text()

        if not IDs:
            QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng nhập ID!")
            return

        try:
            if self.fingerPrint:
                self.fingerPrint.send("r" + IDs)
                self.google_sheet.delete(self.ui.classNameInput.text(), IDs)
            else:
                QMessageBox.warning(self.ui, "Lỗi", "Thiết bị vân tay chưa được khởi tạo!")
        except Exception as e:
            QMessageBox.warning(self.ui, "Lỗi", str(e))

    def register_type_changed(self):
        """
        Toggles the UI between camera and fingerprint modes based on the register type selected.
        """
        try:
            if self.ui.registerTypeSelector.currentIndex() == 0:  # Camera mode
                self.ui.modelPathInput.setEnabled(True)
                self.ui.cameraSelector.setEnabled(True)
                self.ui.modelSelectButton.setEnabled(True)
                self.ui.fingerPrintCOMInput.setEnabled(False)
                self.ui.cameraView.setVisible(True)
                self.ui.fingerPrintView.setVisible(False)
            else:  # Fingerprint mode
                self.ui.modelPathInput.setEnabled(False)
                self.ui.cameraSelector.setEnabled(False)
                self.ui.modelSelectButton.setEnabled(False)
                self.ui.fingerPrintCOMInput.setEnabled(True)
                self.ui.cameraView.setVisible(False)
                self.ui.fingerPrintView.setVisible(True)
        except AttributeError as e:
            logging.error(f"Error in register type change: {e}")
            QMessageBox.warning(self.ui, "Lỗi", "Có lỗi xảy ra trong quá trình chuyển đổi loại đăng ký.")

    def on_fingerprint_read(self, message):
        """
        Handles messages received from the fingerprint device.
        """
        message = message.strip()
        if message == "FINGER_ADDED":
            QMessageBox.information(self.ui, "Thông báo", "Vân tay đã được thêm!")
            self.ui.addFingerIDInput.setText("")
            self.ui.studentNameInput.setText("")
        elif message == "FINGER_DELETED":
            QMessageBox.information(self.ui, "Thông báo", "Vân tay đã được xóa!")
            self.ui.deleteFingerIDInput.setText("")
        elif message == "FINGER_ID_NOT_NULL":
            QMessageBox.warning(self.ui, "Cảnh báo", "ID đã tồn tại!")
        elif message == "FINGER_ID_NULL":
            self.ui.idValue.setText("ID không tồn tại!")
            self.ui.nameValue.setText("")
        elif message == "INVALID_ID":
            QMessageBox.warning(self.ui, "Cảnh báo", "ID không hợp lệ!")
            self.clear_fingerprint_inputs()
        elif message == "FINGER_EMPTY":
            QMessageBox.warning(self.ui, "Cảnh báo", "Vân tay không tồn tại!")
        elif message.isdigit():
            self.handle_valid_fingerprint(message)

    def handle_valid_fingerprint(self, IDs):
        """
        Handles valid fingerprint ID by displaying the associated information and
        ensuring that the push to Google Sheets only happens once within a set time period.
        """
        # Lấy thời gian hiện tại
        current_time = time.time()
        cooldown_period = 300  # 5 phút

        # Kiểm tra nếu ID đã được điểm danh trong vòng thời gian cooldown
        if IDs in self.last_checkin_time:
            elapsed_time = current_time - self.last_checkin_time[IDs]
            if elapsed_time < cooldown_period:
                print(f"ID {IDs} đã được điểm danh gần đây. Bỏ qua.")
                return

        # Cập nhật thời gian điểm danh của ID
        self.last_checkin_time[IDs] = current_time

        # Cập nhật UI và gửi thông tin đến Google Sheets
        self.ui.idValue.setText(IDs)
        student_name = self.google_sheet.get_information(self.ui.classNameInput.text(), IDs)[1]
        self.ui.nameValue.setText(student_name)

        # Gửi request điểm danh
        self.google_sheet.push(self.ui.classNameInput.text(), IDs)

    def clear_fingerprint_inputs(self):
        """
        Clears fingerprint input fields after an operation.
        """
        self.ui.deleteFingerIDInput.setText("")
        self.ui.addFingerIDInput.setText("")

    def on_update_image_view(self, frame):
        """
        Updates the camera view with the current frame.
        """
        self.ui.imageViewFrame.setPixmap(frame)

    def information_signal_from_camera(self, information):
        """
        Handles the information signal received from the camera with checks to avoid multiple requests.
        """
        try:
            data = information.split(" ")
            if len(data) > 1:
                IDs = str(int(data[0]) + 1)
                name = " ".join(data[1:])
            else:
                IDs = str(int(data[0]) + 1)
                name = ""

            self.ui.idValue_2.setText(IDs)
            self.ui.nameValue_2.setText(name)

            # Kiểm tra nếu ID đã được điểm danh trong vòng thời gian cooldown
            current_time = time.time()
            cooldown_period = 300  # 5 phút

            if IDs in self.last_checkin_time:
                elapsed_time = current_time - self.last_checkin_time[IDs]
                if elapsed_time < cooldown_period:
                    return

            # Cập nhật thời gian điểm danh của ID
            self.last_checkin_time[IDs] = current_time

            # Gửi request đến Google Sheets
            self.google_sheet.push(self.ui.classNameInput.text(), IDs)

        except IndexError:
            print("Error: 'information' format is invalid.")

# git push -u origin main