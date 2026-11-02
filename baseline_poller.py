import time
import csv
from datetime import datetime, timezone
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('127.0.0.1', port=502)
client.connect()

with open('/home/tommy55/baseline_log.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    while True:
        try:
            result = client.read_holding_registers(address=0, count=1, device_id=0)
            ts = datetime.now(timezone.utc).isoformat()
            value = result.registers[0] if not result.isError() else 'ERROR'
        except Exception as e:
            ts = datetime.now(timezone.utc).isoformat()
            value = f'ERROR: {e}'
            # try to reconnect so a dropped connection doesn't kill the loop
            try:
                client.close()
            except Exception:
                pass
            client.connect()
        writer.writerow([ts, value])
        f.flush()
        print(ts, value)
        time.sleep(2)
