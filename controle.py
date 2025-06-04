# controle.py
import numpy as np
import math

class ThermostatCentral:
    def __init__(self, mode='eco', heure_consigne = [], debut = 7, fin = 18, consigne=18.0):
        self.consigne_generale = consigne
        self.heure_consigne = heure_consigne
        self.heure_debut = debut
        self.heure_fin = fin
        self.vannes = []

    def ajouter_vanne(self, vanne):
        self.vannes.append(vanne)
        if len(self.vannes) == 1:
            self.heure_consigne = np.zeros((7, 48, 1))
        else :
            self.heure_consigne = np.concatenate((self.heure_consigne, np.zeros((7, 48, 1))), axis=2)

    def changer_consigne(self, new_consigne):
        self.consigne_generale = new_consigne
    
    def changer_heures_consigne(self, debut, fin):
        self.heure_debut = debut
        self.heure_fin = fin

    def changer_heure_consigne(self, heures):
        debut, fin, date = heures
        dates = np.array(["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche", "tous_les_jours"])
        nbdate = np.where(dates == date)[0][0]
        if nbdate < 7 :
            for k in range(debut * 2, fin * 2):
                self.heure_consigne[0, k] = True
        else :
            for k in range(debut * 2, fin * 2):
                for i in range(0, 7):
                    self.heure_consigne[i, k] = True
    

    def controler_chauffage(self, minute):
        for vanne in self.vannes:
            nbvanne = np.where(np.array(self.vannes) == vanne)[0]
            temperature = vanne.mesurer_temperature()
            jour = (minute%10080) // 1440
            heure = math.floor(((minute % 1440) /60) * 2)
            if self.heure_consigne[jour][heure][nbvanne]:
                if vanne.switchChauffe :
                    if vanne.mode == 'eco':
                        if temperature < (vanne.consigne):
                            vanne.ouverte = True
                        elif vanne.ouverte & (temperature > vanne.consigne):
                            vanne.ouverte = False
                            vanne.switchChauffe = False
                    if vanne.mode == 'confort':
                        if temperature < (vanne.consigne):
                            vanne.ouverte = True
                        else:
                            vanne.ouverte = False
            elif not(vanne.switchChauffe):
                vanne.switchChauffe = True
                vanne.ouverte = False
            elif vanne.ouverte :
                vanne.ouverte = False

class VanneThermostatique:
    def __init__(self, piece,radiateur, mode = 'eco', consigne=19.0):
        self.piece = piece
        self.radiateur = radiateur
        self.consigne = consigne
        self.ouverte = False
        self.switchChauffe = True
        self.mode = mode # eco ou confort

    def mesurer_temperature(self):
        return self.piece.temperature
    
    def changer_mode(self, mode):
        self.mode = mode