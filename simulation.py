"""
auteur : BEROUD Sebastien (FISE27)
date : 08-05-2025
description :
    Module simulant l'evolution de la temperature des differentes pieces d'une maison chauffee a l'aide du thermostat intelligent
"""

import math
from controle import ThermostatCentral, VanneThermostatique
import numpy as np

class Object_thermique:
    '''
    Défini un objet qui contient de l'énergie et qui peut recevoir et donner de l'énergie,
    perdant ou gagnant ainsi en température
    '''
    def __init__(self, temperature_init = 20):
        self.inertie = 10000 #juste pour définir la variable
        self.temperature = temperature_init
        self.chaleur = (273.15 + self.temperature) * self.inertie

    def transfer_chaleur(self, pertes):
        '''
        setteur permettant de modifier l'énergie contenue dans la pièce
        '''
        self.chaleur += pertes # les pertes sont algébriques

    def maj_temperature(self):
        '''
        met à jour la température quand il y a un changement de configuration vis-à-vis des pièces voisines
        '''
        self.temperature = (self.chaleur/self.inertie) - 273.15

class Piece(Object_thermique):
    '''
    Défini une pièce, élément élémentaire de la maison en fonction de ses caractéristiques de construction.
    On considère les temps d'homogénéisation de la température dans la pièces comme très rapides, d'où une température uniforme
    '''
    def __init__(self, nom, volume, temperature_init = 20):
        '''
        Constructeur de la classe.
        La pièce est considérée carré et de 2m de hauteur.

        inertie : correspond à l'énergie nécessaire pour augmenter la température de la pièce de 1°C. Cette inertie reproduit l'inertie moyenne en France d'une maison bien isolée.
                C'est-à-dire une perte d'environ 1°C toutes les 5h en absence de chauffage.
                Les détails du calcul sont dans le rapport.
        
        chaleur : correspond à l'énergie complète contenue dans la pièce. Cette valeur est directement modifiée, à chaque pas de temps, en fonction des échanges thermiques.
        '''
        super().__init__(temperature_init)
        self.nom = nom
        self.volume = volume
        self.nb_ext = 4
        self.surface_mur = math.sqrt(volume/2) * 2 #pièces carrées de 2m de hauteur
    # énergie nécessaire pour augmenter la pièce de 1°; capacité thermique massique = 1010 et masse volumique = 1.20 + 10% de la capacité thermique du mur --> reproduction de la réalité européenne de pertes d'une maison
        self.inertie = 1010 * self.volume * 1.20 + self.nb_ext * 60000 * self.surface_mur + (4-self.nb_ext) * 7650 * self.surface_mur
        self.radiateur = None

    def ajout_voisin(self):
        '''
        Permet de modifier l'inertie de la pièce en prenant en compte le nombre de murs en commun de la pièce avec l'extérieur.
        Les différences de nature des murs d'une pièce jouent sur son inertie.
        '''
        self.nb_ext -= 1
        self.inertie = 1010 * self.volume * 1.20 + self.nb_ext * 60000 * self.surface_mur + (4-self.nb_ext) * 7650 * self.surface_mur
        self.chaleur = (273.15 + self.temperature) * self.inertie


class Radiateur(Object_thermique):
    def __init__(self, surface_echange = 2.5, temperature_init = 20):
        super().__init__(temperature_init)
        self.surface_echange = surface_echange
        self.inertie = 10000
        self.piece = None


