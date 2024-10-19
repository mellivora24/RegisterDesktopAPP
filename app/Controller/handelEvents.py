from PyQt5.QtWidgets import QMessageBox
import app.Model.file_manager as FileManager
from app.Model.devices import Camera

class viewEvents:
    def __init__(self, ui):
        self.camera = None
        self.ui = ui
        self.ui.stopButton.setEnabled(False)
        self.ui.fingerPrintCOMInput.setEnabled(False)
        self.eventsConnect()

    def eventsConnect(self):
        self.ui.stopButton.clicked.connect(self.stopButtonClicked)
        self.ui.startButton.clicked.connect(self.startButtonClicked)
        self.ui.modelSelectButton.clicked.connect(self.modelSelectButtonClicked)
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
                    self.camera.start()
                except Exception as e:
                    QMessageBox.warning(self.ui, "Lỗi", str(e))
            else:
                pass

    def stopButtonClicked(self):
        self.ui.stopButton.setEnabled(False)
        self.ui.startButton.setEnabled(True)
        self.ui.cameraSelector.setEnabled(True)
        self.ui.modelPathInput.setEnabled(True)
        self.ui.classNameInput.setEnabled(True)
        self.ui.modelSelectButton.setEnabled(True)
        self.ui.fingerPrintCOMInput.setEnabled(True)
        self.ui.registerTypeSelector.setEnabled(True)

        if self.ui.registerTypeSelector.currentIndex() == 0:
            pass
        else:
            pass

    def modelSelectButtonClicked(self):
        model_path = FileManager.load_folder()
        if model_path:
            self.ui.modelPathInput.setText(model_path)

    def registerTypeChanged(self):
        if self.ui.registerTypeSelector.currentIndex() == 0:
            self.ui.modelPathInput.setEnabled(True)
            self.ui.cameraSelector.setEnabled(True)
            self.ui.modelSelectButton.setEnabled(True)
            self.ui.fingerPrintCOMInput.setEnabled(False)
        else:
            self.ui.modelPathInput.setEnabled(False)
            self.ui.cameraSelector.setEnabled(False)
            self.ui.modelSelectButton.setEnabled(False)
            self.ui.fingerPrintCOMInput.setEnabled(True)

    def onFingerPrintRead(self, data):
        pass

    def onUpdateImageView(self, frame):
        self.ui.imageViewFrame.setPixmap(frame)