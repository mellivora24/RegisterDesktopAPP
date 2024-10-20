#include <SoftwareSerial.h>
#include <Adafruit_Fingerprint.h>

#define TX 6
#define RX 9

SoftwareSerial fingerPrint(TX, RX);
Adafruit_Fingerprint fingerPrintDevice = Adafruit_Fingerprint(&fingerPrint);

/*------------------------------------*/
// Ham doc gia tri ID tu Serial
uint8_t getIDFromSerial() {
  Serial.println("FINGER_READY");
  while (!(Serial.available() > 0)) {}
  while (Serial.available() > 0 && !isDigit(Serial.peek())) Serial.read();
  uint8_t id = (uint8_t)Serial.parseInt();
  if (id == 0 && !Serial.peek()) return 255;

  Serial.println("ID received = ");
  Serial.println(id);

  return id;
}


// Ham check su ton tai cua ID
bool checkFingerprintID(uint8_t id) {
  uint8_t result = fingerPrintDevice.loadModel(id);
  if (result == FINGERPRINT_OK) return true;
  else return false;
}

// Ham lay ID van tay
uint8_t getFingerID() {
  if (fingerPrintDevice.image2Tz() == FINGERPRINT_OK)
    if (fingerPrintDevice.fingerSearch() == FINGERPRINT_OK) return fingerPrintDevice.fingerID;
  return -1;
}

void addFinger() {
  uint8_t id = getIDFromSerial();
  if (id == 255) {
    Serial.println("INVALID_ID");
    return;
  }
  if (checkFingerprintID(id)) {
    Serial.println("FINGER_ID_NOT_NULL");
    return;
  }

  if (fingerPrintDevice.getImage() != FINGERPRINT_OK) Serial.println("FINGER_NOT_FOUND");
  while (fingerPrintDevice.getImage() != FINGERPRINT_OK) {}

  if (fingerPrintDevice.image2Tz(1) == FINGERPRINT_OK) {
    delay(1357);
    while (fingerPrintDevice.getImage() != FINGERPRINT_OK) fingerPrintDevice.getImage();
    if (fingerPrintDevice.image2Tz(2) == FINGERPRINT_OK)
      if (fingerPrintDevice.createModel() == FINGERPRINT_OK)
        if (fingerPrintDevice.storeModel(id) == FINGERPRINT_OK) {
          Serial.println("FINGER_ADDED");
          return;
        }
  }

  Serial.println("FINGER_FAILED");
}

void removeFinger() {
  fingerPrintDevice.getTemplateCount();
  if (fingerPrintDevice.templateCount == 0) {
    Serial.println("FINGER_EMPTY");
    return;
  }

  uint8_t id = getIDFromSerial();
  if (id == 255) {
    Serial.println("INVALID_ID");
    return;
  }

  if (checkFingerprintID(id) && fingerPrintDevice.deleteModel(id) == FINGERPRINT_OK) {
    Serial.println("FINGER_DELETED");
    return;
  } else Serial.println("FINGER_FAILED");
}

void setup() {
  Serial.begin(9600);
  fingerPrintDevice.begin(57600);
  if (!fingerPrintDevice.verifyPassword()) Serial.println("FINGER_FAILED");
  else Serial.println("FINGER_SUCCESSED");
}

void loop() {
  if (Serial.available() > 0) {
    char command = (char)Serial.read();
    switch (command) {
      case 'a':
        Serial.flush();
        addFinger();
        break;
      case 'r':
        Serial.flush();
        removeFinger();
        break;
      default:
        break;
    }
  }

  if (fingerPrintDevice.getImage() == FINGERPRINT_OK) {
    Serial.println("FINGER_FOUND");
    uint8_t id = getFingerID();
    if (id != -1 && id != 255) Serial.println(id);
    else Serial.println("FINGER_ID_NULL");
  }
}
