#!/usr/bin/python
# -- coding: utf-8 --

# 文件名  :   UartProtocolSet.py
# 时间    :   2022/08/02 10:53:38
# 作者    :   tic
# Email   :   evsv@sohu.com

#导入程序运行必须模块
import json
import struct
import sys
import threading
import UartProtocolSet_ui
import h9uart_class
import serial
import serial.tools.list_ports
# from PySide6.QtCore import *
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog


# 重载串口接收
class uu(h9uart_class.Communication):

    #初始化
    def __init__(self, com, bps, timeout, textedit, protocol):
        self.working = False
        self.protocol = protocol
        self.resultlist = []
        self.port = com
        self.baut = bps
        self.timeout = timeout
        self.N = protocol[-1]['NN']
        self.data = ''
        self.text = textedit
        global Ret
        try:
            # 打开串口，并得到串口对象
            self.main_engine = serial.Serial(self.port,
                                             self.baut,
                                             timeout=self.timeout)
            # 判断是否打开成功
            if (self.main_engine.is_open):
                Ret = True
        except Exception as e:
            print("---异常---：", e)

    def beginT(self):
        t2 = threading.Thread(
            target=self.uartR,
            args=())  # target是要执行的函数名（不是函数），args是函数对应的参数，以元组的形式存在
        t2.start()

    def uartR(self):
        # 循环接收数据，此为死循环，可用线程实现
        # self.main_engine.read_all()
        print("开始接收数据：")
        while self.working:
            try:
                # 一个字节一个字节的接收
                n = self.main_engine.in_waiting
                if n == self.N:

                    data1 = self.main_engine.read(self.N)  #转为十六进制
                    # data2 = int(data1, 16)  #转为十进制
                    # print(data1)
                    self.data = data1.hex()
                    # self.text.setText('kkk')
                    # print('-')
                    self.resultlist.clear()
                    for pr in self.protocol:

                        if pr['show'] == '1':
                            xx = struct.unpack(pr['type'],
                                               data1[pr['NF']:pr['NN']])[0]
                            print(pr['name'] + ':' + str((xx)), end='  ')
                            self.resultlist.append(xx)
                        if pr['show'] == 'x':
                            xx = struct.unpack(pr['type'],
                                               data1[pr['NF']:pr['NN']])[0]
                            print(pr['name'] + ':' + str((xx)), end='  ')
                            self.resultlist.append(hex(xx))
                elif n > self.N:
                    # self.text.setText('xxx')
                    print("  --" + str(self.main_engine.in_waiting))
                    self.main_engine.read_all()

            except Exception as e:
                print("异常报错：", e)


class Window(QMainWindow, UartProtocolSet_ui.Ui_Form):

    def __init__(self, Form):
        super().setupUi(Form)  # 调用父类的setupUI函数
        QMainWindow.__init__(self)  # 才能使用dialoguefileopen
        self.timer = None
        self.timer_running = None
        self.Engine1 = None
        self.protocol = []
        self.baut = 115200
        self.isopen = False
        uartdescription = h9uart_class.Communication.Print_Used_Com()
        self.comboBox.addItems(uartdescription)
        self.te_baut.setText('115200')
        self.textEdit.setText('3')
        self.saveoneline = ''
        # 表
        n = 0
        self.model = QStandardItemModel(n, 4)
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(
            ['变量名', '类型或命令', '单位', '显示(0 1 x s)'])
        # 实例化表格视图，设置模型为自定义的模型
        self.tableView.setModel(self.model)

        # button
        self.pushButton.clicked.connect(
            lambda: self.adddata(int(self.textEdit.toPlainText())))
        self.pushButton_2.clicked.connect(lambda: self.savedata())
        self.pushButton_add.clicked.connect(lambda: self.addraw())
        self.pushButton_del.clicked.connect(lambda: self.delraw())
        self.pushButton_load.clicked.connect(lambda: self.loaddata())

        self.pushButton_load_protocol.clicked.connect(
            lambda: self.loaddata_work())
        self.pushButton_openUart.clicked.connect(lambda: self.openUart())
        self.pushButton_searchUart.clicked.connect(lambda: self.searchUart())
        self.pushButton_ls.clicked.connect(lambda: self.ls())
        self.pushButton_savedatawork.clicked.connect(
            lambda: self.savedata_work())

