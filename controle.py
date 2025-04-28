# controle.py

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

