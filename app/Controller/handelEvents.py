from app.Model.devices import Camera
from PyQt5.QtWidgets import QMessageBox
from app.Model.devices import FingerPrint
import app.Model.file_manager as FileManager
from app.Services.google_sheet import GoogleSheet

class viewEvents:
    def __init__(self, ui):
        self.camera = None
        self.ui = ui
        self.guiInit()
        self.eventsConnect()
        self.google_sheet = GoogleSheet()

    def guiInit(self):
        self.ui.fingerPrintCOMInput.setEnabled(False)
        self.ui.stopButton.setEnabled(False)
        self.ui.fingerPrintView.setVisible(False)
        self.ui.cameraView.setVisible(True)

    def eventsConnect(self):
        self.ui.stopButton.clicked.connect(self.stopButtonClicked)
        self.ui.startButton.clicked.connect(self.startButtonClicked)
        self.ui.addFingerButton.clicked.connect(self.addFingerButtonClicked)
        self.ui.modelSelectButton.clicked.connect(self.modelSelectButtonClicked)
        self.ui.deleteFingerButton.clicked.connect(self.deleteFingerButtonClicked)
        self.ui.registerTypeSelector.currentIndexChanged.connect(self.registerTypeChanged)

    def startButtonClicked(self):
        is_started = False
        class_name = self.ui.classNameInput.text()
        if self.ui.registerTypeSelector.currentIndex() == 0:
            if not self.ui.modelPathInput.text() and not class_name:
                QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng nhập đường dẫn mô hình và tên lớp!")
            else:
                is_started = True
        else:
            if not self.ui.fingerPrintCOMInput.text() and not class_name:
                QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng nhập cổng COM và tên lớp!")
            else:
                is_started = True

        if is_started:
            self.ui.stopButton.setEnabled(True)
            self.ui.startButton.setEnabled(False)
            self.ui.cameraSelector.setEnabled(False)
            self.ui.modelPathInput.setEnabled(False)
            self.ui.classNameInput.setEnabled(False)
            self.ui.modelSelectButton.setEnabled(False)
            self.ui.fingerPrintCOMInput.setEnabled(False)
            self.ui.registerTypeSelector.setEnabled(False)

            if self.ui.registerTypeSelector.currentIndex() == 0:
                try:
                    self.camera = Camera(self.ui.cameraSelector.currentIndex())
                    self.camera.update_image_signal.connect(self.onUpdateImageView)
                    self.camera.send_information_signal.connect(self.informationSignalFromCamera)
                    self.camera.start()
                except Exception as e:
                    QMessageBox.warning(self.ui, "Lỗi", str(e))
                    self.stopButtonClicked()
            else:
                try:
                    self.fingerPrint = FingerPrint(self.ui.fingerPrintCOMInput.text())
                    self.fingerPrint.finger_print_read_signal.connect(self.onFingerPrintRead)
                    self.fingerPrint.start()
                except Exception as e:
                    QMessageBox.warning(self.ui, "Lỗi", str(e))
                    self.stopButtonClicked()

    def stopButtonClicked(self):
        self.ui.stopButton.setEnabled(False)
        self.ui.startButton.setEnabled(True)
        self.ui.classNameInput.setEnabled(True)
        self.ui.registerTypeSelector.setEnabled(True)

        if self.ui.registerTypeSelector.currentIndex() == 0:
            self.ui.cameraSelector.setEnabled(True)
            self.ui.modelPathInput.setEnabled(True)
            self.ui.modelSelectButton.setEnabled(True)
            if self.camera:
                self.camera.stop()
        else:
            self.ui.fingerPrintCOMInput.setEnabled(True)
            if self.fingerPrint:
                self.fingerPrint.stop()

    def modelSelectButtonClicked(self):
        model_path = FileManager.load_folder()
        if model_path:
            self.ui.modelPathInput.setText(model_path)

    def addFingerButtonClicked(self):
        IDs = self.ui.addFingerIDInput.text()
        name = self.ui.studentNameInput.text()
        if not IDs:
            QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng nhập ID!")
        else:
            message = "a" + IDs
            self.fingerPrint.send(message)
            self.google_sheet.create_data(self.ui.classNameInput.text(), IDs, name)

    def deleteFingerButtonClicked(self):
        IDs = self.ui.deleteFingerIDInput.text()
        if not IDs:
            QMessageBox.warning(self.ui, "Cảnh báo", "Vui lòng nhập ID!")
        else:
            message = "r" + IDs
            self.fingerPrint.send(message)

    def registerTypeChanged(self):
        if self.ui.registerTypeSelector.currentIndex() == 0:
            self.ui.modelPathInput.setEnabled(True)
            self.ui.cameraSelector.setEnabled(True)
            self.ui.modelSelectButton.setEnabled(True)
            self.ui.fingerPrintCOMInput.setEnabled(False)
            self.ui.cameraView.setVisible(True)
            self.ui.fingerPrintView.setVisible(False)
        else:
            self.ui.modelPathInput.setEnabled(False)
            self.ui.cameraSelector.setEnabled(False)
            self.ui.modelSelectButton.setEnabled(False)
            self.ui.fingerPrintCOMInput.setEnabled(True)
            self.ui.cameraView.setVisible(False)
            self.ui.fingerPrintView.setVisible(True)

    def onFingerPrintRead(self, message):
        message = message.strip()
        if message == "FINGER_ADDED":
            QMessageBox.information(self.ui, "Thông báo", "Vân tay đã được thêm!")
            self.ui.addFingerIDInput.setText("")
        elif message == "FINGER_DELETED":
            QMessageBox.information(self.ui, "Thông báo", "Vân tay đã được xóa!")
            self.ui.deleteFingerIDInput.setText("")
        elif message == "FINGER_FAILED":
            QMessageBox.warning(self.ui, "Cảnh báo", "Thao tác thất bại!")
            self.ui.deleteFingerIDInput.setText("")
            self.ui.addFingerIDInput.setText("")
        elif message == "FINGER_ID_NOT_NULL":
            QMessageBox.warning(self.ui, "Cảnh báo", "ID đã tồn tại!")
        elif message == "FINGER_ID_NULL":
            self.ui.idValue.setText("ID không tồn tại!")
        elif message == "INVALID_ID":
            QMessageBox.warning(self.ui, "Cảnh báo", "ID không hợp lệ!")
            self.ui.deleteFingerIDInput.setText("")
            self.ui.addFingerIDInput.setText("")
        elif message == "FINGER_EMPTY":
            QMessageBox.warning(self.ui, "Cảnh báo", "Vân tay không tồn tại!")
        elif message.isdigit():
            IDs = message
            self.ui.idValue.setText(IDs)
            self.google_sheet.push(self.ui.classNameInput.text(), IDs)

    def onUpdateImageView(self, frame):
        self.ui.imageViewFrame.setPixmap(frame)

    def informationSignalFromCamera(self, information):
        IDs = information.split(" ")[0]
        self.google_sheet.push(self.ui.classNameInput.text(), IDs)
