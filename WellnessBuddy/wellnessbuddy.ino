#include <HttpClient.h>
#include <SparkFunRHT03.h>
#include "SparkFun_MMA8452Q.h"
#include <Wire.h>
#include "Arduino.h"
#include "SI114X.h"

SI114X SI1145 = SI114X(); // Sunlight sensor
const int pinAdc = A1; // Sound sensor
MMA8452Q accel;                   // create instance of the MMA8452 class
int stepsTaken = 0;
double minThreshold = 10;
double maxThreshold = -10;

const char* IP_ADDRESS = "3.19.71.22";

//unsigned int nextTime = 0; // Next time to contact the server
HttpClient http;
// Headers currently need to be set at init, useful for API keys etc.
http_header_t headers[] = {
// { "Content-Type", "application/json" },
// { "Accept" , "application/json" },
{ "Accept" , "*/*"},
{ NULL, NULL } // NOTE: Always terminate headers will NULL
};

http_request_t request;
http_response_t response;

const int RHT03_DATA_PIN = D3; // RHT03 data pin
RHT03 rht; // This creates a RTH03 object, which we'll use to interact with the sensor
float minimumTempC = 5505;
float maximumTempC = 0;
float minimumTempF = 9941;
float maximumTempF = 0;
float minimumHumidity = 100;
float maximumHumidity = 0;

void calibrateAccel()
{
    int start = millis();
    while (millis() < start + 10000) {
        if (accel.available()) {
            double x = accel.getCalculatedX();
            minThreshold = min(x, minThreshold);
            maxThreshold = max(x, maxThreshold);
        }
    }
}

double mapf(double x, double in_min, double in_max, double out_min, double out_max)
{
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void setup() {

    Serial.begin(9600);
    Serial.println("Beginning Si1145!");

    while (!SI1145.Begin()) {
        Serial.println("Si1145 is not ready!");
        delay(1000);
    }
    Serial.println("Si1145 is ready!");
    
    if (accel.begin() == false) {
    Serial.println("Accelerometer not Connected. Please check connections and read the hookup guide.");
    while (1);
    }
    Wire.begin();
    rht.begin(RHT03_DATA_PIN);  // Initialize the RHT03 sensor
    
    delay(100);
    Serial.println("Calibrating accelerometer...");
    calibrateAccel();
    Serial.println("Done.");
    
    delay(1000);

}

long getSoundData()
{
    long sum = 0;
    for(int i=0; i<32; i++)
    {
        sum += analogRead(pinAdc);
    }
    sum >>= 5;
    return sum;
}

unsigned char getHeartRate()
{
    unsigned char heartRate = 0;
    Wire.requestFrom(0xA0 >> 1, 1);    // request 1 bytes from slave device
    while(Wire.available()) {          // slave may send less than requested
        heartRate = Wire.read();   // receive heart rate value (a byte)
    }
    delay(500);
    return heartRate;
}

void loop() {
    double sensorVal = pow(accel.getCalculatedX() + accel.getCalculatedY(), 2);
    double mappedVal = mapf(sensorVal, minThreshold, maxThreshold, 0, 100);
    if(abs(mappedVal - 50) > 5) {
      stepsTaken += 1;
    }
    
    int update = rht.update();
    if (update && accel.available()) {
        Serial.println();
        Serial.println("Application>\tStart of Loop.");
        
        char buf[256];
        float humidity = rht.humidity();
        // Do some math to calculate the max/min humidity
        if (humidity > maximumHumidity) maximumHumidity = humidity;
        if (humidity < minimumHumidity) minimumHumidity = humidity;
        
        float tempF = rht.tempF();
        // Do some math to calculate the max/min tempF
        if (tempF > maximumTempF) maximumTempF = tempF;
        if (tempF < minimumTempF) minimumTempF = tempF;
        
        float tempC = rht.tempC();
        // Do some math to calculate the max/min tempC
        if (tempC > maximumTempC) maximumTempC = tempC;
        if (tempC < minimumTempC) minimumTempC = tempC;
        
        
        int visibleLight = SI1145.ReadVisible();
        int infraredLight = SI1145.ReadIR();
        float uvIndex = (float)SI1145.ReadUV() / 100;

        int heartrate = getHeartRate();
        // Request path and body can be set at runtime or at setup.
        request.hostname = IP_ADDRESS;
        request.port = 5000;
        sprintf(buf, "/test?fahrenheit=%f&celcius=%f&humidity=%f&sound=%ld&vl=%d&il=%d&uv=%f&steps=%d&heartrate=%d", tempF, tempC, humidity, getSoundData(), visibleLight, infraredLight, uvIndex, stepsTaken, heartrate);
        request.path = buf;
        // The library also supports sending a body with your request:
        //request.body = "{\"key\":\"value\"}";
        // Get request
        http.get(request, response, headers);
        Serial.print("Application>\tResponse status: ");
        Serial.println(response.status);
        Serial.print("Application>\tHTTP Response Body: ");
        Serial.println(response.body);
       delay(500);

    } else {
        delay(RHT_READ_INTERVAL_MS);
    }

}

