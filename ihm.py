# ihm.py

import numpy as np
import matplotlib.pyplot as plt
import os

import sys
from random import randint

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLCDNumber,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
)

# from layout_colorwidget import Color

# FILE HANDLING

def save_data(data):
    # if not(os.path.exists(os.path.join(os.path.dirname(__file__), "DATA"))):
    file = open(os.path.join(os.path.dirname(__file__), "DATA"), 'w')

    # unparse dicionnary
    unparsed_data = []
    pieces = list(data.keys())
    n = len(data[pieces[0]])

    for i in range(n):
        new_data = []
        for piece in pieces:
            new_data.append(data[piece][i])
        unparsed_data.append(new_data)

    # print
    file.write(str(n))
    file.write("\n")

    for p in pieces:
        file.write(p)
        file.write(" ")
    file.write("\n")
    
    for line in unparsed_data:
        for column in line:
            file.write(str(column))
            file.write(" ")
        file.write("\n")

def open_data(file_name):
    file = open(os.path.join(os.path.dirname(__file__), file_name), 'r')
    n = int(file.readline())
    pieces = file.readline().split(" ")
    resultats = dict.fromkeys(tuple(pieces), [])

    for i in range(n):
        x = file.readline.split(" ")
        for j in len(x):
            resultats[pieces[i]].append(x[j])
    
    return resultats


def tracer(resultats):
    plt.figure(figsize=(12, 6))
    
    couleurs = ['red', 'blue', 'green', 'black']
    labels = list(resultats.keys())

    for idx, (nom_piece, temperatures) in enumerate(resultats.items()):
        plt.plot(temperatures, label=nom_piece, color=couleurs[idx % len(couleurs)])
    
    plt.title("Évolution des températures dans la maison")
    plt.xlabel("Temps (minutes)")
    plt.ylabel("Température (°C)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()





# class AnotherWindow(QWidget):
#     """
#     This "window" is a QWidget. If it has no parent,
#     it will appear as a free-floating window.
#     """

#     def __init__(self):
#         super().__init__()
#         layout = QVBoxLayout()
#         self.label = QLabel("Another Window % d" % randint(0, 100))
#         layout.addWidget(self.label)
#         self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mon Thermostat Intelligent")
        self.setFixedSize(QSize(405, 720))

        pagelayout = QVBoxLayout()
        self.button_layout = QVBoxLayout()
        self.stacklayout = QStackedLayout()


        pagelayout.addLayout(self.stacklayout)
        pagelayout.addLayout(self.button_layout)

        btn = QPushButton("MENU")
        btn.pressed.connect(self.activate_tab_1)
        self.button_layout.addWidget(btn)
        widget = QLabel("20°C")
        widget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.stacklayout.addWidget(widget)

        # btn = QPushButton("PROGRAMME")
        # btn.pressed.connect(self.activate_tab_2)
        # button_layout.addWidget(btn)
        # self.stacklayout.addWidget(QTimeEdit())

        test = TestLayout(self)

        btn = QPushButton("PARAMETRES")
        btn.pressed.connect(self.activate_tab_3)
        self.button_layout.addWidget(btn)
        self.stacklayout.addWidget(QLabel("PARAMETRES"))

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)
    
    def set_home_layout(self):
        pass

    def activate_tab_1(self):
        self.stacklayout.setCurrentIndex(0)

    def activate_tab_2(self):
        self.stacklayout.setCurrentIndex(1)

    def activate_tab_3(self):
        self.stacklayout.setCurrentIndex(2)


class TestLayout(MainWindow):
    def __init__(self, master):
        btn = QPushButton("PROGRAMME")
        btn.pressed.connect(self.activate_tab_2)
        self.master.button_layout.addWidget(btn)
        self.master.stacklayout.addWidget(QTimeEdit())
        



