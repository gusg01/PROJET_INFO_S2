# simulation.py

from controle import ThermostatCentral, Chauffage, VanneThermostatique

def initialiser_systeme(maison, liste_pieces):
    thermostat = ThermostatCentral(mode='eco')
    chauffage = Chauffage()
    vannes = []

    for piece in liste_pieces:
        vanne = VanneThermostatique(piece=piece, consigne=19.0)
        thermostat.ajouter_vanne(vanne)
        vannes.append(vanne)
    
    return thermostat, chauffage, vannes

def lancer_simulation(maison, thermostat, chauffage, duree_minutes=60):
    resultats = {vanne.piece.nom: [] for vanne in thermostat.vannes}
    resultats["Exterieur"] = []

    for minute in range(duree_minutes):
        # Diffusion interne
        maison.diffusion_chaleur()

        # Perte vers extérieur
        maison.perte_vers_exterieur(minute)

        # Ajustement des vannes
        for vanne in thermostat.vannes:
            temperature = vanne.mesurer_temperature()
            if thermostat.mode == 'eco':
                if temperature < vanne.consigne:
                    vanne.ouverte = True
                else:
                    vanne.ouverte = False

        # Contrôle du chauffage
        besoin_chauffage = any(vanne.ouverte for vanne in thermostat.vannes)
        if besoin_chauffage:
            chauffage.allumer()
        else:
            chauffage.eteindre()

        # Fournir chaleur
        for vanne in thermostat.vannes:
            if chauffage.allume and vanne.ouverte:
                chauffage.fournir_chaleur(vanne.piece)

        # Stocker résultats
        for vanne in thermostat.vannes:
            resultats[vanne.piece.nom].append(vanne.piece.temperature)
        
        # Stocker température extérieure
        resultats["Exterieur"].append(maison.temperature_exterieure(minute))

    return resultats