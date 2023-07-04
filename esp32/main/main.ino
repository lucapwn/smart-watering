#include "smart_watering.h"

RTC_DS3231 RTC;
MQ135 MQ135(MQ135_PIN);
Adafruit_BMP280 BMP280;
DHT DHT(DHT11_PIN, DHT11);
UltraSonicDistanceSensor HCSR04(HCSR04_TRIG_PIN, HCSR04_ECHO_PIN);

float humidity              = 0.0f;
float temperature           = 0.0f;
float atmospheric_pressure  = 0.0f;
float ultraviolet_radiation = 0.0f;
float luminosity            = 0.0f;
float air_quality           = 0.0f;
float water_level           = 0.0f;
float water_flow            = 0.0f;
float consumption           = 0.0f;
float runtime               = 0.0f;
unsigned int soil_moisture  = 0;
unsigned int rain_level     = 0;
unsigned long start_time    = 0;
bool water_pump_on          = false;

TaskHandle_t second_core_task_handle = NULL;

void setup() {
    start_settings();
}

void loop() {
    read_sensors_data();
    connect_to_wifi();
    analyze_irrigation_test();
    analyze_irrigation_schedules();
    send_sensor_data();
    disconnect_from_wifi();
}

void debugging(String message, unsigned int level) {
    if (level == WIFI_DEBUGGING_LEVEL && DEBUG_WIFI) {
        Serial.println("[" + get_datetime() + "]  Wi-Fi     " + message);
    } else if (level == ESP32_DEBUGGING_LEVEL && DEBUG_ESP32) {
        Serial.println("[" + get_datetime() + "]  ESP32     " + message);
    } else if (level == SENSOR_DEBUGGING_LEVEL && DEBUG_SENSOR) {
        Serial.println("[" + get_datetime() + "]  Sensor    " + message);
    } else if (level == REQUEST_DEBUGGING_LEVEL && DEBUG_REQUEST) {
        Serial.println("[" + get_datetime() + "]  Request   " + message);
    } else if (level == RESPONSE_DEBUGGING_LEVEL && DEBUG_RESPONSE) {
        Serial.println("[" + get_datetime() + "]  Response  " + message);
    }
}

void start_settings(void) {
    DHT.begin();
    Serial.begin(ESP32_BAUD_RATE);
    BMP280.setSampling(Adafruit_BMP280::MODE_NORMAL, Adafruit_BMP280::SAMPLING_X2, Adafruit_BMP280::SAMPLING_X16, Adafruit_BMP280::FILTER_X16, Adafruit_BMP280::STANDBY_MS_500);

    while (!RTC.begin()) {
        debugging(F("The DS3231 RTC module could not be found."), SENSOR_DEBUGGING_LEVEL);
        delay(1000);
    }

    if (RTC.lostPower()) {
        RTC.adjust(DateTime(F(__DATE__), F(__TIME__)));
        debugging(F("The DS3231 RTC module ran out of power! The time was reset to the compile time."), SENSOR_DEBUGGING_LEVEL);
    }
    
    pinMode(GYML8511_OUT_PIN, INPUT);
    pinMode(GYML8511_3V3_PIN, INPUT);
    pinMode(TEMT6000_PIN, INPUT);
    pinMode(FC28_PIN, INPUT);
    pinMode(YL83_PIN, INPUT);
    pinMode(YFS201_PIN, INPUT);
    pinMode(RELAY_PIN, OUTPUT);

    xTaskCreatePinnedToCore(second_core_task, "second_core_task", 2048, NULL, 1, &second_core_task_handle, 0);
}

