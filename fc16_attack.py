from pymodbus.client import ModbusTcpClient
import time

client = ModbusTcpClient('192.168.1.200', port=502)
client.connect()

# Write Multiple Registers (FC16) - overwrite both registers at once
client.write_registers(address=0, values=[8888, 4444], device_id=0)
print("Sent FC16 write: register 0 = 8888, register 1 = 4444")

time.sleep(1)
result = client.read_holding_registers(address=0, count=2, device_id=0)
print("After 1s:", result.registers)

client.close()
