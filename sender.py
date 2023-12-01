import smbus
from time import sleep

serverMACaddress = 'D8:3A:DD:3C:D9:91'
port = 4
data = 1
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.connect((serverMACaddress, port))

bus = smbus.SMBus(1)
ADC_ADDRESS = 0x4b

try:
    while True:
        #Read sensor input from ADC
        data = bus.read_i2c_block_data(ADC_ADDRESS, 0)
        client_socket.send(data[0])
        sleep(0.25)

except KeyboardInterrupt:
    pass