void connect_to_wifi(void) {
    debugging(F("Connecting..."), WIFI_DEBUGGING_LEVEL);

    WiFi.mode(WIFI_STA);

    if (STATIC_IP_ADDRESS) {
        IPAddress IP(IP_ADDRESS);
        IPAddress Gateway(GATEWAY_ADDRESS);
        IPAddress Subnet(SUBNET_MASK);
        IPAddress PrimaryDNS(PRIMARY_DNS);
        IPAddress SecondaryDNS(SECONDARY_DNS);

        WiFi.config(IP, Gateway, Subnet, PrimaryDNS, SecondaryDNS);
    }
    
    WiFi.setTxPower(WIFI_POWER_19_5dBm);
    WiFi.begin(F(WIFI_SSID), F(WIFI_PASSWORD));

    while (WiFi.status() != WL_CONNECTED) {
        if (micros() - start_time >= 4000 * 1000) {
            debugging(F("Failed to connect."), WIFI_DEBUGGING_LEVEL);
            ESP.restart();
        }
    }

    debugging("SSID: " + WiFi.SSID(), WIFI_DEBUGGING_LEVEL);
    debugging("IP: " + get_address_string(WiFi.localIP()), WIFI_DEBUGGING_LEVEL);
    debugging("Subnet: " + get_address_string(WiFi.subnetMask()), WIFI_DEBUGGING_LEVEL);
    debugging("Gateway: " + get_address_string(WiFi.gatewayIP()), WIFI_DEBUGGING_LEVEL);
    debugging("Primary DNS: " + get_address_string(WiFi.dnsIP()), WIFI_DEBUGGING_LEVEL);
    debugging("Secondary DNS: " + get_address_string(WiFi.dnsIP(1)), WIFI_DEBUGGING_LEVEL);
    debugging("MAC: " + WiFi.macAddress(), WIFI_DEBUGGING_LEVEL);
    debugging("BSSID: " + WiFi.BSSIDstr(), WIFI_DEBUGGING_LEVEL);
    debugging("RSSI: " + String(WiFi.RSSI()) + " bB", WIFI_DEBUGGING_LEVEL);
    debugging("Channel: " + String(WiFi.channel()), WIFI_DEBUGGING_LEVEL);

    esp_chip_info_t esp_chip;
    esp_chip_info(&esp_chip);
    
    debugging("Board: " + String(ARDUINO_BOARD), ESP32_DEBUGGING_LEVEL);
    debugging("Model: " + String(esp_chip.model), ESP32_DEBUGGING_LEVEL);
    debugging("CPU: " + String(getCpuFrequencyMhz()) + " MHz", ESP32_DEBUGGING_LEVEL);
    debugging("Cores: " + String(esp_chip.cores), ESP32_DEBUGGING_LEVEL);
    debugging("XTAL: " + String(getXtalFrequencyMhz()) + " MHz", ESP32_DEBUGGING_LEVEL);
    debugging("APB: " + String(getApbFrequency()) + " Hz", ESP32_DEBUGGING_LEVEL);
    debugging("Free Heap Memory: " + String(esp_get_free_heap_size()) + " bytes", ESP32_DEBUGGING_LEVEL);
    debugging("Chip ID: " + String(ESP.getEfuseMac()), ESP32_DEBUGGING_LEVEL);
    debugging("SDK Version: " + String(esp_get_idf_version()), ESP32_DEBUGGING_LEVEL);
    debugging("Review Version: " + String(esp_chip.revision), ESP32_DEBUGGING_LEVEL);
}

void disconnect_from_wifi(void) {
    debugging(F("Disconnecting..."), WIFI_DEBUGGING_LEVEL);
    WiFi.disconnect(true);

    runtime = (micros() - start_time) / 1000.0f;
    debugging("Runtime: " + String(runtime) + " ms", ESP32_DEBUGGING_LEVEL);
}

void send_sensor_data(void) {
    String body = "rain_level="             + String(rain_level)
                + "&soil_moisture="         + String(soil_moisture)
                + "&humidity="              + String(humidity)
                + "&temperature="           + String(temperature)
                + "&air_quality="           + String(air_quality)
                + "&atmospheric_pressure="  + String(atmospheric_pressure)
                + "&water_flow="            + String(water_flow)
                + "&water_level="           + String(water_level)
                + "&luminosity="            + String(luminosity)
                + "&ultraviolet_radiation=" + String(ultraviolet_radiation);

    request_post(F(SERVER_URL "/api/sensors/"), body);
}

