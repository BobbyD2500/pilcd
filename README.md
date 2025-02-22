# PiLCD
This project allows an eight-character, 7-segment display using a MAX7219 driver connected via SPI to display text specified in MQTT messages. As the name implies, the project was originally desinged to run on a Raspberry Pi but should run on any device with SPI drivers.

## Environmental Variables
The following variables are used:
|Variable|Required?|Description|Default Value|
|---|---|---|---|
|MQTT_USERNAME|Yes|Username used for MQTT Broker||
|MQTT_PASSWORD|Yes|Password used for MQTT Broker||
|MQTT_HOST|No|Hostname or IP Address of MQTT Broker|127.0.0.1|
|MQTT_PORT|No|Port used by MQTT Broker|1883|
|MQTT_PREFIX|No|Prefix of MQTT topics|pilcd|
|MQTT_SECURE|No|Whether TLS is used for the MQTT Connection (see TLS section below)|False|
|DEBUG|No|Whether debug messaging is printed to output|False|
|SPI_DEVICE|No|SPI Device Number|0|
|SPI_PORT|No|SPI Port Number|0|

## TLS
If TLS is used, the CA certificate should be copied to /etc/ssl/certs/ca-certificates.crt. Alternatively, if using Docker, a volume mount can be used to provide the certificate.

## Docker Example
For use with Compose.
~~~
services:
  pilcd:
    build: pilcd
    container_name: pilcd
    restart: unless-stopped
    devices:
      - /dev/spidev0.0
    privileged: true
    environment:
      - MQTT_HOST=127.0.0.1
      - MQTT_PREFIX=pilcd
      - MQTT_USERNAME=mqtt
      - MQTT_PASSWORD=ultrasecretpassword
      - MQTT_PORT=1883 
      - MQTT_SECURE=False
      - DEBUG=False
      - SPI_PORT=0
      - SPI_DEVICE=0
~~~
