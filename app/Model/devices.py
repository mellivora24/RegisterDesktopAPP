import cv2
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

class Camera(QThread):
    update_image_signal = pyqtSignal(object)

    def __init__(self, camera_id):
        super().__init__()
        self.camera_id = camera_id
        self.camera = cv2.VideoCapture(camera_id)
        # self.model = "app/Model/converted_keras/keras_model.h5"
        # self.labels = "app/Model/converted_keras/labels.txt"
        self.is_running = True

    def run(self):
        self.is_running = True
        while self.is_running:
            ret, frame = self.camera.read()
            if ret:
                try:
                    frame = cv2.resize(frame, (581, 361))
                    frame_cvt = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    qimg = QPixmap.fromImage(QImage(frame_cvt.data, w, h, bytes_per_line, QImage.Format_RGB888))
                    self.update_image_signal.emit(qimg)
                except Exception as e:
                    print(e)


    def stop(self):
        self.is_running = False
        self.camera.release()