# set ---------------------------------------------------------------------------
# 添加表格数据

    def adddata(self, n):
        self.model = QStandardItemModel(n, 4)
        # 设置水平方向四个头标签文本内容
        self.model.setHorizontalHeaderLabels(
            ['变量名', '类型或命令', '单位', '显示(0 1 x s)'])
        for row in range(n):
            item = QStandardItem(str('数据') + str(row + 1))
            self.model.setItem(row, 0, item)
            item = QStandardItem(str('<H'))
            self.model.setItem(row, 1, item)
            item = QStandardItem(str('°'))
            self.model.setItem(row, 2, item)
            item = QStandardItem(str('1'))
            self.model.setItem(row, 3, item)
        # 实例化表格视图，设置模型为自定义的模型
        self.tableView.setModel(self.model)

    # 存储表格数据
    def savedata(self):
        myrow = self.tableView.model().rowCount()
        listset = []
        listsethead = []
        NN = 0
        PN = 0
        countR = 0
        countT = 0
        for row in range(myrow):

            lx = self.tableView.model().item(row, 1).text()
            lshow = self.tableView.model().item(row, 3).text()
            NN = 0
            if lshow == '1' or lshow == 'x' or lshow == '0':  # 接收协议 1为10进制 x为16进制 0为不显示
                countR = countR + 1
                if 'c' in lx or 'B' in lx:
                    NN = 1
                elif 'h' in lx or 'H' in lx:
                    NN = 2
                elif 'i' in lx or 'I' in lx:
                    NN = 4
                elif 'q' in lx or 'Q' in lx:
                    NN = 8
                elif 'f' in lx:
                    NN = 4
                elif 'd' in lx:
                    NN = 8
                listset.append({
                    "name":
                    self.tableView.model().item(row, 0).text(),
                    "type":
                    self.tableView.model().item(row, 1).text(),
                    "unit":
                    self.tableView.model().item(row, 2).text(),
                    "show":
                    self.tableView.model().item(row, 3).text(),
                    "NF":
                    PN,
                    "NN":
                    PN + NN,
                })
                PN = PN + NN
            elif lshow == 's':  # 发送协议
                countT = countT + 1
                listset.append({
                    "name":
                    self.tableView.model().item(row, 0).text(),
                    "commd":
                    self.tableView.model().item(row, 1).text(),
                    "show":
                    self.tableView.model().item(row, 3).text()
                })
        print(json.dumps(listset))
        listsethead.append({  # 协议头
            "countR": countR,
            "countT": countT,
            "show": 'start',
            "baut": self.te_baut.toPlainText()
        })
        jj = json.dumps(listsethead + listset)
        fileName, _ = QFileDialog.getSaveFileName(
            self, "存储文件", "./", "json Files (*.json);;All Files (*)")
        if fileName:
            f2 = open(fileName, 'w')
            f2.write(jj)
            f2.close()

    # 删除当前选中的数据
    def delraw(self):
        indexs = self.tableView.selectionModel().selection().indexes()
        print(indexs)
        if len(indexs) > 0:
            index = indexs[0]
            self.model.removeRows(index.row(), 1)

    # 添加数据
    def addraw(self):
        indexs = self.tableView.selectionModel().selection().indexes()
        if len(indexs) > 0:
            self.model.insertRow(indexs[0].row() + 1, QStandardItem(str('数据')))
        elif len(indexs) == 0:
            self.model.appendRow(QStandardItem(str('数据')))

    # 导入数据
    def loaddata(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "选取文件", "./", "json Files (*.json);;All Files (*)")
        if fileName:
            with open(fileName, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)
                n = len(json_data)
                print('这是文件中的json数据：', json_data)
                countR = json_data[0]['countR']
                countT = json_data[0]['countT']
                self.te_baut.setText(str(json_data[0]['baut']))
                self.model = QStandardItemModel(countR + countT, 4)
                self.model.setHorizontalHeaderLabels(
                    ['变量名', '类型或命令', '单位', '显示(0 1 x s)'])
                row = 0
                for pr in json_data:
                    if pr['show'] == '1' or pr['show'] == 'x' or pr[
                            'show'] == '0':  # 10 和16进制 不显示

                        item = QStandardItem(str(pr['name']))
                        self.model.setItem(row, 0, item)
                        item = QStandardItem(str(pr['type']))
                        self.model.setItem(row, 1, item)
                        item = QStandardItem(str(pr['unit']))
                        self.model.setItem(row, 2, item)
                        item = QStandardItem(str(pr['show']))
                        self.model.setItem(row, 3, item)
                        row = row + 1
                    if pr['show'] == 's':  # 发送命令列表
                        item = QStandardItem(str(pr['name']))
                        self.model.setItem(row, 0, item)
                        item = QStandardItem(str(pr['commd']))
                        self.model.setItem(row, 1, item)
                        item = QStandardItem(str(pr['show']))
                        self.model.setItem(row, 3, item)
                        row = row + 1
            # 实例化表格视图，设置模型为自定义的模型
            self.tableView.setModel(self.model)
            # #todo 优化1 表格填满窗口
            # # #水平方向标签拓展剩下的窗口部分，填满表格
            # self.tableView.horizontalHeader().setStretchLastSection(True)
            # # #水平方向，表格大小拓展到适当的尺寸
            # self.tableView.horizontalHeader().setSectionResizeMode(
            #     QHeaderView.Stretch)


