from pymodbus.client import ModbusTcpClient
import time

client = ModbusTcpClient('192.168.1.200', port=502)
client.connect()

client.write_register(address=1, value=7777, device_id=0)
print("Wrote 7777 to unprotected register")

time.sleep(2)
result = client.read_holding_registers(address=1, count=1, device_id=0)
print("After 2s:", result.registers)

client.close()
