# main.py

from controle import Maison, Piece
from simulation import initialiser_systeme, lancer_simulation
from ihm import tracer_historique

def creer_maison():
    salon = Piece("Salon", volume=30, inertie_thermique=1.2)
    chambre = Piece("Chambre", volume=20, inertie_thermique=1.0)
    cuisine = Piece("Cuisine", volume=15, inertie_thermique=0.8)

    maison = Maison(temperature_exterieure=5.0)
    maison.ajouter_piece(salon)
    maison.ajouter_piece(chambre)
    maison.ajouter_piece(cuisine)

    maison.connecter_pieces(salon, chambre)
    maison.connecter_pieces(salon, cuisine)

    return maison

def main():
    maison = creer_maison()
    thermostat, chauffage = initialiser_systeme(maison)
    historique = lancer_simulation(maison, thermostat, chauffage, duree_minutes=120)
    tracer_historique(historique)

if __name__ == "__main__":
    main()
