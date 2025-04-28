# simulation.py

import math
from controle import ThermostatCentral, Chauffage, VanneThermostatique

class Piece:
    def __init__(self, nom, volume, inertie_thermique=1.0):
        self.nom = nom
        self.volume = volume
        self.inertie_thermique = inertie_thermique
        self.temperature = 18.0
        self.perte_temperature = 0.05  # °C/minute sans chauffage

    def perdre_chaleur(self, perte_exterieure):
        self.temperature -= perte_exterieure / self.inertie_thermique

    def chauffer(self, apport):
        self.temperature += apport / (self.volume * self.inertie_thermique)

class Maison:
    """
    Classe représentant la maison dans son ensemble.
    """
    def __init__(self, temperature_moyenne=5.0, amplitude=5.0):
        self.pieces = []
        self.connexions = {}
        self.perte_exterieure = 0.008  # °C/min
        self.temperature_moyenne = temperature_moyenne
        self.amplitude = amplitude

    def ajouter_piece(self, piece):
        self.pieces.append(piece)
        self.connexions[piece] = []

    def connecter_pieces(self, piece1, piece2):
        if piece1 in self.connexions:
            self.connexions[piece1].append(piece2)
        if piece2 in self.connexions:
            self.connexions[piece2].append(piece1)

    def temperature_exterieure(self, minute):
        """
        Calcule la température extérieure en fonction de l'heure (minute du jour).
        """
        periode = 1440  # 24h = 1440 minutes
        decalage = 240  # Décalage pour que le minimum soit vers 4h du matin
        angle = 2 * math.pi * (minute - decalage) / periode
        return self.temperature_moyenne + self.amplitude * math.cos(angle)

    def diffusion_chaleur(self):
        variations = {}
        for piece, voisines in self.connexions.items():
            for voisine in voisines:
                delta = (voisine.temperature - piece.temperature) * 0.01
                variations[piece] = variations.get(piece, 0) + delta
                variations[voisine] = variations.get(voisine, 0) - delta

        for piece, variation in variations.items():
            piece.temperature += variation

    def perte_vers_exterieur(self, minute):
        for piece in self.pieces:
            T_ext = self.temperature_exterieure(minute)
            perte = self.perte_exterieure * (piece.temperature - T_ext) / piece.inertie_thermique
            piece.temperature -= perte

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