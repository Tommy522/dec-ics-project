import time
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.1.200', port=502)
client.connect()

print("Starting rapid-write flood...")
for i in range(20):
    value = 9000 + i  # varying anomalous values each write
    client.write_register(address=0, value=value, device_id=0)
    print(f"Wrote {value}")
    time.sleep(0.05)  # 20 writes over ~1 second

time.sleep(0.5)
result = client.read_holding_registers(address=0, count=1, device_id=0)
print("Final read:", result.registers)

client.close()
