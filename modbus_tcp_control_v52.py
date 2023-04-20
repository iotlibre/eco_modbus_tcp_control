#!/usr/bin/env python


'''
Este script de python esta preparado para actuar sobre una bomba de calor
recibe los comandos por el API de mqtt y los ejecuta
el API de mqtt consiste en:
Los métodos están en msg.payload en formato json
Los comandos configurados son:
* {"name":"file_read", "value": "read"}
* {"name":"bdc_configure", "value": "read"}

file_read: Lee el fichero comportamiento_bdc.json que esta ubicado en el mismo directorio del escript

Los comandos pueden venir desde NodeRed localmente o remotamente
La lectura del fichero diaria y la configuración hoararia se hace enviando las ordenes desde NodeRed

El API de modbus ha cambiado con respoecto a la versión anterior
pyModbus Version 3.2.2 is the current release (Supports Python >=3.8)
  
'''
import os
import configparser
import paho.mqtt.client as mqtt
import logging
from logging.handlers import RotatingFileHandler
import json
import datetime
import time
from pyModbusTCP.client import ModbusClient

# Para obtener mas detalle: level=logging.DEBUG
# Para comprobar el funcionamiento: level=logging.INFO
logging.basicConfig(
        level=logging.DEBUG,
        handlers=[RotatingFileHandler('./logs/log_modbus_tcp_control.log', maxBytes=1000000, backupCount=10)],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')

# Parseo de variables del .ini
parser = configparser.ConfigParser()
parser.read('modbus_tcp_control.ini')

# Parseo de las variables de emonCMS
tx_modbus_ip = parser.get('modbus_server','modbus_ip')
tx_modbus_port = parser.get('modbus_server','modbus_port')
mqtt_topic = parser.get('listener','topic')
mqtt_ip = parser.get('listener','mqtt_ip')
mqtt_login = parser.get('listener','mqtt_login')
mqtt_password = parser.get('listener','mqtt_password')

def file_read():
    logging.debug("file_read()")
    dataDOk = False
    global dataD
    if os.path.isfile('comportamiento_bdc.json'):
        logging.debug("load file: comportamiento_bdc.json")
        lectura = open("comportamiento_bdc.json", "r", encoding="utf-8")
        jsonF= True
        try:
            dataD = json.load(lectura) 
        except:
            logging.debug("error al intentar transformar a json")
            jsonF= False
        if jsonF:               
            if type(dataD) == type([]):
                if len(dataD) == 24:
                    for h in dataD:
                        if 'MarchaBdC' in h:
                            dataDOk = True
                        else:
                            dataDOk = False
                            break  
                    
    if not dataDOk:
        logging.debug("comportamiento_por_defecto.json")
        lectura = open("comportamiento_por_defecto.json", "r", encoding="utf-8")
        dataD = json.load(lectura)             
    logging.debug('dataDOk: %d' , dataDOk)
    lectura.close()
    logging.debug(dataD)
    
def bdc_configure_tx(MarchaBdcJ_,TstorageJ_):
    logging.debug("bdc_configure_tx()")
    res1 = cli.write_single_register(1002, MarchaBdcJ_)
    logging.debug("write MarchaBdcJ: %d" , res1)
    res1 = cli.write_single_register(1005, TstorageJ_)
    logging.debug("write TstorageJ: %d" ,res1)
    
def bdc_configure():
    logging.debug("bdc_configure()")
    if 'dataD' in globals():
        logging.debug('Variable exist.')
    else:
        logging.debug('Variable don\'t exist.')
        file_read()
    hora_actual = datetime.datetime.now().time()
    MarchaBdcJ = dataD[hora_actual.hour]['MarchaBdC']
    TstorageJ = dataD[hora_actual.hour]['Tstorage']
    logging.debug('MarchaBdC: %d' , MarchaBdcJ)
    logging.debug('Tstorage: %d' , TstorageJ)
    bdc_configure_tx(MarchaBdcJ,TstorageJ)
   
def on_connect(client, obj, flags, rc):
    logging.debug("rc: " + str(rc))
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    data_string = msg.payload
    decoded_ok = 1
    
    logging.info("mqtt message:")
    logging.info(data_string)
    
    #Decoded
    decoded = json.loads(data_string)
    
    try:
        name_1=     str(decoded["name"])
        value_1 =   str(decoded["value"])

    except:
        logging.info("error in decoded")
        decoded_ok = 0
    
    if decoded_ok == 1:
        logging.debug("name: ")
        logging.debug(name_1)
        logging.debug("value: ")
        logging.debug(value_1)
        if name_1 == "file_read":
            file_read()
        elif name_1 == "bdc_configure":
            bdc_configure() 
        else:
            logging.debug("name no configurado")  
    else:
        logging.info("decoded_ok == 0:")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        result="Unexpected disconnection"
        logging.info(result)


cli = ModbusClient('192.168.3.141', port=502, debug=False, auto_open=True, auto_close=True)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_diconnect = on_disconnect

client.username_pw_set(mqtt_login,mqtt_password)
client.connect(mqtt_ip, 1883, 60)
logging.debug("<- inicio loop_forever ->")
client.loop_forever(timeout=1.0, max_packets=1, retry_first_connection=False)





