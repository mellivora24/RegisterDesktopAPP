import os
import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal
from tensorflow.keras.models import load_model

class Camera(QThread):
    np.set_printoptions(suppress=True)
    update_image_signal = pyqtSignal(object)

    def __init__(self, camera_id):
        super().__init__()
        self.camera_id = camera_id
        self.camera = cv2.VideoCapture(camera_id)

        try:
            model_path = "../../app/Model/converted_keras/keras_model.h5"
            labels_path = "../../app/Model/converted_keras/labels.txt"

            if os.path.exists(model_path) and os.path.exists(labels_path):
                self.model = load_model(model_path, compile=False)
                self.labels = [label.strip() for label in open(labels_path, "r").readlines()]
            else:
                raise FileNotFoundError(f"Model or labels file not found in {model_path} or {labels_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            model = None
            labels = []

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.is_running = True

    def run(self):
        self.is_running = True
        while self.is_running:
            ret, frame = self.camera.read()
            if ret:
                self.process_frame(frame)

    def process_frame(self, frame):
        try:
            # Resize and preprocess the frame for the model
            img_resized = cv2.resize(frame, (224, 224))
            img_normalized = img_resized.astype(np.float32) / 255.0
            img_input = np.expand_dims(img_normalized, axis=0)

            # Model prediction
            prediction = self.model.predict(img_input, verbose=0)
            name = self.labels[np.argmax(prediction)]

            # Face detection
            gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray_img, 1.5, 3)

            # Annotate frame with the label and face rectangle if faces are found
            if len(faces) > 0:
                x, y, w, h = faces[0]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Update the frame
            self.update_display(frame)

        except Exception as e:
            print(f"Error processing frame: {e}")

    def update_display(self, frame):
        # Resize and convert the frame to QImage for display
        frame_resized = cv2.resize(frame, (581, 361))
        frame_cvt = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_cvt.shape
        bytes_per_line = ch * w
        qimg = QPixmap.fromImage(QImage(frame_cvt.data, w, h, bytes_per_line, QImage.Format_RGB888))
        self.update_image_signal.emit(qimg)

    def stop(self):
        self.is_running = False
        self.camera.release()

    def __del__(self):
        self.camera.release()
