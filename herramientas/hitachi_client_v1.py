#!/usr/bin/env python
from pyModbusTCP.client import ModbusClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


cli = ModbusClient('192.168.3.141', port=502, debug=False, auto_open=True)
# assert cli.open()

# Inicio de la consulta

res1 = cli.read_holding_registers(1050, 1)
# assert not res1.isError()

print("-" * 30)
print("Registros")
print(res1)

# Inicio de la consulta

res1 = cli.read_holding_registers(1055, 1)
# assert not res1.isError()

print("-" * 30)
print("Registros")
print(res1)

# fin de la consulta