String request_get(String host) {
    if (WiFi.status() != WL_CONNECTED) {
        debugging(F("It fails to make the request because there is no connection to the Wi-Fi."), REQUEST_DEBUGGING_LEVEL);
        return F("[]");
    }

    if (HTTPS_SERVER) {
        WiFiClientSecure *client = new WiFiClientSecure;

        if (!client) {
            debugging(F("Unable to connect to the HTTPS client."), REQUEST_DEBUGGING_LEVEL);
            return F("[]");
        }

        HTTPClient https;
        client->setCACert(ROOT_CA_CERTIFICATE);

        https.begin(*client, host);
        https.addHeader(F("Content-Type"), F("application/json"));

        int status_code = https.GET();
        String response = https.getString();

        debugging("GET " + host + " " + String(status_code), REQUEST_DEBUGGING_LEVEL);
        debugging(response, RESPONSE_DEBUGGING_LEVEL);
        
        https.end();
        return response;
    }
    
    HTTPClient http;

    http.begin(host);
    http.addHeader(F("Content-Type"), F("application/json"));

    int status_code = http.GET();
    String response = http.getString();

    debugging("GET " + host + " " + String(status_code), REQUEST_DEBUGGING_LEVEL);
    debugging(response, RESPONSE_DEBUGGING_LEVEL);
    
    http.end();
    return response;
}

String request_post(String host, String body) {
    if (WiFi.status() != WL_CONNECTED) {
        debugging(F("It fails to make the request because there is no connection to the Wi-Fi."), REQUEST_DEBUGGING_LEVEL);
        return F("[]");
    }

    if (HTTPS_SERVER) {
        WiFiClientSecure *client = new WiFiClientSecure;

        if (!client) {
            debugging(F("Unable to connect to the HTTPS client."), REQUEST_DEBUGGING_LEVEL);
            return F("[]");
        }

        HTTPClient https;
        client->setCACert(ROOT_CA_CERTIFICATE);

        https.begin(*client, host);
        https.addHeader(F("Content-Type"), F("application/x-www-form-urlencoded"));
        https.addHeader(F("Authorization"), F(DJANGO_API_TOKEN));

        int status_code = https.POST(body);
        String response = https.getString();

        debugging("POST " + host + " " + String(status_code), REQUEST_DEBUGGING_LEVEL);
        debugging(response, RESPONSE_DEBUGGING_LEVEL);
        
        https.end();
        return response;
    }
    
    HTTPClient http;
    WiFiClient client;
    
    http.begin(client, host);
    http.addHeader(F("Content-Type"), F("application/x-www-form-urlencoded"));
    http.addHeader(F("Authorization"), F(DJANGO_API_TOKEN));

    int status_code = http.POST(body);
    String response = http.getString();

    debugging("POST " + host + " " + String(status_code), REQUEST_DEBUGGING_LEVEL);
    debugging(response, RESPONSE_DEBUGGING_LEVEL);
    
    http.end();
    return response;
}

void update_datetime(void) {
    if (Serial.available()) {
        String user_input = Serial.readStringUntil('\n');

        if (user_input.isEmpty()) {
            return;
        }
        
        int day, month, year, hour, minute, second;
        int result = sscanf(user_input.c_str(), "%d/%d/%d %d:%d:%d", &day, &month, &year, &hour, &minute, &second);

        if (result != 6 || !valid_datetime(user_input)) {
            debugging(F("The date and time must be in the format \"dd/mm/yyyy hh:mm:ss\"."), SENSOR_DEBUGGING_LEVEL);
            return;
        }

        DateTime datetime(year, month, day, hour, minute, second);
        RTC.adjust(datetime);
        debugging(F("The date and time have been set successfully!"), SENSOR_DEBUGGING_LEVEL);
    }
}

