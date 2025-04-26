class ThermostatCentral:
    """
    Classe représentant le thermostat centralisé.
    Gère la température de référence et les modes de fonctionnement.
    """
    def __init__(self, mode='eco'):
        self.mode = mode  # 'eco' ou 'confort'
        self.consigne_generale = 19.0
        self.vannes = []  # Liste des vannes connectées
    
    def ajouter_vanne(self, vanne):
        self.vannes.append(vanne)

    def changer_mode(self, mode):
        self.mode = mode

    def controler_chauffage(self):
        """
        Détermine si le chauffage doit être déclenché selon le mode.
        """
        pass


class VanneThermostatique:
    """
    Classe représentant une vanne thermostatique connectée.
    """
    def __init__(self, piece, consigne=19.0):
        self.piece = piece
        self.consigne = consigne
        self.ouverte = False
    
    def mesurer_temperature(self):
        return self.piece.temperature

    def ajuster_etat(self, mode):
        pass


class Piece:
    """
    Classe représentant une pièce de la maison.
    """
    def __init__(self, nom, volume, inertie_thermique=1.0):
        self.nom = nom
        self.volume = volume
        self.inertie_thermique = inertie_thermique
        self.temperature = 18.0
        self.perte_temperature = 0.05  # °C perdu par minute sans chauffage

    def perdre_chaleur(self):
        self.temperature -= self.perte_temperature / self.inertie_thermique

    def chauffer(self, apport):
        self.temperature += apport / (self.volume * self.inertie_thermique)


class Chauffage:
    """
    Classe représentant le système de chauffage général.
    """
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
    def __init__(self):
        self.pieces = []  # Liste des pièces
        self.connexions = {}  # Connexions entre pièces
        self.perte_exterieure = 0.1  # °C/min vers l'extérieur

    def ajouter_piece(self, piece):
        self.pieces.append(piece)
        self.connexions[piece] = []

    def connecter_pieces(self, piece1, piece2):
        if piece1 in self.connexions:
            self.connexions[piece1].append(piece2)
        if piece2 in self.connexions:
            self.connexions[piece2].append(piece1)

    def diffusion_chaleur(self):
        variations = {}
        for piece, voisines in self.connexions.items():
            for voisine in voisines:
                delta = (voisine.temperature - piece.temperature) * 0.01
                variations[piece] = variations.get(piece, 0) + delta
                variations[voisine] = variations.get(voisine, 0) - delta

        for piece, variation in variations.items():
            piece.temperature += variation

    def perte_vers_exterieur(self):
        for piece in self.pieces:
            piece.temperature -= self.perte_exterieure / piece.inertie_thermique