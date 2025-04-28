# main.py

from controle import ThermostatCentral, VanneThermostatique, Chauffage
from simulation import Maison, Piece, initialiser_systeme, lancer_simulation
import ihm  # Pour tracer ensuite

def creer_maison_de_test():
    # Création des pièces
    salon = Piece("Salon", volume=30, inertie_thermique=1.2)
    chambre = Piece("Chambre", volume=20, inertie_thermique=1.0)
    cuisine = Piece("Cuisine", volume=15, inertie_thermique=0.8)

    # Création de la maison
    maison = Maison(temperature_moyenne=5.0, amplitude=5.0)
    maison.ajouter_piece(salon)
    maison.ajouter_piece(chambre)
    maison.ajouter_piece(cuisine)

    # Connexions physiques entre pièces
    maison.connecter_pieces(salon, chambre)
    maison.connecter_pieces(salon, cuisine)

    return maison, salon, chambre, cuisine

if __name__ == "__main__":
    maison, salon, chambre, cuisine = creer_maison_de_test()
    thermostat, chauffage, vannes = initialiser_systeme(maison, [salon, chambre, cuisine])
    
    # Simulation et récupération des températures
    resultats = lancer_simulation(maison, thermostat, chauffage, duree_minutes=720)  # Simulation sur 12h

    # Tracer les résultats
    ihm.tracer(resultats)