class Maison:
    """
    Classe représentant la maison dans son ensemble. C'est une composition des pièces et des thermostats.
    """
    def __init__(self, temperature_moyenne=12.0, amplitude_annuelle = 8.0, amplitude=4.0):
        '''
        Constructeur de la classe.
        self.connexions : dictionnaire qui recense toutes les pièces mitoyennes
        Rint: correspond à la résistance thermique des murs intéireurs de la maison
        Rext: correspond à la résistance thermique des murs extérieurs de la maison
        '''
        self.pieces = []
        self.connexions = {}
        self.pieces_vect = np.array([])
        self.calcul_vect = np.array([])
        self.temperature_vect = np.array([])
        self.Rint = 0.16 #(mur de placo de 2* 2cm d'épaisseur)
        self.Rext = 4.17 #(mur de 15 cm de laine de verre et 20 cm de parpaing)
        self.h_conv = 4 #W.K-1.m-2
        # Pour simulation de la temperature exterieur :
        self.temperature_moyenne = temperature_moyenne
        self.amplitude_annuelle = amplitude_annuelle
        self.amplitude = amplitude
        self.minute = 0

    def ajouter_piece(self, piece):
        '''
        fonction permettant d'ajouter une pièce à la maison
        '''
        self.pieces.append(piece)
        piece.radiateur = Radiateur()
        piece.radiateur.piece = piece
        self.connexions[piece] = []

    def connecter_pieces(self, piece1, piece2):
        '''
        fonction permettant de connecter deux pièces déjà existantes de la maison
        '''
        if piece1 in self.connexions: #raise error ?? / try ??
            self.connexions[piece1].append(piece2)
        if piece2 in self.connexions:
            self.connexions[piece2].append(piece1)
        piece1.ajout_voisin()
        piece2.ajout_voisin()

    def fin_de_modelisation(self):
        self.pieces_vect = np.array([0] + self.pieces + [i.radiateur for i in self.pieces])
        self.calcul_vect = np.zeros((len(self.pieces_vect), len(self.pieces_vect)))

        #On place les facteurs pour l'extérieur
        for k in range(1, len(self.pieces_vect)):
            if self.pieces_vect[k] in self.pieces :
                n = 4 - len(self.connexions[self.pieces_vect[k]])
                int =  n *self.pieces_vect[k].surface_mur / self.Rext
                self.calcul_vect[0][k] += int
                self.calcul_vect[k][k] -= int

        #On vient placer les facteurs internes
        for piece1 in self.connexions.keys():
            position1 = np.where(self.pieces_vect == piece1)[0][0]
            for voisine in self.connexions[piece1]:
                S = (piece1.surface_mur + voisine.surface_mur) / 2
                position2 = np.where(self.pieces_vect == voisine)[0][0]
                self.calcul_vect[position2][position1] += S / self.Rint
                self.calcul_vect[position1][position1] += - S / self.Rint
            position2 = np.where(self.pieces_vect == piece1.radiateur)[0][0]
            self.calcul_vect[position2][position1] += self.h_conv * piece1.radiateur.surface_echange
            self.calcul_vect[position1][position1] += - self.h_conv * piece1.radiateur.surface_echange
            self.calcul_vect[position2][position2] += - self.h_conv * piece1.radiateur.surface_echange
            self.calcul_vect[position1][position2] += self.h_conv * piece1.radiateur.surface_echange

        #On crée le vecteur de température inital
        self.temperature_vect = np.array([self.temperature_exterieure(0)] + [i.temperature for i in self.pieces] + [i.radiateur.temperature for i in self.pieces])

    def temperature_exterieure(self, minute):
        """
        Calcule la température extérieure en fonction de l'heure (minute du jour).
        """

        # --- Variation annuelle ---
        jour = (minute % 525600) / 1440
        # décalé pour que le minimum est lieu vers le 21 janvier (~jour 21)
        temp_saison = self.temperature_moyenne + self.amplitude_annuelle * math.sin(-2 * math.pi * (jour + 21) / 365)

        # --- Variation journalière ---
        min = minute % 1440
        # pic journalier à 15h (900 min), minimum vers 3h (180 min)
        temp_jour = self.amplitude * math.sin(-2 * math.pi * (min + 180) / 1440)

        return temp_saison + temp_jour

    def echange_chaleur(self, minute):
        '''
        fonction qui simule les échangent de châleur entre les pièces et avec l'extérieur
        '''
        ### Code en l'absence de calcul vectoriel
        # for piece in self.connexions.keys():
        #     for voisine in self.connexions[piece]:
        #         echange = (piece.temperature - voisine.temperature)/(self.Rint/piece.surface_mur) #énergie échange en 1 sec par le mur
        #         piece.transfer_chaleur(-60 * echange) # pas de temps de 1 min donc 60 sec
        #         print(60 * echange)
        #     échanges de châleur avec l'extérieur
        #     echange = self.h_conv * (piece.temperature - piece.radiateur.temperature) * piece.radiateur.surface_echange
        #     print(60 * echange)
        #     piece.transfer_chaleur(-60 * echange)
        #     piece.radiateur.transfer_chaleur(60 * echange)
        #     n = 4 - len(self.connexions[piece])
        #     echange = n * (piece.temperature - self.temperature_exterieure(minute)) / (self.Rext/piece.surface_mur)
        #     print(60 * echange)
        #     piece.transfer_chaleur(-60 * echange)

        # prise en compte des echanges de chaleur entre les pièces

        echange = (self.temperature_vect @ self.calcul_vect) * 60 #puissance pendant 60 secondes
        for i in range (1, len(self.pieces_vect)):
            self.pieces_vect[i].transfer_chaleur(echange[i])

    def maj_temperature(self, minute):
        '''
        fonction qui met à jour la température dans toutes les pièces de la maison après que tous les échanges thermiques aient été effectués
        '''
        for piece in self.connexions.keys():
            piece.maj_temperature()
            piece.radiateur.maj_temperature()
        self.temperature_vect = np.array([self.temperature_exterieure(minute + 1)] + [i.temperature for i in self.pieces] + [i.radiateur.temperature for i in self.pieces])


def initialiser_systeme(liste_pieces, consigne = 19):
    '''
    
    '''
    thermostat = ThermostatCentral()
    vannes = []

    for piece in liste_pieces:
        vanne = VanneThermostatique(piece=piece, radiateur = piece.radiateur, consigne = consigne)
        thermostat.ajouter_vanne(vanne)
        vannes.append(vanne)
    thermostat.fin_de_construction()

    return thermostat, vannes


# Je pense que lancer_simulation decrit en fait le comportement du thermostat

def lancer_simulation(maison, thermostat, duree_minutes=1440):
    resultats = {vanne.piece.nom: [] for vanne in thermostat.vannes}
    resultats["Exterieur"] = []
    # resultats["alpha"] = []
    # resultats["puissance"] = []

    for minute in range(duree_minutes):
        # Diffusion interne
        maison.minute += 1
        maison.echange_chaleur(maison.minute)

        # Fournir chaleur
        thermostat.controler_chauffage(maison.minute)
        for vanne in thermostat.vannes:
            if vanne.ouverte:
                vanne.radiateur.transfer_chaleur(vanne.chauffer() * 60) #en joule

        maison.maj_temperature(maison.minute)
        #print(maison.pieces[1].radiateur.temperature)

        # Stocker résultats
        for vanne in thermostat.vannes:
            resultats[vanne.piece.nom].append(vanne.piece.temperature)

        # Stocker température extérieure
        resultats["Exterieur"].append(maison.temperature_exterieure(maison.minute))

        # resultats["alpha"] = (thermostat.opti.donner_coeffs(thermostat.vannes[0])[0])
        # temp = (thermostat.opti.donner_puissance(thermostat.vannes[0]))
        # if len(temp) > 0 :
        #     resultats["puissance"].append((thermostat.opti.donner_puissance(thermostat.vannes[0]))[-1])
        # else :
        #     resultats["puissance"].append(0)
    return resultats