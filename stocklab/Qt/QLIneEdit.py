from PyQt5.QtWidgets import *
import sys
from PyQt5.QtCore import *


class MyWindow(QMainWindow):
    #gui연습
    #LineEdit객체에 텍스트를 쓰면 상태바에 텍스트를 표시함

    def __init__(self):
        super().__init__()
        self.setUpUI()

    def setUpUI(self):
        self.setGeometry(200, 200, 400, 400)  # X,Y, width, height
        label = QLabel("code ", self)
        label.move(20, 20)
        btn1 = QPushButton("닫기", self)
        btn1.move(250, 20)
        btn1.clicked.connect(QCoreApplication.quit)
        self.input_code = QLineEdit("", self)
        self.input_code.move(100, 20)
        self.input_code.textChanged.connect(self.when_code_input)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

    def when_code_input(self):
        self.status_bar.showMessage(self.input_code.text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywin = MyWindow()
    mywin.show()
    app.exec_()
