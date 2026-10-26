import time
import csv
from datetime import datetime, timezone
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.1.200', port=502)
client.connect()

with open('baseline_log.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    while True:
        result = client.read_holding_registers(address=0, count=1, device_id=0)
        ts = datetime.now(timezone.utc).isoformat()
        value = result.registers[0] if not result.isError() else 'ERROR'
        writer.writerow([ts, value])
        f.flush()
        print(ts, value)
        time.sleep(2)
