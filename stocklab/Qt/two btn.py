from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.SetUpUI()

    def SetUpUI(self):
        self.setGeometry(400, 200, 400, 400)
        self.text1 = QLabel("", self)
        self.text1.move(20, 50)
        self.text2 = QLabel("", self)
        self.text2.move(200, 50)

        btn1 = QPushButton("click", self)
        btn1.move(20, 20)
        btn2 = QPushButton("clear", self)
        btn2.move(200, 20)
        btn1.clicked.connect(self.btn1clicked)
        btn2.clicked.connect(self.btn2clicked)

    def btn1clicked(self):
        self.text1.setText("아빠 로블록스")

    def btn2clicked(self):
        self.text2.setText("30분만")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywin = MyWindow()
    mywin.show()
    app.exec_()
