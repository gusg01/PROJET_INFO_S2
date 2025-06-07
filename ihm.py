# ihm.py

import numpy as np
import matplotlib.pyplot as plt
import os

import sys
from random import randint

import pyqtgraph as pg

from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QStackedLayout,
    QVBoxLayout,
    QGridLayout,
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
    QCalendarWidget
)

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
        x = file.readline().split(" ")
        for j in range(len(x)):
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








# IHM

class MainWindow(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Mon Thermostat Intelligent")
        self.setFixedSize(QSize(405, 720))

        pagelayout = QVBoxLayout()
        self.button_layout = QVBoxLayout()
        self.settings_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.addLayout(self.stacklayout) # MAIN DISPLAY
        pagelayout.addLayout(self.button_layout)
        pagelayout.addLayout(self.settings_layout)

        btn = QPushButton("MENU")
        btn.pressed.connect(self.activate_tab_1)
        self.button_layout.addWidget(btn)
        self.stacklayout.addWidget(MenuWiget())

        btn = QPushButton("SUIVI")
        btn.pressed.connect(self.activate_tab_2)
        self.button_layout.addWidget(btn)
        self.stacklayout.addWidget(SuiviWiget(data).plot_graph)

        btn = QPushButton("PROGRAMME")
        btn.pressed.connect(self.activate_tab_3)
        self.button_layout.addWidget(btn)
        self.stacklayout.addWidget(ProgWiget())

        btn = QPushButton("[PARAMETRES]")
        btn.pressed.connect(self.activate_tab_4)
        self.settings_layout.addWidget(btn)
        self.stacklayout.addWidget(ParamWiget().widget)

        btn = QPushButton("[RELANCER]")
        btn.pressed.connect(self.activate_tab_5)
        self.settings_layout.addWidget(btn)
        self.stacklayout.addWidget(RelanceWiget().widget)

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

    def activate_tab_4(self):
        self.stacklayout.setCurrentIndex(3)

    def activate_tab_5(self):
        self.stacklayout.setCurrentIndex(4)


class MenuWiget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.dial = QDial()
        self.dial.setRange(0, 300)
        self.dial.setSingleStep(1)
        self.dial.setValue(200)
        self.dial.sliderMoved.connect(self.slider_position)
        self.bar = QLabel("20.0°C")
        self.bar.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(self.bar)
        layout.addWidget(self.dial)

        self.setLayout(layout)

    def slider_position(self, p):
        self.bar.setText(f"{str(p/10.0)}°C")
        
class SuiviWiget(QWidget):
    def __init__(self, resultats):
        super().__init__()
        # self.widget = QLabel("test")
        # Temperature vs time plot
        n = len(resultats[list(resultats.keys())[0]])

        self.plot_graph = pg.PlotWidget()
        self.plot_graph.setBackground("w")
        self.plot_graph.setTitle("Temperature vs Time", color="b", size="20pt")
        styles = {"color": "red", "font-size": "18px"}
        self.plot_graph.setLabel("left", "Temperature (°C)", **styles)
        self.plot_graph.setLabel("bottom", "Time (min)", **styles)
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.setXRange(1, n)
        self.plot_graph.setYRange(0, 30)

        # pen = pg.mkPen(color=(255, 0, 0))
        # self.plot_line(
        #     "Temperature Sensor 1", time, temperature_1, pen, "b"
        # )
        #len(resultats[list(resultats.keys())[0]])
        time = [i for i in range(n)] 
        couleurs = ['r', 'b', 'g', 'k']

        for idx, (nom_piece, temperatures) in enumerate(resultats.items()):
            pen = pg.mkPen(color=(255, 0, 0))
            self.plot_line(nom_piece, time, temperatures, pen, couleurs[idx % len(couleurs)])

    def plot_line(self, name, time, temperature, pen, brush):
        self.plot_graph.plot(
            time,
            temperature,
            name=name,
            pen=pen,
            symbol="+",
            symbolSize=5,
            symbolBrush=brush,
        )


class ProgWiget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)
        self.grid = QGridLayout()
        self.grid.addWidget(QPushButton("A"), 0, 0)
        self.grid.addWidget(QPushButton("B"), 0, 1)
        self.grid.addWidget(QPushButton("C"), 1, 0)
        self.grid.addWidget(QPushButton("D"), 1, 1)

        layout.addLayout(self.grid)

        self.setLayout(layout)

class ParamWiget(QWidget):
    def __init__(self):
        super().__init__()
        self.widget = QLabel("parametres")

class RelanceWiget(QWidget):
    def __init__(self):
        super().__init__()
        self.widget = QLabel("relance")
        