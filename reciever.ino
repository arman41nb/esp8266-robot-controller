#include <ESP8266WiFi.h>
#include <espnow.h>
#include <EEPROM.h>

#define PAIR_BUTTON 14
#define ESPNOW_LED 4
#define MOBILE_LED 5

typedef struct struct_message{
  byte b1, b2, b3, b4, b5, b6, b7, b8;
} struct_message;

struct_message myData;

const uint8_t START_MARKER = 0xAA;
const uint8_t END_MARKER   = 0x55;

volatile bool dataReceived = false;

volatile bool gotMacAddress = false;
volatile bool macIsValid;

uint8_t broadcastAddress[6] = {};

WiFiEventHandler connectedHandler;

volatile unsigned long lastDataReceived = 0;

void setup() {
  // put your setup code here, to run once:
  connectedHandler = WiFi.onStationModeConnected(&onWiFiConnected);

  Serial.begin(9600);
  Serial.swap();

  pinMode(PAIR_BUTTON, INPUT_PULLUP);
  pinMode(ESPNOW_LED, OUTPUT);
  digitalWrite(ESPNOW_LED, LOW);
  pinMode(MOBILE_LED, OUTPUT);
  digitalWrite(MOBILE_LED, LOW);

  EEPROM.begin(512);

  ESPNOW_init();
}

void loop() {
  // put your main code here, to run repeatedly:
  handleReceivedData();
  handlePairing();
  handleESPNOW_LED();
  yield();
}

void onWiFiConnected(const WiFiEventStationModeConnected& evt){
  uint8_t* mac = WiFi.BSSID();

  for(int i = 0; i < 6; i++){
    if(mac[i] == 0){
      macIsValid = false;
      return;
    }
    else{
      macIsValid = true;
    }
  }

  for(int i = 0; i < 6; i++){
    broadcastAddress[i] = mac[i];
  }


  // Serial.print("mac address: ");
  // for(int i = 0; i < 6; i++){
  //   Serial.print(broadcastAddress[i]);
  //   if(i != 5) Serial.print(":");
  // }
  // Serial.print("\n");


  gotMacAddress = true;
}

void handleReceivedData(){
  if(dataReceived){
    dataReceived = false;

    Serial.write(START_MARKER);
    Serial.write(myData.b1);
    Serial.write(myData.b2);
    Serial.write(myData.b3);
    Serial.write(myData.b4);
    Serial.write(myData.b5);
    Serial.write(myData.b6);
    Serial.write(myData.b7);
    Serial.write(myData.b8);
    Serial.write(END_MARKER);
  }
}

void handlePairing(){
  static unsigned long buttonPressStart = 0;

  if (!digitalRead(PAIR_BUTTON)) {
    if (buttonPressStart == 0) {
      buttonPressStart = millis();
    } 
    else if (millis() - buttonPressStart > 3000) {
      pair();
      buttonPressStart = 0;
    }
  } 
  else {
    buttonPressStart = 0;
  }
}

void handleESPNOW_LED(){
  static unsigned long lastBlinkTime = 0;
  static bool ledState = false;

  if (millis() - lastDataReceived >= 100) {
    if (millis() - lastBlinkTime >= 100) {
      lastBlinkTime = millis();
      ledState = !ledState;
      digitalWrite(ESPNOW_LED, ledState);
    }
  }else{
    digitalWrite(ESPNOW_LED, HIGH);
  }
}

void WriteEEPROM(){
  for (int i = 0; i < 6; i++) {
    EEPROM.put(i, broadcastAddress[i]);
  }
  EEPROM.put(6, '\0');
  EEPROM.commit();
}

void ReadEEPROM(){
  uint8_t ch = 0;
  int address = 0, i = 0;
  while ((ch = EEPROM.read(address + i)) != '\0') {
    broadcastAddress[i] = ch;
    i++;
  }
}

void disconnect(){
  WiFi.disconnect(true);
  // WiFi.mode(WIFI_OFF);
}

void ESPNOW_init(){
  ReadEEPROM();

  for(int i = 0; i < 6; i++){
    if(broadcastAddress[i] == 0) return;
  }

  WiFi.mode(WIFI_STA);

  esp_now_init();

  esp_now_set_self_role(ESP_NOW_ROLE_COMBO);

  esp_now_register_recv_cb(OnDataRecv);

  // digitalWrite(ESPNOW_LED, HIGH);
}

void ESPNOW_deinit(){
  esp_now_unregister_recv_cb();

  esp_now_deinit();

  digitalWrite(ESPNOW_LED, LOW);  
}

void OnDataRecv(uint8_t * mac, uint8_t *incomingData, uint8_t len){
  for(int i = 1; i < 6; i++){
    // Serial.printf("mac %d:", i);
    // Serial.println(mac[i]);
    // Serial.printf("bca %d:", i);
    // Serial.println(broadcastAddress[i]);
    if(mac[i] != broadcastAddress[i]) return;
  }

  memcpy(&myData, incomingData, sizeof(myData));

  dataReceived = true;

  lastDataReceived = millis();
}

void pair(){
  ESPNOW_deinit();

  WiFi.mode(WIFI_STA);
  WiFi.begin("PAIRING", "123456789");

  gotMacAddress = false;
  unsigned long lastBlinkTime = 0;
  bool ledState = false;

  while(!gotMacAddress){
    if(millis() - lastBlinkTime >= 100){
      lastBlinkTime = millis();
      ledState = !ledState;
      digitalWrite(ESPNOW_LED, !ledState);
    }

    yield();
  }

  WriteEEPROM();

  delay(500);

  disconnect();

  ESPNOW_init();

  while(!digitalRead(PAIR_BUTTON)){
    handleReceivedData();
  }
}