# work ---------------------------------------------------------------------------

# 导入协议

    def loaddata_work(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "选取文件", "./", "json Files (*.json);;All Files (*)")
        # fileName = './h9/姿态仪.json'
        # fileName = './h9/h9new.json'
        if fileName:
            with open(fileName, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)
                self.protocol = json_data

                # n = len(json_data)
                self.baut = json_data[0]['baut']
                self.countR = json_data[0]['countR']
                self.countT = json_data[0]['countT']
                # print('这是文件中的json数据：', json_data)

                self.modelwork = QStandardItemModel(self.countR, 3)
                self.modelwork.setHorizontalHeaderLabels(['变量名', '数据', '单位'])

                self.modelwork_send = QStandardItemModel(self.countT, 2)
                self.modelwork_send.setHorizontalHeaderLabels(['名称', '命令'])
                row = 0
                row_send = 0

                for pr in json_data:
                    if pr['show'] == '1' or pr['show'] == 'x':  # 10 和16进制
                        item = QStandardItem(str(pr['name']))
                        self.modelwork.setItem(row, 0, item)
                        item = QStandardItem(str(pr['unit']))
                        self.modelwork.setItem(row, 2, item)

                        row = row + 1
                    if pr['show'] == 's':  # 发送命令列表
                        item_work = QStandardItem(str(pr['name']))
                        self.modelwork_send.setItem(row_send, 0, item_work)
                        item_work = QStandardItem(str(pr['commd']))
                        self.modelwork_send.setItem(row_send, 1, item_work)
                        row_send = row_send + 1
            # 实例化表格视图，设置模型为自定义的模型

            self.tableView_work.setModel(self.modelwork)
            self.tableView_work_send.setModel(self.modelwork_send)
            self.baut = json_data[0]['baut']

    # 打开串口
    def openUart(self):
        ls = self.comboBox.currentText()
        port = ls[ls.find('(COM') + 1:-1]

        if (self.isopen):
            self.isopen = False
            self.Engine1.working = False
            self.Engine1.Close_Engine()
            self.pushButton_openUart.setText('关闭')
            self.timer_running = False
            # self.fun_timer()
        else:
            self.isopen = True
            self.Engine1 = uu(port, self.baut, 0.5, self.textedit_senddata,
                              self.protocol)
            self.Engine1.working = True
            self.pushButton_openUart.setText('打开')
            self.Engine1.beginT()
            self.timer_running = True
            self.fun_timer()

    # 搜索可以串口
    def searchUart(self):
        uartdescription = uu.Print_Used_Com()
        self.comboBox.clear()
        self.comboBox.addItems(uartdescription)

    # 定时刷新数据
    def fun_timer(self):
        if self.timer_running:
            # self.timer.cancel()  # 这步可能不是必须的
            self.timer = threading.Timer(0.2, self.updateData)
            self.timer.start()
        else:
            self.timer.cancel()

    # 定时刷新数据
    def updateData(self):
        row = 0
        for pr in self.Engine1.resultlist:
            item = QStandardItem(str(pr))
            self.modelwork.setItem(row, 1, item)
            row = row + 1
        # 实例化表格视图，设置模型为自定义的模型
        self.tableView_work.setModel(self.modelwork)
        self.fun_timer()

    def ls(self):
        lll = self.modelwork_send.itemData(
            self.modelwork_send.index(
                self.tableView_work_send.currentIndex().row(), 1))
        sss = lll[0]
        for i in range(0, len(sss) - 1, 2):
            ls = sss[i:i + 2]
            result = int(ls, 16)
            hex_num = hex(result)
            print(hex_num)
            buffer = struct.pack(">B", result)
            self.Engine1.Send_data(buffer)
        # buffer = struct.pack(">Q", 0x9966060411222222)
        # print(buffer.hex())

    def savedata_work(self):

        # fileName, _ = QFileDialog.getSaveFileName(
        #     self, "存储文件", "./", "json Files (*.json);;All Files (*)")

        # with open(fileName, 'a') as f:
        #     f.writelines('\n' + str(self.Engine1.resultlist))
        # f.close()
        # with open('ls.txt', "wb") as f:
        self.saveoneline = self.saveoneline + '\n' + str(
            self.Engine1.resultlist)
        self.textedit_saveoneline.setText(self.saveoneline)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Window(MainWindow)  # 注意把类名修改为myDialog
    MainWindow.show()
    sys.exit(app.exec())
