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

from simulation import Maison, Piece, initialiser_systeme, lancer_simulation

# FILE HANDLING

def save_data(data):
    """
    Enregistre dans un fichier DATA - qui est cree s'il n'existe pas - les donnees sous la forme d'un dictionnaire founrit en argument
    """
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
    """
    Renvoie le dictionnaire de donnees reconstitue a partir d'un fichier texte dont le nom est donne en entree
    """
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
    """
    Trace les resultats de la simulation dans une fenetre matplotlib
    """
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
    """
    Application
    Cette classe definit et lance l'application de controle du thermostat
    Elle definit et lance egalement la simulation.
    Les fonctions sont :
    - MENU : retour vers le menu principal
    - SUIVI : affichage du suivi de la temperature, ici les resultats de la simulation
    - PROGRAMME : permet de rentrer un planning de chauffe
    Les boutons [PARAMETRES] et [RELANCE] sont specifiques a la simulation
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mon Thermostat Intelligent")
        self.setFixedSize(QSize(405, 720))

        # SIM

        self.maison, salon, chambre, cuisine = self.creer_maison_de_test()
        self.maison.fin_de_modelisation()
        self.duree_minutes = 10080
        self.consigne = 20.0
        self.mode = 'eco'
        # self.heure_consigne = np.zeros((7, 48, 3), dtype=int)
        self.thermostat, vannes = initialiser_systeme([salon, chambre, cuisine], consigne=20)
        self.data = lancer_simulation(self.maison, self.thermostat, self.duree_minutes)  # Simulation sur 7j
        self.timer = self.maison.minute

        # DISPLAY

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
        self.menu = MenuWiget()
        self.stacklayout.addWidget(self.menu)

        btn = QPushButton("SUIVI")
        btn.pressed.connect(self.activate_tab_2)
        self.button_layout.addWidget(btn)
        self.test = SuiviWiget(self.data, self.timer).plot_graph
        self.stacklayout.addWidget(self.test)

        btn = QPushButton("PROGRAMME")
        btn.pressed.connect(self.activate_tab_3)
        self.button_layout.addWidget(btn)
        self.prog = ProgWiget(self)
        self.stacklayout.addWidget(self.prog)

        btn = QPushButton("[PARAMETRES]")
        btn.pressed.connect(self.activate_tab_4)
        self.settings_layout.addWidget(btn)
        self.param = ParamWiget()
        self.stacklayout.addWidget(self.param)

        btn = QPushButton("[RELANCER]")
        btn.pressed.connect(self.reload)
        self.settings_layout.addWidget(btn)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def activate_tab_1(self):
        self.stacklayout.setCurrentWidget(self.menu)

    def activate_tab_2(self):
        self.stacklayout.setCurrentWidget(self.test)

    def activate_tab_3(self):
        self.stacklayout.setCurrentWidget(self.prog)

    def activate_tab_4(self):
        self.stacklayout.setCurrentWidget(self.param) 

    def reload(self):
        """
        Lance une nouvelle semaine de simulation avec les parametre actuelisés
        """
        self.stacklayout.setCurrentWidget(self.menu)
        self.stacklayout.removeWidget(self.test)
        self.consigne = self.menu.consigne2
        self.thermostat.set_consigne_generale(self.consigne)
        self.mode = self.menu.check.currentText()
        self.thermostat.set_mode_general(self.mode)
        self.data = lancer_simulation(self.maison, self.thermostat, self.duree_minutes)
        self.timer = self.maison.minute
        self.test = SuiviWiget(self.data, self.timer).plot_graph
        self.stacklayout.addWidget(self.test)

    def ajouter_heure_consigne(self):
        j = self.prog.jour.currentText()
        h1 = 2*self.prog.h1.time().hour() + self.prog.h1.time().minute()//30 
        h2 = 2*self.prog.h2.time().hour() + self.prog.h2.time().minute()//30
        self.thermostat.changer_heure_consigne(j, h1, h2, 1);

    def supprimer_heure_consigne(self):
        j = self.prog.jour.currentText()
        h1 = 2*self.prog.h1.time().hour() + self.prog.h1.time().minute()//30 
        h2 = 2*self.prog.h2.time().hour() + self.prog.h2.time().minute()//30
        self.thermostat.changer_heure_consigne(j, h1, h2, 0);

    def creer_maison_de_test(self):
        # Création des pièces
        salon = Piece("Salon", volume=50)
        chambre = Piece("Chambre", volume=30)
        cuisine = Piece("Cuisine", volume=15)

        # Création de la maison (entitée coordinatrice)
        maison = Maison(temperature_moyenne=10, amplitude_annuelle=8.0, amplitude=4.0)
        maison.ajouter_piece(salon)
        maison.ajouter_piece(chambre)
        maison.ajouter_piece(cuisine)

        # Connexions physiques entre pièces (espace de simulation)
        maison.connecter_pieces(salon, chambre)
        maison.connecter_pieces(salon, cuisine)

        return maison, salon, chambre, cuisine    


class MenuWiget(QWidget):
    """
    Menu principal :
    Il affiche la temperature de consigne et le mode de chauffage
    Un DIAL permet de changer cette temperature de consigne generale et une checkbox permet de selectionner le mode entre ECO et CONFORT
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.dial = QDial()
        self.dial.setRange(0, 300)
        self.dial.setSingleStep(1)
        self.dial.setValue(200)
        self.dial.sliderMoved.connect(self.slider_position)
        self.bar = QLabel("20.0°C")
        self.consigne2 = 20.0
        font = self.bar.font()
        font.setPointSize(42)
        self.bar.setFont(font)
        self.bar.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.mode = QHBoxLayout()
        self.label = QLabel("Mode :")
        self.check = QComboBox()
        self.check.addItems(["eco","confort"])
        self.mode.addWidget(self.label)
        self.mode.addWidget(self.check)
        layout.addWidget(self.bar)
        layout.addWidget(self.dial)
        layout.addLayout(self.mode)

        self.setLayout(layout)

    def slider_position(self, p):
        self.bar.setText(f"{str(p/10.0)}°C")
        self.consigne2 = p/10.0
        
