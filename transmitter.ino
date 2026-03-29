#include <ESP8266WiFi.h>
#include <espnow.h>
#include <EEPROM.h>

#define ESPNOW_LED 1 //Active low

uint8_t broadcastAddress[6] ={};
uint8_t hardCoded[6] = {0xC4, 0xD8, 0xD5, 0x29, 0x82, 0xB2};

bool macIsValid;

WiFiEventHandler stationConnectedHandler;

typedef struct struct_message{
  byte b1, b2, b3, b4, b5, b6, b7, b8;
} struct_message;

struct_message msg;

unsigned long pairTime1, pairTime2; 

void setup() {
  // put your setup code here, to run once:  
  stationConnectedHandler = WiFi.onSoftAPModeStationConnected(&onStationConnected);

  // Serial.begin(115200);
  // delay(500);
  // Serial.println("\nsetup started.");

  EEPROM.begin(EEPROM_MIN_SIZE);

  pinMode(ESPNOW_LED, OUTPUT);
  digitalWrite(ESPNOW_LED, HIGH);

  pinMode(0, INPUT_PULLUP);
  pinMode(2, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);
  pinMode(12, INPUT_PULLUP);
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
  pinMode(16, INPUT_PULLUP); ////HAS TO BE EXTERNALLY PULLED UP

  ESPNOW_init();

  Serial.println("setup done.");
}

void loop() {
  // put your main code here, to run repeatedly:
  send();
  delay(25);

  // Serial.println("working.");

  pairTime1 = millis();
  while(!digitalRead(0) && !digitalRead(2)){
    send();
    delay(25);
    
    // Serial.println("pairing.");

    pairTime2 = millis();
    if(pairTime2 - pairTime1 > 3000){
      // Serial.println("pairing2.");
      
      pair();
    }
    yield();
  }
}

void send(){
  msg.b1 = digitalRead(0);//A
  msg.b2 = digitalRead(2);//A
  msg.b3 = digitalRead(4);//
  msg.b4 = digitalRead(5);//
  msg.b5 = digitalRead(12);//A
  msg.b6 = digitalRead(13);//A
  msg.b7 = digitalRead(14);//
  msg.b8 = digitalRead(16);//
  esp_now_send(broadcastAddress, (uint8_t *) &msg, sizeof(msg));
}

void OnDataSent(uint8_t *mac_addr, uint8_t sendStatus) {
  // Serial.print("Last Packet Send Status: ");
  if (sendStatus == 0){
    // Serial.println("Delivery success");
    digitalWrite(ESPNOW_LED, LOW);
  }
  else{
    // Serial.println("Delivery fail");
    digitalWrite(ESPNOW_LED, HIGH);
  }
}

void WriteEEPROM(){
  EEPROM.wipe();
  EEPROM.commit();

  for(int i = 0; i < 6; i++){
    EEPROM.put(i, broadcastAddress[i]);
  }
  EEPROM.put(6, '\0');
  EEPROM.commit();
}

void ReadEEPROM(){
  for(int i = 0; i < 6; i++){
    broadcastAddress[i] = EEPROM.read(i);
  }
}

void ESPNOW_init(){
  ReadEEPROM();

  WiFi.mode(WIFI_STA);

  esp_now_init();

  esp_now_add_peer(broadcastAddress, ESP_NOW_ROLE_SLAVE, 1, NULL, 0);

  esp_now_set_self_role(ESP_NOW_ROLE_CONTROLLER);
  esp_now_register_send_cb(OnDataSent);

  digitalWrite(ESPNOW_LED, LOW);
}

void ESPNOW_deinit(){
  esp_now_unregister_send_cb();

  esp_now_deinit();

  digitalWrite(ESPNOW_LED, HIGH);
}

void softAP_deinit(){
  WiFi.disconnect(true);
  // WiFi.mode(WIFI_OFF);
} 

void onStationConnected(const WiFiEventSoftAPModeStationConnected& evt){
  for(int i = 0; i < 6; i++){
    if(evt.mac[i] == 0){
      macIsValid = false;
      return;
    }
    else{
      macIsValid= true;
    }
  }

  for(int i = 0; i < 6; i++){
    broadcastAddress[i] = evt.mac[i];
  }
}

void pair(){
  // Serial.println("pairing started.");

  ESPNOW_deinit();

  WiFi.softAP("PAIRING", "123456789");

  // Serial.println("this point.");

  macIsValid = false;
  while(!macIsValid) delay(100);

  // Serial.println("this point2.");

  WriteEEPROM();

  delay(500);

  // Serial.println("this point2.");

  softAP_deinit();

  ESPNOW_init();

  // Serial.println("this point2.");

  while(!digitalRead(0), !digitalRead(2)){
    send();
    delay(25);
  }
}


















