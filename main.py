# main.py

from controle import ThermostatCentral, VanneThermostatique, Chauffage
from simulation import Maison, Piece, initialiser_systeme, lancer_simulation
import ihm  # Pour tracer ensuite

def creer_maison_de_test():
    # Création des pièces
    salon = Piece("Salon", volume=30)
    chambre = Piece("Chambre", volume=20)
    cuisine = Piece("Cuisine", volume=15)

    # Création de la maison
    maison = Maison(temperature_moyenne=15.0, amplitude=5.0)
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
    resultats = lancer_simulation(maison, thermostat, chauffage, duree_minutes=5760)  # Simulation sur 4j

    # Tracer les résultats
    ihm.tracer(resultats)
