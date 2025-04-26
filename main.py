# main.py

from controle import Maison, Piece, ThermostatCentral, VanneThermostatique, Chauffage

def creer_maison_de_test():
    # Création des pièces
    salon = Piece("Salon", volume=30, inertie_thermique=1.2)
    chambre = Piece("Chambre", volume=20, inertie_thermique=1.0)
    cuisine = Piece("Cuisine", volume=15, inertie_thermique=0.8)

    # Création de la maison
    maison = Maison()
    maison.ajouter_piece(salon)
    maison.ajouter_piece(chambre)
    maison.ajouter_piece(cuisine)

    # Connexions physiques entre pièces
    maison.connecter_pieces(salon, chambre)
    maison.connecter_pieces(salon, cuisine)

    return maison, salon, chambre, cuisine

def initialiser_systeme(maison, pieces):
    # Création du thermostat central
    thermostat = ThermostatCentral(mode='eco')

    # Création du chauffage
    chauffage = Chauffage()

    # Création des vannes pour chaque pièce
    vannes = []
    for piece in pieces:
        vanne = VanneThermostatique(piece=piece, consigne=19.0)
        thermostat.ajouter_vanne(vanne)
        vannes.append(vanne)

    return thermostat, chauffage, vannes

def simulation(maison, thermostat, chauffage, duree_minutes=60):
    for minute in range(duree_minutes):
        print(f"--- Minute {minute} ---")

        # Diffusion interne entre pièces
        maison.diffusion_chaleur()

        # Perte vers extérieur
        maison.perte_vers_exterieur()

        # Mesure et ajustement par les vannes
        for vanne in thermostat.vannes:
            temperature = vanne.mesurer_temperature()
            if thermostat.mode == 'eco':
                # En mode éco, les vannes ferment seules sans allumer le chauffage
                if temperature < vanne.consigne:
                    vanne.ouverte = True
                else:
                    vanne.ouverte = False

        # Contrôle global du chauffage
        besoin_chauffage = any(vanne.ouverte for vanne in thermostat.vannes)
        if besoin_chauffage:
            chauffage.allumer()
        else:
            chauffage.eteindre()

        # Fournir chaleur si chauffage allumé
        for vanne in thermostat.vannes:
            if chauffage.allume and vanne.ouverte:
                chauffage.fournir_chaleur(vanne.piece)

        # Affichage des températures
        for vanne in thermostat.vannes:
            print(f"{vanne.piece.nom}: {vanne.piece.temperature:.2f}°C")

def main():
    maison, salon, chambre, cuisine = creer_maison_de_test()
    thermostat, chauffage, vannes = initialiser_systeme(maison, [salon, chambre, cuisine])
    simulation(maison, thermostat, chauffage, duree_minutes=30)

if __name__ == "__main__":
    main()