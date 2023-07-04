#ifndef SMART_WATERING_H
#define SMART_WATERING_H

// Required Libraries

#include <Arduino.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <Adafruit_BMP280.h>
#include <ArduinoJson.h>
#include <esp_system.h>
#include <HCSR04.h>
#include <RTClib.h>
#include <libgen.h>
#include <regex.h>
#include <MQ135.h>
#include <WiFi.h>
#include <DHT.h>

// Set the Wi-Fi name and password.

#define WIFI_SSID     "WIFI_NAME"
#define WIFI_PASSWORD "WIFI_PASSWORD"

// Set the platform URL and API token.

#define SERVER_URL       "http://192.168.0.104"
#define DJANGO_API_TOKEN "93a079be-561a-437a-9706-747968e48a53"

// If you are testing the local server, set it to false. Otherwise, set it to true.

#define HTTPS_SERVER false

// This certificate is used for HTTPS requests. If it has expired, you will need to generate a new one.

#define ROOT_CA_CERTIFICATE                                              \
    "-----BEGIN CERTIFICATE-----\n"                                      \
    "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\n" \
    "-----END CERTIFICATE-----\n"

// Enable or disable the debug messages for these items.

#define DEBUG_WIFI     true
#define DEBUG_ESP32    true
#define DEBUG_SENSOR   true
#define DEBUG_REQUEST  true
#define DEBUG_RESPONSE true

// It is not necessary to change these items.

#define WIFI_DEBUGGING_LEVEL     0
#define ESP32_DEBUGGING_LEVEL    1
#define SENSOR_DEBUGGING_LEVEL   2
#define REQUEST_DEBUGGING_LEVEL  3
#define RESPONSE_DEBUGGING_LEVEL 4

// Set whether the ESP32 IP should be static or not (activation recommended).

#define STATIC_IP_ADDRESS true

// Set the Wi-Fi network addresses according to your needs.

#define IP_ADDRESS      192, 168, 0, 100
#define GATEWAY_ADDRESS 192, 168, 0, 1
#define SUBNET_MASK     255, 255, 0, 0
#define PRIMARY_DNS     8, 8, 8, 8
#define SECONDARY_DNS   8, 8, 4, 4

// Set the ESP32 baud rate according to your needs.

#define ESP32_BAUD_RATE 115200

// It is not necessary to change the GPIOs below (some error may occur).

#define DHT11_PIN         4
#define HCSR04_ECHO_PIN  12
#define HCSR04_TRIG_PIN  13
#define YL83_PIN         14
#define RELAY_PIN        18
#define YFS201_PIN       19
#define TEMT6000_PIN     25
#define FC28_PIN         27
#define GYML8511_OUT_PIN 32
#define GYML8511_3V3_PIN 33
#define MQ135_PIN        34

// Debugging Function.

void debugging(String message, unsigned int level);

// Startup functions for settings, network operations, and tasks on the second core.

void start_settings(void);
void connect_to_wifi(void);
void disconnect_from_wifi(void);
void second_core_task(void *argv);
String request_get(String host);
String request_post(String host, String body);

// Functions responsible for irrigation scheduling and testing.

void analyze_irrigation_test(void);
void analyze_irrigation_schedules(void);

// Data collection and sending functions.

void send_sensor_data(void);
void read_sensors_data(void);
void send_test_availability(unsigned int id, bool available);
void send_schedule_status(unsigned int id, String status);
void send_water_consumption(float consumption);
void send_notification(String title, String message);
void measure_water_consumption(void);

// Utility Functions.

String get_time(void);
String get_timeout(const String &time, unsigned int increase);
String get_datetime(bool formatted = true);
String get_address_string(IPAddress address);
String split_datetime(String datetime);
String split_time(String datetime);
int valid_value_range(int range);
void update_datetime(void);
bool valid_datetime(const String &datetime);
float map_float(float x, float in_min, float in_max, float out_min, float out_max);

#endif