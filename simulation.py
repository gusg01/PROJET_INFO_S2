# simulation.py

import math
from controle import ThermostatCentral, Chauffage, VanneThermostatique


class Piece:
    # on considères les pièces comme des ensembles suffisemment petits pour avoir des temps de convection thermique faibles vis-à-vis du temps de chauffage de la pièce
    # donc on néglige ces temps.
    def __init__(self, nom, volume, temperature_init = 20):
        self.nom = nom
        self.volume = volume
        self.nb_ext = 4
        self.surface_mur = math.sqrt(volume/2) * 2 #pièces carrées de 2m de hauteur
    # énergie nécessaire pour augmenter la pièce de 1°; capacité thermique massique = 1010 et masse volumique = 1.20 + 10% de la capacité thermique du mur --> reproduction de la réalité européenne de pertes d'une maison
        self.inertie = 1010 * self.volume * 1.20 + self.nb_ext * 20000 * self.surface_mur + (4-self.nb_ext) * 2550 * self.surface_mur
        self.temperature = temperature_init
        self.chaleur = (273.15 + self.temperature) * self.inertie # chaleur contenue dans la pièce

    def ajout_voisin(self):
        self.nb_ext -= 1
        self.inertie = 1010 * self.volume * 1.20 + self.nb_ext * 20000 * self.surface_mur + (4-self.nb_ext) * 2550 * self.surface_mur
        self.chaleur = self.chaleur = (273.15 + self.temperature) * self.inertie
 
    def pertes_chaleur(self, pertes):
        self.chaleur -= pertes # les pertes sont algébriques

    def chauffer(self, apport):
        apport = abs(apport)
        self.temperature += apport
    
    def maj_temperature(self):
        self.temperature = (self.chaleur/ self.inertie) - 273.15

class Maison:
    """
    Classe représentant la maison dans son ensemble.
    """
    def __init__(self, temperature_moyenne=5.0, amplitude=5.0):
        self.pieces = []
        self.connexions = {}
        self.Rint = 0.16 #(mur de placo de 2* 2cm d'épaisseur)
        self.Rext = 4.17 #(mur de 15 cm de laine de verre et 20 cm de parpaing)
        # Pour temperature exterieur :
        self.temperature_moyenne = temperature_moyenne
        self.amplitude = amplitude

    def ajouter_piece(self, piece):
        self.pieces.append(piece)
        self.connexions[piece] = []

    def connecter_pieces(self, piece1, piece2):
        if piece1 in self.connexions: #raise error ?? / try ??
            self.connexions[piece1].append(piece2)
        if piece2 in self.connexions:
            self.connexions[piece2].append(piece1)
        piece1.ajout_voisin()
        piece2.ajout_voisin()

    def temperature_exterieure(self, minute):
        """
        Calcule la température extérieure en fonction de l'heure (minute du jour).
        """
        periode = 1440  # 24h = 1440 minutes
        decalage = 960  # Décalage pour que le minimum soit vers 4h du matin
        angle = 2 * math.pi * (minute - decalage) / periode
        return self.temperature_moyenne + self.amplitude * math.cos(angle)

    def echange_chaleur(self, minute):
        # prise en compte des echanges de chaleur entre les pièces
        for piece in self.connexions.keys():
            for voisine in self.connexions[piece]:
                echange = (piece.temperature - voisine.temperature)/(self.Rint/piece.surface_mur) #énergie échange en 1 sec par le mur
                piece.pertes_chaleur(echange * 60) # pas de temps de 1 min donc 60 sec
            n = 4 - len(self.connexions[piece])
            echange = (piece.temperature - self.temperature_exterieure(minute)) / (self.Rext/piece.surface_mur)
            piece.pertes_chaleur(echange * 60)

    def maj_temperature(self):
        for piece in self.connexions.keys():
            piece.maj_temperature()


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
        maison.echange_chaleur(minute)
        maison.maj_temperature()


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