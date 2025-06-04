# controle.py
import numpy as np
import math

class ThermostatCentral:
    def __init__(self, mode='eco', heure_consigne = [], debut = 7, fin = 18, consigne=18.0):
        self.mode = mode        #eco or comfort
        self.consigne_generale = consigne
        self.heure_consigne = heure_consigne
        self.heure_debut = debut
        self.heure_fin = fin
        self.vannes = []
        self.SwitchChauffe = True

    def ajouter_vanne(self, vanne):
        self.vannes.append(vanne)
        if len(self.vannes) == 1:
            self.heure_consigne = np.zeros((7, 48, 1))
        else :
            self.heure_consigne = np.concatenate((self.heure_consigne, np.zeros((7, 48, 1))), axis=2)

    def changer_mode(self, mode):
        self.mode = mode

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
            temperature = vanne.mesurer_temperature()
            jour = (minute%10080) // 1440
            heure = math.floor(((minute % 1440) /60) * 2)
            Vvannes = np.array(self.vannes == vanne)
            if self.heure_consigne[jour][heure][np.where(Vvannes)]:
                if self.SwitchChauffe :
                    if self.mode == 'eco':
                        if temperature < (vanne.consigne):
                            vanne.ouverte = True
                        elif vanne.ouverte & (temperature > vanne.consigne):
                            vanne.ouverte = False
                            self.SwitchChauffe = False
                    if self.mode == 'confort':
                        if temperature < (vanne.consigne):
                            vanne.ouverte = True
                        else:
                            vanne.ouverte = False
            elif not(self.SwitchChauffe):
                self.SwitchChauffe = True
                vanne.ouverte = False
            elif vanne.ouverte :
                vanne.ouverte = False

class VanneThermostatique:
    def __init__(self, piece,radiateur, consigne=19.0):
        self.piece = piece
        self.radiateur = radiateur
        self.consigne = consigne
        self.ouverte = False

    def mesurer_temperature(self):
        return self.piece.temperature

    # NOT USED
    def ajuster_etat(self, mode):
        temperature = self.mesurer_temperature()
        if mode == 'eco':
            self.ouverte = temperature < (self.consigne - 1.0)
        elif mode == 'confort':
            self.ouverte = temperature < self.consigne