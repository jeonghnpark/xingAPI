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
        self.tex1.setText("버튼1이 클릭됨")

    def btn2clicked(self):
        self.tex2.setText("버튼2이 클릭됨")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywin = MyWindow()
    mywin.show()
    app.exec_()
