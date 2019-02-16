# Vending Machine Hydroponic Sensors
This is designed to run in our vending machine and to monitor the water temperature and ambient temperate, humidity and CO2 levels.

Its written in Micropython for the EPS32.

Sensors attached:
SGP30 - CO2 Sensor and Volatile gasses
DHT20 - Temperature and Humidity Sensor
Ds18x20 - one wire waterproof sensor.

## To install:
Select the port the ESP is attached to and export it:
export $AMPY_PORT=/dev/ttyUSBO 
./scripts/flash_firmware.sh


once the firmware is flashed you can upload the micropython code
This will require you to have mpfshell installed 
./scripts/flash_standard_mpfshell.sh


