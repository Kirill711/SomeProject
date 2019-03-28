import network
import socket
from machine import UART
import micropython
import time


def read_and_send(comport, request, lst, len_lst):
    comport.write(request)
    data = comport.read(5)
    # for i in range(500):
    #     lst.append(str(i).encode())
    lst.append(data)
    if len(lst) == len_lst:
        for val in lst:
            UDPClientSocket.sendto(val, (UDP_IP, serverPort))
            UDPClientSocket.settimeout(5)
        UDPClientSocket.sendto(b'End', (UDP_IP, serverPort))
        lst.clear()
        UDPClientSocket.sendto(str(time.ticks_ms()).encode(), (UDP_IP, serverPort))
        uart.read()


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('ORBI27', 'narrowship322')
while not wlan.isconnected():
    time.sleep(1)

UDP_IP = "192.168.1.21"
serverPort = 50500
UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

UDPClientSocket.sendto(b'Hello_UDP_Server', (UDP_IP, serverPort))
msg, addr = UDPClientSocket.recvfrom(16)
if msg == b'Hello_UDP_Client':
    UDPClientSocket.sendto(b'ESP32', (UDP_IP, serverPort))

# buffer = []
# while True:
#     read_and_send(buffer, 500)

uart = UART(2, 115200)
uart.init(115200, bits=8, parity=None, stop=1, timeout=50)
micropython.kbd_intr(-1)
uart.read()

buffer = []
requests = (b'\x55\x95\x0D', b'\x55\x0A\xA1', b'\x55\x08\xA0\x01\x00', b'\x55\x0A\xA0', b'\x55\x08\xA1\x00\x20',
            b'\x55\x08\xA0\x00\x00', b'\x55\x0A\xA1', b'\x55\x0A\xA0')
for value in requests:
    read_and_send(uart, value, buffer, 8)

while True:
    read_and_send(uart, b'\x55\x0A\xA0', buffer, 500)
