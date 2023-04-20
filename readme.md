# eco_modbus_tcp_control

Este script de python esta preparado para actuar sobre una bomba de calor o cualquier otro sistema que sea controlable mediante modbus TP
recibe los comandos por el API de mqtt y los ejecuta
## API de mqtt
Los métodos deben recibirse en msg.payload en formato json.

Los comandos configurados son:
- {"name":"file_read", "value": "read"}
- {"name":"bdc_configure", "value": "read"}

file_read: Lee el fichero comportamiento_bdc.json que esta ubicado en el mismo directorio del escript.

Los comandos pueden venir desde NodeRed localmente o remotamente. La lectura del fichero diaria y la configuración hoararia se hace enviando las ordenes desde NodeRed
## Notas
El API de modbus ha cambiado con respoecto a la versión anterior.
pyModbus Version 3.2.2 is the current release (Supports Python >=3.8).