class SuiviWiget(QWidget):
    """
    Affiche l'evolution de la temperature en fonction du temps
    C'est a dire les resultats de la simulation, par defaut sur une semaine
    """
    def __init__(self, resultats, timer):
        super().__init__()
        # self.widget = QLabel("test")
        # Temperature vs time plot
        n = len(resultats[list(resultats.keys())[0]])

        self.plot_graph = pg.PlotWidget()
        self.plot_graph.setBackground("w")
        self.plot_graph.setTitle("Temperature sur une semaine", color="k", size="15pt")
        styles = {"color": "black", "font-size": "15px"}
        self.plot_graph.setLabel("left", "Temperature (°C)", **styles)
        self.plot_graph.setLabel("bottom", f"Temps (min) | {timer//1440} jours passés" , **styles)
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.setXRange(1, n)
        self.plot_graph.setYRange(0, 30)

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
    """
    Permet de modifier les creneaux de chauffe
    """
    def __init__(self, master):
        super().__init__(master)
        layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)
        self.grid = QGridLayout()
        self.grid.addWidget(QLabel("Jour:"), 0, 0)
        self.jour = QComboBox()
        self.jour.addItems(["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche", "Tous_les_jours"])
        self.grid.addWidget(self.jour,              0, 1)
        self.grid.addWidget(QLabel("Heure debut:"), 1, 0)
        self.h1 = QTimeEdit()
        self.grid.addWidget(self.h1,                1, 1)
        self.grid.addWidget(QLabel("Heure fin:"),   2, 0)
        self.h2 = QTimeEdit()
        self.grid.addWidget(self.h2,                2, 1)
        self.add = QPushButton("Ajouter")
        self.add.pressed.connect(master.ajouter_heure_consigne)
        self.grid.addWidget(self.add, 3, 0)
        self.supp = QPushButton("Supprimer")
        self.supp.pressed.connect(master.supprimer_heure_consigne)
        self.grid.addWidget(self.supp, 3, 1)

        layout.addLayout(self.grid)

        self.setLayout(layout)

class ParamWiget(QWidget):
    """
    Affiche les parametres physiques de la simulation
    """
    def __init__(self):
        super().__init__()
        layout =  QVBoxLayout()
        label = QLabel("PARAMETRES PHYSIQUES DE LA SIMULATION :")
        label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        layout.addWidget(label)
        grid = QGridLayout()
        grid.addWidget(QLabel("Temperature moyenne :"), 1, 0)
        grid.addWidget(QLabel("10.0°C"),                1, 1)
        grid.addWidget(QLabel("Amplitude annuelle :"),  2, 0)
        grid.addWidget(QLabel("8.0°C"),                 2, 1)
        grid.addWidget(QLabel("Pieces :"),              3, 0)
        grid.addWidget(QLabel("Volumes :"),             3, 1)
        grid.addWidget(QLabel("Salon"),                 4, 0)
        grid.addWidget(QLabel("Chambre"),               5, 0)
        grid.addWidget(QLabel("Cuisine"),               6, 0)
        grid.addWidget(QLabel("50m3"),                  4, 1)
        grid.addWidget(QLabel("30m3"),                  5, 1)
        grid.addWidget(QLabel("15m3"),                  6, 1)
        grid.setContentsMargins(20,20,20,20)
        grid.setSpacing(69)
        layout.addLayout(grid)

        self.setLayout(layout)

        