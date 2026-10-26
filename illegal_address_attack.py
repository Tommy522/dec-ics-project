from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.1.200', port=502)
client.connect()

print("Reading register 500 (does not exist on this testbed)...")
result = client.read_holding_registers(address=500, count=1, device_id=0)

if result.isError():
    print(f"Server returned an exception: {result}")
else:
    print(f"Unexpected success: {result.registers}")

client.close()
