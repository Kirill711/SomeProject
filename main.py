import network
import socket
from machine import UART
import micropython
import esp
import uos
import time


class Interrupt(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        elapsed_time = "Elapsed time: {:.3f} sec".format(time.time() - self._startTime)
        UDPClientSocket.sendto(elapsed_time.encode(), (UDP_IP, serverPort))


def read_and_send(comport, request, lst, len_lst):
    comport.write(request)
    time.sleep(0.025)
    data = comport.read(5)  # '5' - кол-во принимаемых платой байт
    lst.append(data)
    if len(lst) == len_lst:
        for i, val in enumerate(lst):
            UDPClientSocket.sendto(val, (UDP_IP, serverPort))
        lst.clear()


def send_bytes(comport, request, sock, ip, port):
    comport.write(request)
    time.sleep(1)
    answer = comport.read()
    sock.sendto(answer, (ip, port))


sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)

sta_if.active(True)
ap_if.active(False)
sta_if.connect('ORBI27', 'narrowship322')
while not sta_if.isconnected():
    time.sleep(1)

UDP_IP = "255.255.255.255"
serverPort = 5000

UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # create a UDP socket at client side

UDPClientSocket.sendto(b'Hello_UDP_Server', (UDP_IP, serverPort))  # send to server using created UDP socket
msg, addr = UDPClientSocket.recvfrom(16)
if msg == b'Hello_UDP_Client':
    UDPClientSocket.sendto(b'ESP32', (UDP_IP, serverPort))

esp.osdebug(None)
uos.dupterm(None, 0)
# timeout=0
uart = UART(2, 115200)  # создание объекта UART, "2"- Номер UART-порта микроконтроллера
uart.init(115200, bits=8, parity=None, stop=1)  # initialization the UART

micropython.kbd_intr(-1)  # запрет умирания платы в случае, когда датчик возвращает байт, который равен "C"
micropython.alloc_emergency_exception_buf(100)  # for interrupt
uart.read()  # чтение данных из входного буфера микроконтроллера и его очистка

with Interrupt():
    send_bytes(uart, b'\x55\x95\x0D', UDPClientSocket, UDP_IP, serverPort)  # initialization the sensor
    send_bytes(uart, b'\x55\x08\xA0\x01\x00', UDPClientSocket, UDP_IP, serverPort)  # EEPROM unlock
    send_bytes(uart, b'\x55\x0A\xA0', UDPClientSocket, UDP_IP, serverPort)  # check EEPROM unlock state
    send_bytes(uart, b'\x55\x08\xA1\x00\x20', UDPClientSocket, UDP_IP, serverPort)  # изменение регистра
    # конфигурации (принимаем fd=20)
    send_bytes(uart, b'\x55\x08\xA0\x00\x00', UDPClientSocket, UDP_IP, serverPort)  # EEPROM lock
    send_bytes(uart, b'\x55\x0A\xA1', UDPClientSocket, UDP_IP, serverPort)  # check EEPROM conversion rate
    send_bytes(uart, b'\x55\x0A\xA0', UDPClientSocket, UDP_IP, serverPort)  # check EEPROM lock state
UDPClientSocket.sendto(b'End', (UDP_IP, serverPort))  # completing the configuration

buffer = []
while True:
    read_and_send(uart, b'\x55\x0A\xA0', buffer, 50)
