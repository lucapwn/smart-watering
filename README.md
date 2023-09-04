# Smart Watering

IoT platform for remote monitoring and control of a sustainable irrigation system developed with the ESP32.

![Badge](https://img.shields.io/static/v1?label=license&message=MIT&color=1E90FF)
![Badge](https://img.shields.io/static/v1?label=build&message=passing&color=00d110)

## Content

- [About](#about)
  - [Features](#features)
- [Support](#support)
- [Materials](#materials)
  - [Connecting the components](#connecting-the-components)
  - [System Example](#system-example)
- [Running](#running)
  - [IoT Platform](#iot-platform)
  - [Irrigation System](#irrigation-system)
- [Author](#author)
- [License](#license)

## About

Smart Watering is an IoT platform developed with the ESP32 for remote monitoring and control of sustainable irrigation. It includes a REST API for seamless communication between the platform and the ESP32.

Watch the example video on YouTube at [```https://www.youtube.com/watch?v=AMdGk-LIUu8```](https://www.youtube.com/watch?v=AMdGk-LIUu8).

<img src="https://github.com/lucapwn/smart-watering/assets/58787069/4b6ed894-7dd2-48f9-94d8-ccdb8b9cd15e" alt="Smart Watering" width="1000">

### Features

Users can schedule irrigation in various ways, such as by day/time, soil moisture, or water flow. This flexibility allows for dynamic and specific values, making the platform suitable for managing diverse plant types. Automatic irrigation can be set for single or daily periods.

In terms of irrigation management, users have full control over adding, listing, editing, and deleting schedules. They can search for specific attributes, apply filters, and sort information in table columns.

The system allows for quick irrigation tests to ensure proper functioning. Real-time sensor data is displayed through graphs, enabling users to monitor irrigation and make informed decisions based on ideal weather conditions. Meteorological data includes temperature, air quality, humidity, pressure, heat index, rainfall, light intensity, and UV radiation. Water-related information covers reservoir capacity and consumption.

Remote configuration options are available, allowing users to customize temperature units, reservoir capacity calculations, system notifications, color schemes, and the platform's menu.

Data can be exported in CSV format, offering comprehensive insights. Reports provide numerical data for analysis, eliminating the need to access the database or user interface directly. Users can select desired data and time frames, easily share reports, and archive them for future reference.

To enhance user experience and resource location, a search field has been implemented for specific elements and functionalities, reducing search time.

The platform is developed using Django framework, providing efficient management of database information through an integrated administration page. This facilitates user, sensor, permission, authentication, and setting management, ensuring an organized and accessible platform for administrators.

Moreover, the platform offers an API for seamless communication with the irrigation system. It serves as an interface for data collection, command sending, and IoT device configuration. The API is protected by authentication features, granting access only to authorized systems. Users gain instant access to critical information, including sensor data, irrigation schedules, notifications, water consumption, and platform settings.

## Support

The platform is compatible and responsive on mobile devices, tablets and desktops, ensuring its adaptation to different screen sizes and operating systems.

## Materials

To set up the irrigation system, you will need the following materials:

Name                       | Type 
-------------------------- | ---------------
FC-28                      | Sensor
YL-83                      | Sensor
DHT11                      | Sensor
MQ-135                     | Sensor
BMP280                     | Sensor
GY-8511                    | Sensor
TEMT6000                   | Sensor
HCSR-04                    | Sensor
YF-S201                    | Sensor 
Relay                      | Actuator
RTC DS3231                 | Module
ESP32-WROOM-32U DevKitC V4 | Microcontroller
Jumpers                    | Component
Breadboard                 | Component
2.4 GHz Antenna for ESP32  | Component
5V USB charger             | Component
Micro USB cable            | Component
Battery CR2032             | Component

### Connecting the components

The GPIOs of the sensors and actuators must be connected to the ESP32 as follows:

ESP32 | DHT11 | HCSR-04 | YL-83 | Relay | YF-S201 | DS3231 | TEMT6000 | FC-28 | GY-8511    | MQ-135
----- | ----- | ------- | ----- | ----- | ------- | ------ | -------- | ----- | ---------- | ------
4     | A0    |         |       |       |         |        |          |       |            | 
12    |       | ECHO    |       |       |         |        |          |       |            |
13    |       | TRIG    |       |       |         |        |          |       |            |
14    |       |         | A0    |       |         |        |          |       |            |
18    |       |         |       | IN    |         |        |          |       |            |
19    |       |         |       |       | D0      |        |          |       |            |
21    |       |         |       |       |         | SDA    |          |       |            |
22    |       |         |       |       |         | SCL    |          |       |            |
25    |       |         |       |       |         |        | A0       |       |            |
27    |       |         |       |       |         |        |          | A0    |            |
32    |       |         |       |       |         |        |          |       | A0         |
33    |       |         |       |       |         |        |          |       | EN and 3V3 |
34    |       |         |       |       |         |        |          |       |            | A0
GND   | GND   | GND     | GND   | GND   | GND     | GND    | GND      | GND   | GND        | GND
5V    | VCC   | VCC     | VCC   | VCC   | VCC     | VCC    | VCC      | VCC   |            | VCC
3V3   |       |         |       |       |         |        |          |       | 3V3        |

### System Example

After connecting the components, the system should look similar to the system illustrated in the image below.

<img src="https://github.com/lucapwn/smart-watering/assets/58787069/3ede2807-cf93-4cfe-ad45-bde694d29e4a" width="540">

## Running

### IoT Platform

With Git installed, clone the project repository:

~~~console
foo@bar:~$ git clone https://github.com/lucapwn/smart-watering.git
~~~

With Python installed, go to the main project folder and install the application dependencies:

~~~console
foo@bar:~$ pip install -r requirements.txt
~~~

Apply the changes to the application database:

~~~console
foo@bar:~$ python manage.py migrate
~~~

Create a user with administrator permissions:

~~~console
foo@bar:~$ python manage.py createsuperuser
~~~

Run the application server:

~~~console
foo@bar:~$ python manage.py runserver 0.0.0.0:80
~~~

You can now access the application on your computer at [```http://localhost```](http://localhost). If you want to access the platform on another device, you need to get the IP address of the computer that is running this application, then enter that address into a browser.

### Irrigation System

With the Arduino IDE installed and configured to run ESP32 applications, install the necessary libraries included in the [```esp32/libraries```](https://github.com/lucapwn/smart-watering/tree/main/esp32/libraries) folder of the project.

After that, configure the ESP32 to your preference in the [```smart_watering.h```](https://github.com/lucapwn/smart-watering/blob/main/esp32/main/smart_watering.h) header file in [```esp32/main```](https://github.com/lucapwn/smart-watering/tree/main/esp32/main).

Finally, upload the code from the [```main.ino```](https://github.com/lucapwn/smart-watering/blob/main/esp32/main/main.ino) file in [```esp32/main```](https://github.com/lucapwn/smart-watering/tree/main/esp32/main) to the ESP32.

## Author

Developed by [Lucas Araújo](https://github.com/lucapwn).

## License

This software is [MIT](https://choosealicense.com/licenses/mit/) licensed.
