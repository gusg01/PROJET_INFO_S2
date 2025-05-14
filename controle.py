# controle.py

class ThermostatCentral:
    def __init__(self, mode='eco', consigne=18.0):
        self.mode = mode
        self.consigne_generale = consigne
        self.vannes = []

    def ajouter_vanne(self, vanne):
        self.vannes.append(vanne)

    def changer_mode(self, mode):
        self.mode = mode

    def changer_consigne(self, new_consigne):
        self.consigne_generale = new_consigne

    def controler_chauffage(self):
        for vanne in self.vannes:
            temperature = vanne.mesurer_temperature()
            if self.mode == 'eco':
                if temperature < (vanne.consigne - 1.0):
                    vanne.ouverte = True
                elif (temperature < vanne.consigne)and(vanne.ouverte):
                    vanne.ouverte = True
                else:
                    vanne.ouverte = False            
            if self.mode == 'confort':
                if temperature < (vanne.consigne):
                    vanne.ouverte = True
                else:
                    vanne.ouverte = False

        # Contrôle du chauffage
        # besoin_chauffage = any(vanne.ouverte for vanne in self.vannes)
        # if besoin_chauffage:
        #     chauffage.allumer()
        # else:
        #     chauffage.eteindre()

class VanneThermostatique:
    def __init__(self, piece, consigne=19.0):
        self.piece = piece
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



