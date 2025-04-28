from controle import ThermostatCentral, VanneThermostatique, Piece, Chauffage, Maison
import time

# 1. Création de la maison
maison = Maison()
salon = Piece('Salon', volume=50, inertie_thermique=2.0)
chambre = Piece('Chambre', volume=30, inertie_thermique=1.5)
sdb = Piece('Salle de Bain', volume=20, inertie_thermique=1.2)

maison.ajouter_piece(salon)
maison.ajouter_piece(chambre)
maison.ajouter_piece(sdb)

maison.connecter_pieces(salon, chambre)
maison.connecter_pieces(chambre, sdb)

# 2. Création du chauffage
chauffage = Chauffage()

# 3. Création du thermostat et des vannes
thermostat = ThermostatCentral(mode='eco')
v1 = VanneThermostatique(salon, consigne=19)
v2 = VanneThermostatique(chambre, consigne=20)
v3 = VanneThermostatique(sdb, consigne=21)

thermostat.ajouter_vanne(v1)
thermostat.ajouter_vanne(v2)
thermostat.ajouter_vanne(v3)

# 4. Simulation
duree_simulation_minutes = 60 * 24  # 24h
pas_temps_minutes = 1  # 1 minute par itération
temperature_exterieure = 5.0  # Température extérieure constante

for minute in range(0, duree_simulation_minutes, pas_temps_minutes):
    # Contrôle
    thermostat.controler_chauffage()
    for vanne in thermostat.vannes:
        vanne.ajuster_etat(thermostat.mode)
    
    # Chauffage
    for vanne in thermostat.vannes:
        if vanne.ouverte:
            chauffage.fournir_chaleur(vanne.piece)
    
    # Diffusion de chaleur
    maison.diffusion_chaleur()
    
    # Perte de chaleur
    maison.perte_vers_exterieur()

    # Affichage toutes les heures
    if minute % 60 == 0:
        print(f"--- Heure {minute // 60} ---")
        for piece in maison.pieces:
            print(f"{piece.nom}: {piece.temperature:.2f}°C")

# Plus tard : sauvegarder dans un fichier texte