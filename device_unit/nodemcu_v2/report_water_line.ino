#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
#include <string.h>

#define SERVER_HOST "ec2-3-112-231-92.ap-northeast-1.compute.amazonaws.com:21090"
#define DEVICE_NAME "water_line"

#define STASSID "MuranoHome_host"
#define STAPSK  "pray123a"

int trigPin = D1;
int echoPin = D2;
int sampleRate = 10;
float sampleChangeLimit = 5.0;    // Unit is cm
int sampleCutOffLen = 2;
float None = -1.0;


void setup() {  
  Serial.begin (9600);
  pinMode(D0, OUTPUT);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  digitalWrite(trigPin, LOW);
  delay(100);

  //setup wifi env....
  WiFi.begin(STASSID, STAPSK);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());

  if ((WiFi.status() == WL_CONNECTED)) {

    WiFiClient client;
    HTTPClient http;

    Serial.print("[HTTP] begin...\n");
    // configure traged server and url
    http.begin(client, "http://" SERVER_HOST "/"); //HTTP
    //http.addHeader("Content-Type", "application/json");

    Serial.print("[HTTP] GET...\n");
    // start connection and send HTTP header and body
    int httpCode = http.GET();

    // httpCode will be negative on error
    if (httpCode > 0) {
      // HTTP header has been send and Server response header has been handled
      Serial.printf("[HTTP] GET... code: %d\n", httpCode);

      // file found at server
      if (httpCode == HTTP_CODE_OK) {
        const String& payload = http.getString();
        Serial.println("received payload:\n<<");
        Serial.print(payload);
        Serial.println(">>");
      }
    } else {
      Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
  }

  delay(100);
}

void lighting(int time_ms) {
  digitalWrite(D0, LOW);
  delay(time_ms);
  digitalWrite(D0, HIGH);
}

float set_decimal_place(float value_intput, int decimalPlace) {
  float vlaue_output;
  long cut_vlaue = pow(10, decimalPlace);
  long temp = value_intput * cut_vlaue;
  vlaue_output = temp / cut_vlaue;
  return vlaue_output;
}

float echo_sensor() {
  digitalWrite(trigPin, HIGH);     // 給 Trig 高電位，持續 10微秒
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration;
  duration = pulseIn(echoPin, HIGH);   // 收到高電位時的時間
  float cm = ((float)duration / 2.0) / 29.1;         // 將時間換算成距離 cm
  Serial.print(cm);
  Serial.println("cm");
  return cm;
}

void bubble_sort(float arr[], int len) {
  for (int i = 0; i < len - 1; ++i) {
    for (int j = 0; j < i; ++j) {
      if (arr[j] > arr[i]) {
        float temp = arr[j];
        arr[j] = arr[i];
        arr[i] = temp;
      }
    }
  }
}

void loop() {
  float sample_list[sampleRate];
  // Fill value to sample list
  for (int index = 0; index < sampleRate; index++) {
    float distance;
    distance = echo_sensor();
    sample_list[index] = distance;
    lighting(100);
    delay(400);
  }
  // Sort this list
  bubble_sort(sample_list, sampleRate);
  // Average value
  float sample_sum = 0.0;
  for (int index = sampleCutOffLen; index < sampleRate - sampleCutOffLen; index++) {
    sample_sum += sample_list[index];
  }
  float sample_avg_temp = sample_sum / (sampleRate - sampleCutOffLen * 2);
  float sample_avg = set_decimal_place(sample_avg_temp, 2);
  // Send value to server
  if ((WiFi.status() == WL_CONNECTED)){
    WiFiClient client;
    HTTPClient http;
    http.begin(client, "http://" SERVER_HOST "/device/" DEVICE_NAME);
    http.addHeader("Content-Type", "application/json");
    DynamicJsonDocument setData(1024);
    setData["deviceName"] = "魚缸水位";
    setData["value"] = sample_avg;
    setData["unit"] = "cm";
    DynamicJsonDocument root(1024);
    root["setData"] = setData;
    String jsonStr;
    serializeJson(root, jsonStr);
    int httpCode = http.POST(jsonStr);
    Serial.printf("[HTTP] POST... code: %d\n", httpCode);
    if (httpCode == HTTP_CODE_OK) {
      const String& payload = http.getString();
      Serial.println("received payload:\n<<");
      Serial.print(payload);
      Serial.println(">>");
    }
  }

}