void measure_water_consumption(void) {
    int high_pulse = pulseIn(YFS201_PIN, HIGH);
    int low_pulse = pulseIn(YFS201_PIN, LOW);

    float flow_time = high_pulse + low_pulse;
    float frequency = 1e6 / flow_time;
    
    water_flow = frequency / 7.5f;

    if (!isinf(frequency)) {
        consumption += water_flow / 60.0f;
    } else {
        water_flow = 0.0f;
    }
}

void second_core_task(void *argv) {
    while (true) {
        update_datetime();
        measure_water_consumption();
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void read_sensors_data(void) {
    start_time = micros();
    debugging("Water Flow: " + String(water_flow) + " L/min", SENSOR_DEBUGGING_LEVEL);
    
    rain_level = valid_value_range(map(analogRead(YL83_PIN), 2180, 4095, 100, 0));
    debugging("Rain Level: " + String(rain_level) + "%", SENSOR_DEBUGGING_LEVEL);

    soil_moisture = valid_value_range(map(analogRead(FC28_PIN), 1340, 4095, 100, 0));
    debugging("Soil Moisture: " + String(soil_moisture) + "%", SENSOR_DEBUGGING_LEVEL);

    water_level = HCSR04.measureDistanceCm();
    debugging("Distance: " + String(water_level) + " cm", SENSOR_DEBUGGING_LEVEL);

    luminosity = ((analogRead(TEMT6000_PIN) * (5.0f / 1024.0f)) / 10000.0f) * 1000000.0f * 2.0f;
    debugging("Luminosity: " + String(luminosity) + " lx", SENSOR_DEBUGGING_LEVEL);

    ultraviolet_radiation = map_float(analogRead(GYML8511_OUT_PIN) * (3.3f / analogRead(GYML8511_3V3_PIN)), 0.95f, 2.9f, 0.0f, 15.0f);
    debugging("Ultraviolet Radiation: " + String(ultraviolet_radiation) + " mW/cm²", SENSOR_DEBUGGING_LEVEL);

    if (!BMP280.begin(0x76)) {
        debugging(F("The BMP280 sensor was not found."), SENSOR_DEBUGGING_LEVEL);
    } else {
        atmospheric_pressure = BMP280.readPressure();
        debugging("Atmospheric Pressure: " + String(atmospheric_pressure) + " Pa", SENSOR_DEBUGGING_LEVEL);
    }

    humidity = DHT.readHumidity();
    temperature = DHT.readTemperature();
    
    if (isnan(humidity) || isnan(temperature)) {
        humidity = 0.0f;
        temperature = 0.0f;
        debugging(F("The DHT11 sensor was not found."), SENSOR_DEBUGGING_LEVEL);
    } else {
        debugging("Humidity: " + String(humidity) + "%", SENSOR_DEBUGGING_LEVEL);
        debugging("Temperature: " + String(temperature) + " °C", SENSOR_DEBUGGING_LEVEL);
    }

    air_quality = MQ135.getCorrectedPPM(temperature, humidity);

    if (isnan(air_quality)) {
        air_quality = 0.0f;
        debugging(F("The MQ-135 sensor was not found."), SENSOR_DEBUGGING_LEVEL);
    } else {
        debugging("Air Quality: " + String(air_quality) + " ppm", SENSOR_DEBUGGING_LEVEL);
    }
}

void analyze_irrigation_test(void) {
    String irrigation_tests = request_get(F(SERVER_URL "/api/irrigation-tests/?filter=last_available"));

    DynamicJsonDocument json(4096);
    deserializeJson(json, irrigation_tests);

    if (!json.size()) {
        return;
    }
    
    unsigned int id = json[0]["pk"];
    unsigned int irrigation_time = json[0]["fields"]["irrigation_time"];
    String created_at = split_time(json[0]["fields"]["created_at"]);
    String timeout = get_timeout(created_at, irrigation_time);
    String time_now = get_time();

    if (time_now >= created_at && time_now < timeout) {
        if (!water_pump_on) {
            consumption = 0.0f;
            water_pump_on = true;
        }
    
        digitalWrite(RELAY_PIN, HIGH);
    } else if (time_now >= timeout) {
        digitalWrite(RELAY_PIN, LOW);

        send_test_availability(id, false);
        send_water_consumption(consumption);

        water_pump_on = false;
    }
}

void analyze_irrigation_schedules(void) {
    String irrigation_schedules = request_get(F(SERVER_URL "/api/irrigation-schedules/?status=not_irrigated"));

    DynamicJsonDocument json(4096);
    deserializeJson(json, irrigation_schedules);

    for (size_t i = 0; i < json.size(); i++) {
        unsigned int id = json[i]["pk"];
        String irrigation_type = json[i]["fields"]["irrigation_type"];
        String time_now = get_time();
        String datetime_now = get_datetime(false);
    
        if (irrigation_type == "day") {
            String datetime_on = split_datetime(json[i]["fields"]["datetime_on"]);
            String datetime_off = split_datetime(json[i]["fields"]["datetime_off"]);
            
            if (datetime_now >= datetime_on && datetime_now < datetime_off) {
                if (!water_pump_on) {
                    consumption = 0.0f;
                    water_pump_on = true;

                    digitalWrite(RELAY_PIN, HIGH);
                    send_schedule_status(id, F("irrigating"));

                    String title = "Agenda de Irrigação";
                    String message = "O sistema de irrigação foi ligado às " + split_time(datetime_on) + " e será desligado às " + split_time(datetime_off) + ".";

                    send_notification(title, message);
                }
            } else if (datetime_now >= datetime_off) {
                water_pump_on = false;
                digitalWrite(RELAY_PIN, LOW);
                send_schedule_status(id, F("irrigated"));
                send_water_consumption(consumption);
            }
        } else if (irrigation_type == "time") {
            String irrigation_period = json[i]["fields"]["irrigation_period"];
            String time_on = json[i]["fields"]["time_on"];
            String time_off = json[i]["fields"]["time_off"];
            
            if (time_now >= time_on && time_now < time_off) {
                if (!water_pump_on) {
                    consumption = 0.0f;
                    water_pump_on = true;

                    digitalWrite(RELAY_PIN, HIGH);
                    send_schedule_status(id, F("irrigating"));

                    String title = "Agenda de Irrigação";
                    String message = "O sistema de irrigação foi ligado às " + time_on + " e será desligado às " + time_off + ".";

                    send_notification(title, message);
                }
            } else if (time_now >= time_off && water_pump_on) {
                water_pump_on = false;
                digitalWrite(RELAY_PIN, LOW);

                send_schedule_status(id, (irrigation_period == "unique") ? F("irrigated") : F("scheduled"));
                send_water_consumption(consumption);
            }
        } else if (irrigation_type == "humidity") {
            String irrigation_period = json[i]["fields"]["irrigation_period"];
            unsigned int humidity_on = json[i]["fields"]["humidity_on"];
            unsigned int humidity_off = json[i]["fields"]["humidity_off"];
            bool night_irrigation = json[i]["fields"]["night_irrigation"];
            
            if (soil_moisture >= humidity_on && soil_moisture < humidity_off) {
                if (night_irrigation || (time_now >= "05:00:00" && time_now <= "18:00:00")) {
                    if (!water_pump_on) {
                        consumption = 0.0f;
                        water_pump_on = true;

                        digitalWrite(RELAY_PIN, HIGH);
                        send_schedule_status(id, F("irrigating"));

                        String title = "Agenda de Irrigação";
                        String message = "O sistema de irrigação foi ligado às " + time_now + " ao detectar a umidade de solo com o valor de " + String(humidity_on) + "% e será desligado ao atingir " + String(humidity_off) + "%.";
            
                        send_notification(title, message);
                    }
                } else if (soil_moisture >= humidity_off && water_pump_on) {
                    water_pump_on = false;
                    digitalWrite(RELAY_PIN, LOW);

                    send_schedule_status(id, (irrigation_period == "unique") ? F("irrigated") : F("scheduled"));
                    send_water_consumption(consumption);
                }
            }
        } else if (irrigation_type == "flow") {
            String irrigation_period = json[i]["fields"]["irrigation_period"];
            float water_flow = json[i]["fields"]["water_flow"];
            String time_on = json[i]["fields"]["time_on"];
            unsigned int timeout_in_seconds = 5;
            String timeout = get_timeout(time_on, timeout_in_seconds);
            
            if (time_now >= time_on && time_now < timeout) {
                if (!water_pump_on) {
                    consumption = 0.0f;
                    water_pump_on = true;

                    digitalWrite(RELAY_PIN, HIGH);
                    send_schedule_status(id, F("irrigating"));

                    String title = "Agenda de Irrigação";
                    String message = "O sistema de irrigação foi ligado às " + time_on + " e será desligado após irrigar " + String(water_flow) + " litros de água.";
        
                    send_notification(title, message);
                }
            } else if (consumption >= water_flow && water_pump_on) {
                water_pump_on = false;
                digitalWrite(RELAY_PIN, LOW);
                
                send_schedule_status(id, (irrigation_period == "unique") ? F("irrigated") : F("scheduled"));
                send_water_consumption(consumption);
            }
        }
    }
}

void send_notification(String title, String message) {
    String body = "title=" + title + "&message=" + message;
    request_post(F(SERVER_URL "/api/notifications/"), body);
}

void send_schedule_status(unsigned int id, String status) {
    String body = "id=" + String(id) + "&status=" + status;
    request_post(F(SERVER_URL "/api/change-status/"), body);
}

void send_test_availability(unsigned int id, bool available) {
    String body = "id=" + String(id) + "&available=" + String(available);
    request_post(F(SERVER_URL "/api/change-availability/"), body);
}

void send_water_consumption(float consumption) {
    String body = "consumption=" + String(consumption);
    request_post(F(SERVER_URL "/api/water-consumption/"), body);
}

String get_time(void) {
    char time[9];
    DateTime now = RTC.now();
    snprintf(time, 9, "%02d:%02d:%02d", now.hour(), now.minute(), now.second());
    return time;
}

String get_timeout(const String &time, unsigned int increase) {
    char timeout[9];
    int hour, minute, second;

    sscanf(time.c_str(), "%d:%d:%d", &hour, &minute, &second);
    DateTime now(DateTime(2023, 1, 1, hour, minute, second) + TimeSpan(0, 0, 0, increase));
    snprintf(timeout, 9, "%02d:%02d:%02d", now.hour(), now.minute(), now.second());

    return timeout;
}

String get_datetime(bool formatted) {
    char datetime[20];
    DateTime now = RTC.now();

    if (formatted) {
        snprintf(datetime, 20, "%02d/%02d/%04d %02d:%02d:%02d", now.day(), now.month(), now.year(), now.hour(), now.minute(), now.second());
    } else {
        snprintf(datetime, 20, "%04d-%02d-%02dT%02d:%02d:%02d", now.year(), now.month(), now.day(), now.hour(), now.minute(), now.second());
    }

    return datetime;
}

bool valid_datetime(const String &datetime) {
    regex_t regex;
    regcomp(&regex, "^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/([0-9]{4}) (2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])$", REG_EXTENDED);
    
    int result = regexec(&regex, datetime.c_str(), 0, NULL, 0);
    regfree(&regex);
    
    if (!result) {
        return true;
    }
    
    return false; 
}

String get_address_string(IPAddress address) {
    String buffer = "";

    for (size_t i = 0; i < 4; i++) {
        if (i > 0) {
            buffer += ".";
        }

        buffer += String(address[i]);
    }

    return buffer;
}

String split_time(String datetime) {
    return datetime.substring(11, 19);
}

String split_datetime(String datetime) {
    return datetime.substring(0, 19);
}

int valid_value_range(int range) {
    return (range < 0) ? 0 : (range > 100) ? 100 : range;
}

float map_float(float x, float in_min, float in_max, float out_min, float out_max) {
    float result = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
    return (result > 0.0f) ? result : 0.0f;
}
