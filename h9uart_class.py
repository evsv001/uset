#!/usr/bin/python
# -- coding: utf-8 --

# 文件名  :   uart_class.py
# 时间    :   2022/06/28 09:46:11
# 作者    :   tic
# Email   :   evsv@sohu.com

import threading
import serial
import serial.tools.list_ports
import struct


class Communication():

    #初始化
    def __init__(self, com, bps, timeout, textedit):
        self.port = com
        self.bps = bps
        self.timeout = timeout
        self.N = 47
        self.data = ''
        self.text = textedit
        global Ret
        try:
            # 打开串口，并得到串口对象
            self.main_engine = serial.Serial(self.port,
                                             self.bps,
                                             timeout=self.timeout)
            # 判断是否打开成功
            if (self.main_engine.is_open):
                Ret = True
        except Exception as e:
            print("---异常---：", e)

    # 打印设备基本信息
    def Print_Name(self):
        print(self.main_engine.name)  #设备名字
        print(self.main_engine.port)  #读或者写端口
        print(self.main_engine.baudrate)  #波特率
        print(self.main_engine.bytesize)  #字节大小
        print(self.main_engine.parity)  #校验位
        print(self.main_engine.stopbits)  #停止位
        print(self.main_engine.timeout)  #读超时设置
        print(self.main_engine.writeTimeout)  #写超时
        print(self.main_engine.xonxoff)  #软件流控
        print(self.main_engine.rtscts)  #软件流控
        print(self.main_engine.dsrdtr)  #硬件流控
        print(self.main_engine.interCharTimeout)  #字符间隔超时

    #打开串口
    def Open_Engine(self):
        self.main_engine.open()

    #关闭串口
    def Close_Engine(self):
        self.main_engine.close()
        print(self.main_engine.is_open)  # 检验串口是否打开

    # 打印可用串口列表
    @staticmethod
    def Print_Used_Com():
        port_list = list(serial.tools.list_ports.comports())
        description = []
        for edis in port_list:
            description.append(edis.description)
        # print(description)
        return description

    #接收指定大小的数据
    #从串口读size个字节。如果指定超时，则可能在超时后返回较少的字节；如果没有指定超时，则会一直等到收完指定的字节数。
    def Read_Size(self, size):
        return self.main_engine.read(size=size)

    #接收一行数据
    # 使用readline()时应该注意：打开串口时应该指定超时，否则如果串口没有收到新行，则会一直等待。
    # 如果没有超时，readline会报异常。
    def Read_Line(self):
        return self.main_engine.readline()

    #发数据
    def Send_data(self, data):
        self.main_engine.write(data)

    #小端
    def LE(self, bytesData, n):
        return round(struct.unpack("<f", bytesData)[0], n)

    #更多示例
    # self.main_engine.write(chr(0x06).encode("utf-8"))  # 十六制发送一个数据
    # print(self.main_engine.read().hex())  #  # 十六进制的读取读一个字节
    # print(self.main_engine.read())#读一个字节
    # print(self.main_engine.read(10).decode("gbk"))#读十个字节
    # print(self.main_engine.readline().decode("gbk"))#读一行
    # print(self.main_engine.readlines())#读取多行，返回列表，必须匹配超时（timeout)使用
    # print(self.main_engine.in_waiting)#获取输入缓冲区的剩余字节数
    # print(self.main_engine.out_waiting)#获取输出缓冲区的字节数
    # print(self.main_engine.readall())#读取全部字符。

    #接收数据
    #一个整型数据占两个字节
    #一个字符占一个字节

    def beginT(self):
        t2 = threading.Thread(
            target=self.uartR,
            args=())  # target是要执行的函数名（不是函数），args是函数对应的参数，以元组的形式存在
        t2.start()

    def uartR(self):
        # 循环接收数据，此为死循环，可用线程实现
        self.main_engine.read_all()
        print("开始接收数据：")
        while True:
            try:
                # 一个字节一个字节的接收
                n = self.main_engine.in_waiting
                if n == self.N:

                    data1 = self.main_engine.read(self.N).hex()  #转为十六进制
                    # data2 = int(data1, 16)  #转为十进制
                    print(data1)
                    self.text.setText('kkk')
                    # print('-')

                elif n > self.N:
                    # self.text.setText('xxx')
                    print("  --" + str(self.main_engine.in_waiting))
                    self.main_engine.read_all()

            except Exception as e:
                print("异常报错：", e)


# -----------------------------------------------------------------b
# # 设置
# Communication.Print_Used_Com()
# Ret = True  #是否创建成功标志
# Engine1 = Communication("com8", 115200, 0.5)
# Engine1.Print_Name()

# # 发送设置纬度

# buffer = struct.pack("<BBBBBBBB", 0x99, 0x66, 0x06, 0x04, 0x11, 0x22, 0x22,
#                      0x22)
# print(buffer.hex())
# Engine1.Send_data(buffer)

# # 接收循环
# if (Ret):
#     # Engine1.Recive_data(0)
#     Engine1.beginT()