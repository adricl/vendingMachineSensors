import machine
import dht
import onewire
import sgp30
import ds18x20
import utime
import json
from umqtt.robust import MQTTClient
from slimDNS import SlimDNSServer, bytes_to_dotted_ip
import network

#MQTT_SERVER_MDNS_ADDRESS="iot.local"
MQTT_SERVER_MDNS_ADDRESS="wombat-pi.local"

WAIT_TIME = 30

SSID=""
PASSWORD=""


topTempHumid = None
oneWires = None
oneWireDevices = None
airMonitor = None
client = None
wlan = None
unique_id = None
ip = None


def send_mqtt(payload_out):
    global ip
    slimDNS = None

    try:
        slimDNS = SlimDNSServer(wlan.ifconfig()[0])
        host_address_bytes = slimDNS.resolve_mdns_address(MQTT_SERVER_MDNS_ADDRESS)
        print(host_address_bytes)
        if ip != None:
            print(ip)
        ip = bytes_to_dotted_ip(host_address_bytes)
    except Exception as e:
        print("Could not connect find mDNS address " + str(e))

    if ip != None:
        print('Connecting to MQTT server:', ip)
        mqtt = None
        try:
            mqtt = MQTTClient(client_id=unique_id, server=ip, port=1883)        
            mqtt.connect()
        except Exception as e:
            print('Could not connect to MQTT server')
            return

        try: 
            mqtt.publish("vendingmachine/sensors", payload_out)
            mqtt.disconnect()
        except Exception:
            print("Failed To Publish")

def get_data():
    payload = {}
    payload["topTemperature"] = 0
    payload["topHumidity"] = 0
    try:
        topTempHumid.measure()
        payload["topTemperature"] = topTempHumid.temperature()
        payload["topHumidity"] = topTempHumid.humidity()
    except Exception:
        print("Failed to get TopTemp Humid Sensor")
    try:
        oneWires.convert_temp()
    except Exception:
        print("Failed to talk to one wire")

    payload["waterTemperature"] = 0
    utime.sleep_ms(1000)
    try:
        payload["waterTemperature"] = oneWires.read_temp(oneWireDevices[0])
    except Exception:
        print("Failed to get water temp")
    
    payload["co2eq"] = 0
    payload["tvoc"] = 0
    try:
        airMonitor.iaq_init()
        payload["co2eq"] = airMonitor.co2eq
        payload["tvoc"] = airMonitor.tvoc
        #print("co2eq = %d ppm \t tvoc = %d ppb" % (payload["co2eq"], payload["tvoc"]))
    except Exception:
        print("Failed to get air quality")

    payload_out = json.dumps(payload)
    print(payload_out)
    return payload_out

def initialise():
    global topTempHumid, oneWires, oneWireDevices, airMonitor
    print("Initialising Sensors")

    topTempHumid = dht.DHT22(machine.Pin(23)) #DHT22
    oneWires = ds18x20.DS18X20(onewire.OneWire(machine.Pin(22))) #onewire Probe
    oneWireDevices = oneWires.scan()
    i2c = machine.I2C(scl=machine.Pin(19), sda=machine.Pin(18))
    airMonitor = sgp30.SGP30(i2c)

    airMonitor.iaq_init()
    airMonitor.set_iaq_baseline(0x8973, 0x8aae)

def get_unique_id():
  id = machine.unique_id()
  id = ("000000" + hex((id[3] << 16) | (id[4] << 8) | id[5])[2:])[-6:]
  return id
  
def do_connect():
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
    print('Network config:', wlan.ifconfig())



wlan = network.WLAN(network.STA_IF)
wlan.active(True)
unique_id = get_unique_id()

initialise()

while True:
    print('Starting transmission')
    do_connect()
    data = get_data()
    send_mqtt(data)
    wlan.disconnect()
    utime.sleep(WAIT_TIME)
