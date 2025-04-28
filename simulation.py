# simulation.py

from controle import ThermostatCentral, Chauffage, VanneThermostatique

def initialiser_systeme(maison):
    thermostat = ThermostatCentral(mode='eco')
    chauffage = Chauffage()

    for piece in maison.pieces:
        vanne = VanneThermostatique(piece=piece, consigne=19.0)
        thermostat.ajouter_vanne(vanne)

    return thermostat, chauffage

def lancer_simulation(maison, thermostat, chauffage, duree_minutes=120):
    historique = {piece.nom: [] for piece in maison.pieces}

    for minute in range(duree_minutes):
        maison.diffusion_chaleur()
        maison.perte_vers_exterieur(minute)

        for vanne in thermostat.vannes:
            vanne.ajuster_etat(thermostat.mode)

        if thermostat.controler_chauffage():
            chauffage.allumer()
        else:
            chauffage.eteindre()

        for vanne in thermostat.vannes:
            if chauffage.allume and vanne.ouverte:
                chauffage.fournir_chaleur(vanne.piece)

        for piece in maison.pieces:
            historique[piece.nom].append(piece.temperature)

    return historique
