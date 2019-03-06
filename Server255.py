import socket
# from scipy.signal import find_peaks_cwt

# Set the socket parameters 
# Адрес хоста (сервера): 
# Если не указать хост '' или указать '0.0.0.0', сокет будет прослушивать все хосты;
# 'localhost' — в компьютерных сетях, стандартное, официально зарезервированное доменное имя для частных IP-адресов
# (в диапазоне 127.0.0.1 — 127.255.255.255), подключиться можно будет только с этого же компьютера.
serverIP = '0.0.0.0'
serverPort = 5000  # (от 0 до 65525, порты до 1024 зарезервированы для системы, порты TCP и UDP не пересекаются)
bufferSize = 16  # Размер передаваемого сообщения, байт (1 символ = 1 байт)

# Create a datagram socket
# socket() - функция создания сокета
# первый параметр adress_family обычно AF_INET (сетевой, Internet-домен) или AF_UNIX (для передачи данных используется
# файловая система ввода/вывода Unix)
# второй параметр type обычно SOCK_STREAM (с установлением соединения, для протокола TCP) или SOCK_DGRAM (без
# установления соединеия, для протокола UDP)
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((serverIP, serverPort))  # bind socket to host and port

print("UDP server up and listening")
# Listen for incoming datagrams
# recvfrom - функция чтения UDP сообщений от клиента
while True:
    data, address = UDPServerSocket.recvfrom(bufferSize)
    if data == b'ESP32':
        print(f'Connected by ESP32 with IP Address: {address}')
        break
    elif data == b'Hello_UDP_Server':
        print(f"Message from Client: {data}")
        print(f"Client IP Address: {address}")
        UDPServerSocket.sendto(b'Hello_UDP_Client', address)  # sending a reply to client

answers = []
while True:
    data, address = UDPServerSocket.recvfrom(bufferSize)
    if data == b'End':
        break
    answers.append(data)
print(f'Answers: {answers}')

measurements = []
while True:
    data, address = UDPServerSocket.recvfrom(5)
    temperature = (data[4] << 6 | data[3] >> 2) * 0.015625
    measurements.append(temperature)

#%%
UDPServerSocket.close()
from matplotlib import pyplot as plt
plt.plot(range(len(measurements)), measurements)
plt.show()

#%%
fd = 20  # частота дискретизации, кол-во отсчётов в секунду (в дискретном сигнале представлены частоты от 0.75 до 4 Гц)
# plt.plot(arange(len(measurements))/float(fd), measurements)  # исходный сигнал
# plt.title('Исходный сигнал')
# plt.xlabel('Время, с')
# plt.ylabel('Температура, t°')
# plt.grid(True)
# plt.show()

from numpy import abs as np_abs
from numpy.fft import rfft, rfftfreq

spectrum = rfft(measurements)  # прямое одномерное ДПФ (для действительных сигналов)

plt.plot(rfftfreq(len(measurements), 1./(len(measurements)/fd)), np_abs(spectrum)/len(measurements))
plt.title('Спектр исходного сигнала')
# plt.ylim([0, 0.15])
# plt.xlim([0, 20])
plt.show()


#%%
# if len(measurements) == n:
#     plt.plot(range(len(measurements)), measurements)
#     plt.xlim((n - fd) // fd, n // fd)
#     plt.show()
#     n = n + fd
#     if len(measurements) == 800:
#         break


# measurements = []
# noneData = []
# fd = 20  # частота дискретизации
# n = fd
# while True:
#     bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
#     data = bytesAddressPair[0]
#     if data == b'None':
#         noneData.append(data)
#         print(noneData)
#     else:
#         byte4and3 = int(data, 2) * 0.015625
#         # byte4and3 = float(int(data, 2)) * 0.015625  # преобразование данных в значения температуры
#         measurements.append(byte4and3)
#         if len(measurements) == n:
#             # findPeaks = find_peaks_cwt(measurements, range(1, len(measurements)))
#             # peaks = [measurements[i] for i in findPeaks]
#             fig = plt.figure()
#             plt.plot(range(len(measurements)), measurements)
#             # plt.scatter(findPeaks, peaks, color='red')
#             plt.xlim((n-fd)//fd, n//fd)
#             # plt.xlabel('Время [с]')
#             # plt.ylabel('Температура [°C]')
#             plt.show()
#             n = n + fd
#             if len(measurements) == 800:
#                 fig.savefig('measurements_fd=20_len=800.pdf')
#                 break
#                 # raw_input = input('Would you like to continue?\n Press "y" if yes or "n" if not')
#                 # if raw_input == 'n':
#                 #     break
#
# with open("measurements_fd=20_len=800.txt", 'w') as file:
#     for i in measurements:
#         file.write(str(i) + '\n')
# print('end')
