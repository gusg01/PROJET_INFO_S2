# controle.py
import math

class ThermostatCentral:
    def __init__(self, mode='eco'):
        self.mode = mode
        self.consigne_generale = 19.0
        self.vannes = []

    def ajouter_vanne(self, vanne):
        self.vannes.append(vanne)

    def changer_mode(self, mode):
        self.mode = mode

    def controler_chauffage(self):
        return any(vanne.ouverte for vanne in self.vannes)

class VanneThermostatique:
    def __init__(self, piece, consigne=19.0):
        self.piece = piece
        self.consigne = consigne
        self.ouverte = False

    def mesurer_temperature(self):
        return self.piece.temperature

    def ajuster_etat(self, mode):
        temperature = self.mesurer_temperature()
        if mode == 'eco':
            self.ouverte = temperature < self.consigne
        elif mode == 'confort':
            self.ouverte = temperature < (self.consigne + 1.0)

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

class Chauffage:
    def __init__(self):
        self.allume = False

    def allumer(self):
        self.allume = True

    def eteindre(self):
        self.allume = False

    def fournir_chaleur(self, piece):
        if self.allume:
            piece.chauffer(apport=0.5)

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