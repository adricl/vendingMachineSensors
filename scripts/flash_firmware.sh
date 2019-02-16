#!/bin/sh

echo '### Erase flash ###'
esptool.py --chip esp32 --port $AMPY_PORT erase_flash

echo '### Flash microPython ###'
esptool.py --chip esp32 --port $AMPY_PORT write_flash -z 0x1000 firmware/esp32-20190125-v1.10.bin
