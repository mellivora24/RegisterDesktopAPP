import app.Model.file_manager as FileManager

def onStartButtonClicked(ui):
    try:
        print("Class name: ", ui.classNameInput.text())
        print("Register type: ", ui.registerTypeSelector.currentText())
        if ui.registerTypeSelector.currentIndex() == 0:
            print("Model path: ", ui.modelPathInput.text())
            print("Camera: ", ui.cameraSelector.currentText())
    except Exception as e:
        print(e)

def onStopButtonClicked(app):
    pass

def onRegisterTypeChanged(ui):
    try:
        if ui.registerTypeSelector.currentIndex() == 0:
            ui.modelPathInput.setEnabled(True)
            ui.modelSelectButton.setEnabled(True)
            ui.cameraSelector.setEnabled(True)
        else:
            ui.modelPathInput.setEnabled(False)
            ui.modelPathInput.clear()
            ui.modelSelectButton.setEnabled(False)
            ui.cameraSelector.setEnabled(False)
    except Exception as e:
        print(e)

def onModelSelectButtonClicked(ui):
    model_path = FileManager.load_folder()
    if model_path:
        ui.modelPathInput.setText(model_path)
