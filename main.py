from controle import ThermostatCentral, VanneThermostatique
from simulation import Maison, Piece, initialiser_systeme, lancer_simulation
import ihm  # Pour tracer ensuite
import numpy as np
import time
import sys


def creer_maison_de_test():
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

if __name__ == "__main__":
    maison, salon, chambre, cuisine = creer_maison_de_test()
    maison.fin_de_modelisation()
    thermostat, vannes = initialiser_systeme([salon, chambre, cuisine], consigne = 20)
    
    # Simulation et récupération des températures
    resultats = lancer_simulation(maison, thermostat, duree_minutes=10080)  # Simulation sur 7j
    # resultats = lancer_simulation(maison, thermostat, duree_minutes=525600*2)  # Simulation sur 1 année

    # Tracer les résultats
    ihm.save_data(resultats)
    # ihm.tracer(resultats)

    app = ihm.QApplication(sys.argv)
    w = ihm.MainWindow()
    w.show()
    app.exec()