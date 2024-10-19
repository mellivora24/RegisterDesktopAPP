import sys
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
import app.Controller.handelEvents as EventsController

class MainLayout(QMainWindow):
    def __init__(self, ui_path, title="Main Layout", icon_path="../../res/icon.png"):
        super().__init__()
        self.ui = loadUi(ui_path, self)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon_path))
        self.handelEvents()
        self.show()

    def handelEvents(self):
        self.ui.fingerPrintCOMInput.setEnabled(False)
        self.ui.startButton.clicked.connect(lambda : EventsController.onStartButtonClicked(self.ui))
        self.ui.stopButton.clicked.connect(EventsController.onStopButtonClicked)
        self.ui.modelSelectButton.clicked.connect(lambda : EventsController.onModelSelectButtonClicked(self.ui))
        self.ui.registerTypeSelector.currentIndexChanged.connect(lambda : EventsController.onRegisterTypeChanged(self.ui))
        self.ui.cameraSelector.currentIndexChanged.connect(lambda : EventsController.onCameraChanged(self.ui))

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainLayout(ui_path="../../res/main_layout.ui", title="TEST", icon_path="../../res/image/ico/test.ico")
    sys.exit(app.exec_())