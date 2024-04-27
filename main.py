from machine import ADC,Pin
from time import sleep
import dht
import network
from robust import MQTTClient
import gc
import sys

adc = ADC(0)
sensor = dht.DHT11(Pin(16))
buzzer= Pin(13, Pin.OUT)
relay1 = Pin(5, Pin.OUT)
relay2 = Pin(4, Pin.OUT)

relay1.value(1)
relay2.value(1)

#=======================================================
THINGSPEAK_MQTT_CLIENT_ID = b"PSwCHCQEFSUhNBs6LB4OIBo"
THINGSPEAK_MQTT_USERNAME = b"PSwCHCQEFSUhNBs6LB4OIBo"
THINGSPEAK_MQTT_PASSWORD = b"4l9qnjbn3We2fzaYmvi6T3Ej"
THINGSPEAK_CHANNEL_ID = b'2511429'
#=======================================================

THINGSPEAK_MQTT_USERNAME = THINGSPEAK_MQTT_CLIENT_ID

client = MQTTClient(server=b"mqtt3.thingspeak.com",
                    client_id=THINGSPEAK_MQTT_CLIENT_ID, 
                    user=THINGSPEAK_MQTT_USERNAME, 
                    password=THINGSPEAK_MQTT_PASSWORD, 
                    ssl=False)
                    
try:            
    client.connect()
except Exception as e:
    print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
    sys.exit()


def dht_sensor():
    try:
        sleep(2)
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        """
        print('Sıcaklık: %3.1f C' %t)
        print('Nem: %3.1f %%' %h)
        
        """
    except OSError as e:
        print('sensör okunmadı')
        
    return [t,h]


def toprak_sensor():
    sleep(0.1)
    deger= adc.read()
    yüzde =100 -((100 * deger) / 1024)
    return [deger,yüzde]


def water_pump():
    
    deger, yüzde = toprak_sensor()
    if yüzde<10:
        buzzer.on()
        relay1.value(0)   
        sleep(1)
    else :
        buzzer.off()
        relay1.value(1)
        sleep(1)
    return relay1.value()


PUBLISH_PERIOD_IN_SEC = 15
while True:
    sıcaklık, nem = dht_sensor()
    sleep(0.1)
    deger, yüzde = toprak_sensor()
    sleep(0.1)
    durum = water_pump()
    

    
    try:
        freeHeapInBytes = gc.mem_free()
        credentials = bytes("channels/{:s}/publish".format(THINGSPEAK_CHANNEL_ID), 'utf-8')  
        payload = bytes("field1={:.1f}&field2={:.1f}&field3={:.1f}&field4={:.1f}\n".format(sıcaklık, nem, yüzde,durum), 'utf-8')
        client.publish(credentials, payload)
        sleep(PUBLISH_PERIOD_IN_SEC)
    except KeyboardInterrupt:
        print('Ctrl-C pressed...exiting')
        client.disconnect()
        break


