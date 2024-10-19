from app.Model.devices import fingerPrintDevice, cameraDevice

camera = None

def camera_start(camera_id, model_path):
    global camera
    camera = cameraDevice(camera_id, model_path)
    camera.start()

def fingerPrint_start(port):
    fingerPrint = fingerPrintDevice(port)
    fingerPrint.start()

def camera_stop():
    global camera
    if camera:
        camera.stop()

def fingerPrint_stop(fingerPrint):
    fingerPrint.stop()