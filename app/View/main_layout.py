import sys
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow
from app.Controller.handelEvents import ViewEvents

class MainLayout(QMainWindow):
    def __init__(self, ui_path, title="Main Layout", icon_path="../../res/icon.png"):
        super().__init__()
        self.ui = loadUi(ui_path, self)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon_path))
        self.controller = ViewEvents(self.ui)
        self.show()

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainLayout(ui_path="../../res/main_layout.ui", title="TEST", icon_path="../../res/image/ico/test.ico")
    sys.exit(app.exec_())
