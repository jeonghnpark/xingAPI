import win32com.client

import pythoncom

import sys
import time
import json

from PyQt5 import QtWidgets

from PyQt5 import QtGui

from PyQt5 import QtCore

from PyQt5 import uic

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

XING_PATH = "C:\\eBest\\xingAPI"


def read_csv(fname):
    data = []
    with open(fname, 'r', encoding="UTF8") as FILE:
        csv_reader = csv.reader(FILE, delimiter=',', quotechar='"')
        for row in csv_reader:
            data.append(row)

        return data


def save_file_to_csv(file_name, data):
    """data : list saving each element as each line of file"""
    with open(file_name, 'w', encoding="cp949") as make_file:
        vals = data[0].keys()
        ss = ''
        for val in vals:
            val = val.replace(',', '')
        ss += '\n'
        make_file.write(ss)

        for dt in data:
            vals = dt.values()
            ss = ''
            for val in vals:
                sval = str(val)
                sval = sval.replace(',', '')
                ss += (sval + ',')

            ss += '\n'
            make_file.write(ss)
        make_file.close()


def save_to_file_json(file_name, data):
    with open(file_name, 'w', encoding='cp949') as make_file:
        json.dump(data, make_file, ensure_ascii=False, indent='\t')
    make_file.close()


def load_json_from_file(file_name, err_msg=1):
    try:
        with open(file_name, 'r', encoding='cp949') as make_file:
            data = json.load(make_file)
        make_file.close()
    except Exception as e:
        data = {}
        if err_msg:
            print(e, file_name)
    return data


TODAY = time.strftime('%Y%m%d')
TODAY_TIME = time.strftime("%H%M%S")
TODAY_S = time.strftime("%Y-%m-%d")

# class Form(QtWidgets.QDialog):
#     def __init__(self, parent=None):
#         QtWidgets.QDialog.__init__(self, parent)
#         self.ui = uic.loadUi('xing_sample_ui.ui', self)
#
#         self.query_list = []
#
#     def clear_message(self):
#         self.ui.listWidget_msg.clear()
#
#     def show_message(self, pr):
#         self.ui.listWidget_msg.addItem(pr)
#         self.ui.listWidget_msg.scrollToBottom()


if __name__ == '__main__':
    # app = QtWidgets.QApplication(sys.argv)
    # WIDGET = Form()
    # WIDGET.show()
    # app.exec_()
    # exit()
    pass
