# controle.py
import numpy as np
import math
import random

def generate_heating_schedule() -> np.ndarray:
    """
    Renvoie un tableau NumPy de forme (7, 48, 3) où :
      • 1ʳᵉ dim.  (0-6)  = jours de la semaine (0=lundi … 6=dimanche)
      • 2ᵉ dim.  (0-47) = tranches de 30 min (0 = 00h00, 1 = 00h30, ...)
      • 3ᵉ dim.  (0-2)  = radiateurs / pièces

    La valeur est 1 si le chauffage doit être allumé, 0 sinon.

    Règles :
      • Tous les jours  :  07 h 00 → 10 h 00  et  19 h 00 → 21 h 00
      • Week-end (sam, dim) :  créneau supplémentaire 12 h 00 → 17 h 00
    """
    schedule = np.zeros((7, 48, 3), dtype=int)

    # Créneaux communs (en heures)
    common_slots = [(7, 10), (19, 21)]

    # Helper pour convertir les heures en indices 30 minutes
    def hour_to_index(h):
        return int(h * 2)

    # Appliquer les créneaux communs à tous les jours
    for day in range(7):
        for start_h, end_h in common_slots:
            start_idx = hour_to_index(start_h)
            end_idx   = hour_to_index(end_h)
            schedule[day, start_idx:end_idx, :] = 1

    # Week-end : ajout du créneau 12h-17h
    for day in [5, 6]:  # samedi = 5, dimanche = 6
        start_idx = hour_to_index(12)
        end_idx   = hour_to_index(17)
        schedule[day, start_idx:end_idx, :] = 1

    return schedule

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
        self.heure_consigne = generate_heating_schedule()

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

    def fin_de_construction(self):
        self.opti = Optimisation(self.vannes)

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
                vanne.switchOptimisation = False
            elif vanne.ouverte :
                vanne.ouverte = False
                vanne.switchOptimisation = False
            if vanne.switchOptimisation == False :
                self.opti.optimiser(vanne, vanne.switchPuissance, vanne.piece.temperature)
                vanne.switchOptimisation = True
                vanne.switchPuissance = 0

class VanneThermostatique:
    def __init__(self, piece, radiateur, mode = 'eco', consigne=19.0):
        self.piece = piece
        self.radiateur = radiateur
        self.consigne = consigne
        self.ouverte = False
        self.switchChauffe = True
        self.switchPuissance = 0
        self.switchOptimisation = True

        self.mode = mode # eco ou confort
        self.alpha = 1
        self.beta = 1
        self.puissance_max = 1000

    def mesurer_temperature(self):
        return self.piece.temperature

    def changer_mode(self, mode):
        self.mode = mode

    def chauffer(self):
        if self.ouverte :
            deltaT = self.consigne - self.piece.temperature
            if deltaT > 0:
                puissance = self.puissance_max * self.alpha * (1 - math.exp(-self.beta * deltaT))
                self.switchPuissance += puissance * 60
                return puissance

class Optimisation:
    def __init__(self, vannes):
        self.vannes = np.array(vannes)
        self.coeffs_alpha = [[] for i in range(len(self.vannes))]
        self.coeffs_beta = [[] for i in range(len(self.vannes))]
        self.puissances = [[] for i in range(len(self.vannes))]
        self.Tfin = [[] for i in range(len(self.vannes))]
    
    def donner_coeffs(self, vanne):
        nb = np.where(self.vannes == vanne)[0][0]
        return self.coeffs_alpha[nb], self.coeffs_beta[nb]

    def donner_puissance(self, vanne):
        nb = np.where(self.vannes == vanne)[0][0]
        return self.puissances[nb]
    
    def cout(self, puissance, Tfinal, consigne ):
        if Tfinal >= consigne:
            return puissance
        else :
            return puissance + (consigne - Tfinal) * 10000000000

    def optimiser(self, vanne, puissance, Tfinal):
        nb = np.where(self.vannes == vanne)[0][0]
        if len(self.puissances[nb]) > 0 :
            last_cout = self.cout(self.puissances[nb][-1], self.Tfin[nb][-1], vanne.consigne)
            new_cout = self.cout(puissance, Tfinal, vanne.consigne)
            self.puissances[nb].append(puissance)
            self.Tfin[nb].append(Tfinal)
            if last_cout > new_cout :
                i, j = random.randint(0, 1), random.randint(0,1)
                self.coeffs_alpha[nb].append(vanne.alpha)
                self.coeffs_beta[nb].append(vanne.beta)
                if i :
                    if j:
                        vanne.alpha = vanne.alpha * 0.95
                    else :
                        if vanne.alpha * 1.05 <= 1:
                            vanne.alpha = vanne.alpha * 1.05
                        else :
                            vanne.alpha = 1
                else :
                    if j:
                        vanne.beta = vanne.beta * 0.95
                    else :
                        vanne.beta = vanne.beta * 1.05
            else:
                i, j = random.randint(0, 1), random.randint(0,1)
                self.coeffs_alpha[nb].append(vanne.alpha)
                self.coeffs_beta[nb].append(vanne.beta)
                if i :
                    if j:
                        vanne.alpha = self.coeffs_alpha[nb][-2] * 0.95
                    else :
                        if self.coeffs_alpha[nb][-2]  * 1.05 <= 1 :
                            vanne.alpha = self.coeffs_alpha[nb][-2]  * 1.05
                        else :
                            vanne.alpha = 1
                else :
                    if j:
                        vanne.beta = self.coeffs_beta[nb][-2]  * 0.95
                    else :
                        vanne.beta = self.coeffs_beta[nb][-2]  * 1.05
        else :
            self.puissances[nb].append(puissance)
            self.Tfin[nb].append(Tfinal)
            self.coeffs_alpha[nb].append(vanne.alpha)
            self.coeffs_beta[nb].append(vanne.beta)
            i, j = random.randint(0, 1), random.randint(0,1)
            if i :
                if j:
                    vanne.alpha = 0.95
                else :
                    vanne.alpha = 1
            else :
                if j:
                    vanne.beta = 0.95
                else :
                    vanne.beta = 1.05
