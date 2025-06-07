# test.py

import unittest
from simulation import *
from controle import *

class TestSimulation(unittest.TestCase):
    def test_object_thermique(self):
        for k in range(-50, 50) :
            obj = Object_thermique(25)
            obj.transfer_chaleur(k * obj.inertie)
            obj.maj_temperature()
            self.assertAlmostEqual(obj.temperature, 25 + k, places = 5)

    def test_piece(self):
        salon = Piece("salon", 30, temperature_init= 25)
        self.assertEqual(salon.temperature, 25)
        ancienInertie = salon.inertie
        ancienChaleur = salon.chaleur
        salon.ajout_voisin()
        self.assertTrue(salon.inertie < ancienInertie)
        self.assertNotEqual(salon.chaleur, ancienChaleur)

    def test_maison(self):
        maison = Maison()
        salon = Piece("salon", 20)
        chambre = Piece("chambre", 15)
        maison.ajouter_piece(salon)
        maison.ajouter_piece(chambre)
        maison.connecter_pieces(salon, chambre)
        maison.fin_de_modelisation()
        self.assertEqual(len(maison.pieces), 2)
        self.assertTrue(maison.temperature_exterieure(30240) < 4)
        ancien = salon.temperature
        maison.echange_chaleur(30240)
        maison.maj_temperature(30240)
        self.assertNotAlmostEqual(ancien, salon.temperature)
    
class TestControle(unittest.TestCase):
    def test_ThermostatCentral(self):
        maison = Maison()
        salon = Piece("salon", 20)
        chambre = Piece("chambre", 15)
        maison.ajouter_piece(salon)
        maison.ajouter_piece(chambre)
        maison.connecter_pieces(salon, chambre)
        maison.fin_de_modelisation()
        thermostat = ThermostatCentral()
        vanne1 = VanneThermostatique(salon, salon.radiateur)
        vanne2 = VanneThermostatique(chambre, chambre.radiateur)
        thermostat.ajouter_vanne(vanne1)
        thermostat.ajouter_vanne(vanne2)
        thermostat.fin_de_construction()
        thermostat.changer_heure_consigne(vanne1, (10, 16, 'mardi'))
        self.assertEqual(len(thermostat.vannes), 2)
        self.assertEqual(thermostat.heure_consigne[1, 27, 0], 1)
        vanne1.consigne = 40
        thermostat.controler_chauffage(1440 + 810)
        self.assertEqual(vanne1.ouverte, True)
        thermostat.changer_heure_consigne(vanne1, (10, 16, 'mardi'))
        self.assertEqual(thermostat.heure_consigne[1, 27, 0], 0)
        thermostat.controler_chauffage(1440 + 810)
        self.assertEqual(vanne1.ouverte, False)
    
    def test_VanneThermostatique(self):
        maison = Maison()
        salon = Piece("salon", 20)
        maison.ajouter_piece(salon)   
        maison.fin_de_modelisation()     
        vanne1 = VanneThermostatique(salon, salon.radiateur)
        salon.temperature = 25
        vanne1.consigne = 40
        self.assertEqual(vanne1.mesurer_temperature(), 25)
        self.assertIsNone(vanne1.chauffer())
        vanne1.ouverte = True
        self.assertLessEqual(vanne1.chauffer(), vanne1.puissance_max)

if __name__ == '__main__':
    unittest.main()
