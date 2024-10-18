import os
import shutil
from PyQt5.QtWidgets import QFileDialog, QMessageBox

def load_folder():
    options = QFileDialog.Options()
    folder_path = QFileDialog.getExistingDirectory(None, "Chọn tệp dữ liệu đã đào tạo", options=options)

    if folder_path:
        try:
            train_model_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "converted_keras")
            if os.path.exists(train_model_root):
                shutil.rmtree(train_model_root)
            shutil.copytree(folder_path, train_model_root)
            QMessageBox.information(None, "Thành công!", f"Đã tải lên tập dữ liệu.")
            return train_model_root
        except Exception as e:
            QMessageBox.critical(None, "Lỗi", f"Lỗi khi tải lên tập dữ liệu: {e}")
            return None
    else:
        QMessageBox.information(None, "Lưu ý", "Bạn chưa chọn thư mục nào cả.")
        return None
