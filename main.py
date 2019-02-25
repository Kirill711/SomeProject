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
        send_strings(elapsed_time, UDPClientSocket, UDP_IP, serverPort)


def read_and_send(comport, request, length):
    lst = []
    comport.write(request)
    time.sleep(0.25)
    data = comport.read(5)  # кол-во принимаемых платой байт
    lst.append(data)
    if len(lst) == length:
        for i in range(length):
            send_bytes2(lst[i], UDPClientSocket, UDP_IP, serverPort)
            # if i == length-1:
            #     lst.clear()
            #     text_to_send = 'Package sent'
            #     send_strings(text_to_send, UDPClientSocket, UDP_IP, serverPort)


def send_strings(string, sock, ip, port):
    return sock.sendto(bytes(string, "utf-8"), (ip, port))


def send_bytes(comport, request, sock, ip, port):
    comport.write(request)
    time.sleep(2)
    answer = comport.read()
    sock.sendto(answer, (ip, port))


def send_bytes2(data, sock, ip, port):
    return sock.sendto(data, (ip, port))


# старый вариант функции
# def read_and_send(comport, msg, sock, ip, port):
#     comport.write(msg)
#     time.sleep(0.025)  # ждем, когда придет ответ, с запасом (0.01??? for fd=62)
#     data = comport.read(5)  # кол-во принимаемых платой байт
#     if data:
#         byte3 = str(bin(data[3]))
#         byte3 = byte3[2:-2]  # убираем обозначение "двоичные данные" и биты, неотносящиеся к температуре
#         while len(byte3) < 6:
#             byte3 = "0" + byte3
#         byte4 = str(bin(data[4]))
#         byte4and3 = bytes(byte4 + byte3, 'utf-8')  # данные для передачи на сервер
#         sock.sendto(byte4and3, (ip, port))
#     else:
#         sock.sendto(b'None', (ip, port))


sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)

sta_if.active(True)
ap_if.active(False)
sta_if.connect('ORBI27', 'narrowship322')  # 'ORBI27', 'narrowship322'  'iPhone71', '12345678'
while not sta_if.isconnected():
    time.sleep(1)

UDP_IP = "255.255.255.255"
serverPort = 5000
bufferSize = 16
msgFromClient = "Hello UDP Server"

# Create a UDP socket at client side
UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send to server using created UDP socket
# sendto - передача сообщения UDP
UDPClientSocket.sendto(bytes(msgFromClient, "utf-8"), (UDP_IP, serverPort))

msgFromServer = UDPClientSocket.recvfrom(bufferSize)
msgFromServer = "Message from Server {}".format(msgFromServer[0])

esp.osdebug(None)
uos.dupterm(None, 0)

uart = UART(2, 115200)  # создание объекта UART, "2"- Номер UART-порта микроконтроллера
uart.init(115200, bits=8, parity=None, stop=1)  # инициализация UART

micropython.kbd_intr(-1)  # запрет умирания платы в случае, когда датчик возвращает байт, который равен "C"
micropython.alloc_emergency_exception_buf(100)  # for interrupt
answer1 = uart.read()  # чтение данных из входного буфера микроконтроллера и его очистка
# UDPClientSocket.sendto(answer1, (UDP_IP, serverPort))

send_bytes(uart, b'\x55\x95\x0D', UDPClientSocket, UDP_IP, serverPort)  # initialization the sensor
send_bytes(uart, b'\x55\x08\xA0\x01\x00', UDPClientSocket, UDP_IP, serverPort)  # EEPROM unlock
send_bytes(uart, b'\x55\x0A\xA0', UDPClientSocket, UDP_IP, serverPort)  # check EEPROM unlock state
send_bytes(uart, b'\x55\x08\xA1\x00\x20', UDPClientSocket, UDP_IP, serverPort)  # изменение регистра
# конфигурации (принимаем fd=20)
send_bytes(uart, b'\x55\x08\xA0\x00\x00', UDPClientSocket, UDP_IP, serverPort)  # EEPROM lock
send_bytes(uart, b'\x55\x0A\xA1', UDPClientSocket, UDP_IP, serverPort)  # check EEPROM conversion rate
with Interrupt():
    send_bytes(uart, b'\x55\x0A\xA0', UDPClientSocket, UDP_IP, serverPort)  # check EEPROM lock state


# uart.write(b'\x55\x95\x0D')  # инициализация датчика /цепочки датчиков
# time.sleep(2)  # ждем ответа от датчика, с запасом
# answer2 = uart.read()
# UDPClientSocket.sendto(answer2, (UDP_IP, serverPort))
#
# uart.write(b'\x55\x08\xA0\x01\x00')  # EEPROM unlock
# time.sleep(2)
# answer3 = uart.read()
# # UDPClientSocket.sendto(answer3, (UDP_IP, serverPort))
#
# uart.write(b'\x55\x0A\xA0')  # check EEPROM unlock state
# time.sleep(2)
# answer4 = uart.read()
# UDPClientSocket.sendto(answer4, (UDP_IP, serverPort))
#
# uart.write(b'\x55\x08\xA1\x00\x20')  # изменение регистра конфигурации (принимаем fd=20)
# time.sleep(2)
# answer5 = uart.read()
# # UDPClientSocket.sendto(answer5, (UDP_IP, serverPort))
#
# uart.write(b'\x55\x0A\xA1')  # check EEPROM conversion rate
# time.sleep(2)
# answer6 = uart.read()
# UDPClientSocket.sendto(answer6, (UDP_IP, serverPort))
#
# uart.write(b'\x55\x08\xA0\x00\x00')  # EEPROM lock
# time.sleep(2)
# answer7 = uart.read()
# # UDPClientSocket.sendto(answer7, (UDP_IP, serverPort))
#
# uart.write(b'\x55\x0A\xA0')  # check EEPROM lock state
# time.sleep(2)
# answer8 = uart.read()
# UDPClientSocket.sendto(answer8, (UDP_IP, serverPort))


# while True:
#     read_and_send(uart, b'\x55\x0A\xA0', UDPClientSocket, UDP_IP, serverPort)


while True:
    read_and_send(uart, b'\x55\x0A\xA0', 5)
