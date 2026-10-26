import socket

HOST = '192.168.1.200'
PORT = 502

# Modbus TCP frame: [Transaction ID(2)][Protocol ID(2)][Length(2)][Unit ID(1)][Function Code(1)][Data...]
transaction_id = b'\x00\x01'
protocol_id = b'\x00\x00'
unit_id = b'\x00'
function_code = b'\x2b'   # 43 decimal - not implemented by OpenPLC
data = b'\x0e\x01\x00'    # arbitrary payload, doesn't matter - server should reject on function code alone

payload = unit_id + function_code + data
length = len(payload).to_bytes(2, byteorder='big')
frame = transaction_id + protocol_id + length + payload

print("Sending illegal function code 0x2B...")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(3)
s.connect((HOST, PORT))
s.sendall(frame)

try:
    response = s.recv(256)
    print("Raw response bytes:", response.hex())
    if len(response) >= 8:
        resp_function_code = response[7]
        print(f"Response function code byte: {hex(resp_function_code)}")
        if resp_function_code & 0x80:
            print(f"Exception response confirmed. Exception code: {response[8]}")
except socket.timeout:
    print("No response received (timeout) - server may have silently dropped the request")

s.close()
