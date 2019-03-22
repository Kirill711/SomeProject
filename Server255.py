import socket
from datetime import datetime


# Set the socket parameters 
# Адрес хоста (сервера): 
# Если не указать хост '' или указать '0.0.0.0', сокет будет прослушивать все хосты;
# 'localhost' — в компьютерных сетях, стандартное, официально зарезервированное доменное имя для частных IP-адресов
# (в диапазоне 127.0.0.1 — 127.255.255.255), подключиться можно будет только с этого же компьютера.
serverIP = '0.0.0.0'
serverPort = 5000  # (от 0 до 65525, порты до 1024 зарезервированы для системы, порты TCP и UDP не пересекаются)

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
data = None
while data != b'ESP32':
    data, address = UDPServerSocket.recvfrom(16)  # '16' - размер передаваемого сообщения, байт (1 символ = 1 байт)
    if data == b'Hello_UDP_Server':
        print(f"Message from Client: {data}")
        print(f"Client IP Address: {address}")
        UDPServerSocket.sendto(b'Hello_UDP_Client', address)  # sending a reply to client
    # elif data == b'ESP32':
    #     print(f'Connected by ESP32 with IP Address: {address}')
    #     break
print('Connected to the ESP32')

answers = []
while data != b'End':
    data, address = UDPServerSocket.recvfrom(10)
    # if data == b'End':
    #     break
    answers.append(data)
print(f'Answers: {answers}')

measurements = []
time = []
while True:
    data, address = UDPServerSocket.recvfrom(5)
    # temperature = (data[4] << 6 | data[3] >> 2) * 0.015625
    measurements.append(data)
    time.append(datetime.now().time())

#%%
UDPServerSocket.close()
#%%
import matplotlib.pyplot as plt
import numpy as np
from numpy import arange, abs as np_abs
from numpy.fft import rfft, rfftfreq
fd = 20  # sampling frequency

#%% Open data from another file
measurements = []
with open("measurements_fd=20_len=697.txt") as file:
    for i in file:
        measurements.append(float(i))

#%% Draw measurements
plt.plot(arange(len(measurements))/float(fd), measurements)
plt.title('Pulse wave')
plt.xlabel('time, sec')
plt.ylabel('temperature, t°')
plt.grid()
plt.show()

#%% Draw measurements with peaks with use continuous wavelet transform
from scipy.signal import find_peaks_cwt
findPeaks = find_peaks_cwt(np.array(measurements), range(1, len(measurements)), min_length=1)
peaks = [measurements[i] for i in findPeaks]
plt.plot(range(len(measurements)), measurements)
plt.scatter(findPeaks, peaks, color='red')

#%% Draw measurements with peaks
from scipy.signal import find_peaks

x = np.array(measurements)
peaks1, _ = find_peaks(x, distance=20)
peaks2, _ = find_peaks(x, prominence=0.01)
peaks3, _ = find_peaks(x, width=10)
peaks4, _ = find_peaks(x, threshold=0.01)
plt.subplot(2, 2, 1)
plt.plot(peaks1, x[peaks1], "xr"); plt.plot(x); plt.legend(['distance'])
plt.subplot(2, 2, 2)
plt.plot(peaks2, x[peaks2], "ob"); plt.plot(x); plt.legend(['prominence'])
plt.subplot(2, 2, 3)
plt.plot(peaks3, x[peaks3], "vg"); plt.plot(x); plt.legend(['width'])
plt.subplot(2, 2, 4)
plt.plot(peaks4, x[peaks4], "xk"); plt.plot(x); plt.legend(['threshold'])
plt.show()

#%% Draw spectrum
spectrum = rfft(measurements)  # прямое одномерное ДПФ (для действительных сигналов)

plt.plot(60*rfftfreq(len(measurements), 1./(len(measurements)/fd)), np_abs(spectrum)/len(measurements))
plt.title('Pulse wave spectrum')
plt.ylim([0, 0.005])
# plt.xlim([0, 200])
plt.grid()
plt.show()

#%% Draw spectrum with peaks
spectrum = rfft(measurements)  # прямое одномерное ДПФ (для действительных сигналов)
freq = rfftfreq(len(measurements), 1./(len(measurements)/fd))
ampl = np_abs(spectrum)/len(measurements)

peaks5, _ = find_peaks(ampl, height=0.001)
plt.figure()
plt.plot(peaks5/fd, ampl[peaks5], "xr")
plt.plot(freq, ampl)
plt.xlabel('frequency, Hz')
plt.ylabel('magnitude')
plt.ylim([0, 0.05])
plt.xlim([0, 10])
plt.grid()
plt.show()

#%% Calculate heart rate
val, i = max((val, i) for i, val in enumerate(ampl[peaks5]))
HR = 60*peaks5[i]/fd
plt.plot(peaks5[i]/fd, ampl[peaks5][i], "xg")
plt.title(f'Pulse wave spectrum\nHR = {HR} bps')
# plt.text(8.5, .0044, f'HR: {HR}', fontsize=20)

#%% Save measurements
with open(f"measurements_fd={fd}_len={len(measurements)}.txt", 'w') as file:
    for i in measurements:
        file.write(str(i) + '\n')
print('end')

#%% Save data time
with open(f"data_time_len={len(time)}.txt", 'w') as file:
    for i in time:
        file.write(str(i) + '\n')
print('end')

#%% Draw plot with animation
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.animation import FuncAnimation
j = 0

#%%
style.use('seaborn')

fig, ax = plt.subplots()


def animate(i):
    ax.clear()
    ax.set_xlim(j, 10+j)
    ax.plot(arange(len(measurements))/float(fd), measurements)


anim = FuncAnimation(fig, animate, interval=2000)
plt.show()

#%%
average = sum(measurements)/len(measurements)
measurementsMinusAvg = []
for i in measurements:
    measurementsMinusAvg.append(i - average)
measurementsMinusAvgFFT = rfft(measurementsMinusAvg)

plt.plot(rfftfreq(len(measurementsMinusAvgFFT), 1./(len(measurements)/fd)), measurementsMinusAvgFFT)

#%%
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
#                 fig.savefig(f'measurements_fd={fd}_len={len(measurements)}.pdf')
#                 break
#                 # raw_input = input('Would you like to continue?\n Press "y" if yes or "n" if not')
#                 # if raw_input == 'n':
#                 #     break
