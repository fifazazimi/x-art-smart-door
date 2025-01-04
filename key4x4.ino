#include <Keypad.h>

int data;
const byte ROWS = 4; // four rows
const byte COLS = 4; // four columns
char keys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};

byte rowPins[ROWS] = {9, 8, 7, 6};  // connect to the row pinouts of the keypad
byte colPins[COLS] = {5, 4, 3, 2};  // connect to the column pinouts of the keypad

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

const String correctCode = "1234D";  // กำหนดรหัสที่ถูกต้อง
String inputCode = "";              // เก็บรหัสที่ถูกกด

const int ledPin = 13;  // กำหนดพินของ LED
int relayPin = 12;
void setup() {
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);  // ปิดไฟ LED ในตอนเริ่มต้น
  pinMode(relayPin, OUTPUT);
  Serial.begin(9600);
  Serial.println("Please Enter the Code:");
}

void loop() {
  char key = keypad.getKey();

  if (key != NO_KEY) {
    inputCode += key;  // เพิ่มตัวเลขที่กดไปในรหัสที่ผู้ใช้ใส่

    Serial.print("Current Input: ");
    Serial.println(inputCode);

    // ถ้าจำนวนตัวเลขที่กดครบตามจำนวนรหัสที่ถูกกำหนด
    if (inputCode.length() == correctCode.length()) {
      if (inputCode == correctCode) {
        Serial.println("Code correct! LED is ON.");
        digitalWrite(ledPin, HIGH);  // เปิดไฟ LED
        digitalWrite(relayPin, HIGH);
        delay(5000);
        digitalWrite(ledPin, LOW);
        digitalWrite(relayPin, LOW);
        Serial.println("RESET");
      } else {
        Serial.println("Code incorrect! Please try again.");
        digitalWrite(ledPin, LOW);  // ปิดไฟ LED หากรหัสไม่ถูกต้อง
        digitalWrite(relayPin, LOW);
        delay(500);
        Serial.println("RESET");
      }
      inputCode = "";  // รีเซ็ตการกรอกรหัส
    }
  }
  if (Serial.available() > 0) {
    data = Serial.read();

    if (data == '1') {
      digitalWrite(ledPin, HIGH);  // เปิดไฟ LED
      digitalWrite(relayPin, HIGH);
      Serial.println("WAIT");
      delay(5000);
      Serial.println("DONE");
    } else if (data == '0') {
      digitalWrite(ledPin, LOW);
      digitalWrite(relayPin, LOW);
    }
  }
}