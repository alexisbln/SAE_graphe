import json

class Motif:
    # Initialise un motif avec son nom, sa liste de cases et sa taille
    def __init__(self, nom):
        self.nom = nom
        self.cases = []
        self.taille = 0

    # Ajoute les coordonnées d'une case au motif et met à jour sa taille
    def ajouter_case(self, x, y):
        self.cases.append((x, y))
        self.taille += 1


class Grille:
    # Initialise la grille avec ses dictionnaires de données
    def __init__(self):
        self.motifs = {}
        self.valeurs = {}
        self.graphe = {}
        self.cases_initiales = set()

    # Charge une grille depuis un fichier JSON et peuple les dictionnaires
    def charger_json(self, nom_fichier):
        self.cases_initiales.clear()
        with open(nom_fichier, 'r') as f:
            donnees = json.load(f)

        for nom_motif, liste_cases in donnees.items():
            nouveau_motif = Motif(nom_motif)
            for case in liste_cases:
                x, y, valeur = case[0], case[1], case[2]
                nouveau_motif.ajouter_case(x, y)
                self.valeurs[(x, y)] = valeur
                
                if valeur > 0:
                    self.cases_initiales.add((x, y))
                    
            self.motifs[nom_motif] = nouveau_motif
            
        self.generer_graphe()

    # Sauvegarde la grille actuelle dans un fichier JSON
    def sauvegarder_json(self, nom_fichier):
        donnees_a_sauver = {}
        for nom_motif, motif in self.motifs.items():
            liste_cases = []
            for x, y in motif.cases:
                valeur = self.valeurs.get((x, y), 0)
                liste_cases.append([x, y, valeur])
            donnees_a_sauver[nom_motif] = liste_cases
            
        with open(nom_fichier, 'w') as f:
            json.dump(donnees_a_sauver, f)

    # Crée le dictionnaire d'adjacence reliant chaque case à ses voisins
    def generer_graphe(self):
        for (x, y) in self.valeurs.keys():
            voisins = []
            directions = [(-1, -1), (-1, 0), (-1, 1), 
                          (0, -1),           (0, 1), 
                          (1, -1),  (1, 0),  (1, 1)]
            
            for dx, dy in directions:
                voisin_x, voisin_y = x + dx, y + dy
                if (voisin_x, voisin_y) in self.valeurs:
                    voisins.append((voisin_x, voisin_y))
                    
            self.graphe[(x, y)] = voisins

    # Vérifie si une valeur peut être placée en (x, y) selon les règles du jeu
    def est_coup_valide(self, x, y, test_valeur):
        for voisin in self.graphe[(x, y)]:
            if self.valeurs[voisin] == test_valeur:
                return False

        motif_actuel = None
        for motif in self.motifs.values():
            if (x, y) in motif.cases:
                motif_actuel = motif
                break

        if test_valeur < 1 or test_valeur > motif_actuel.taille:
            return False

        for case in motif_actuel.cases:
            if case != (x, y) and self.valeurs[case] == test_valeur:
                return False

        return True
            
    # Trouve et renvoie les coordonnées (x, y) de la première case vide (valeur 0)
    def trouver_case_vide(self):
        for case, valeur in self.valeurs.items():
            if valeur == 0:
                return case
        return None

    # Résout la grille par essai-erreur (backtracking) et renvoie True si résolue
    def resoudre(self):
        case_vide = self.trouver_case_vide()
        if not case_vide:
            return True

        x, y = case_vide
        
        motif_actuel = None
        for motif in self.motifs.values():
            if (x, y) in motif.cases:
                motif_actuel = motif
                break

        for test_valeur in range(1, motif_actuel.taille + 1):
            if self.est_coup_valide(x, y, test_valeur):
                self.valeurs[(x, y)] = test_valeur
                
                if self.resoudre():
                    return True
                    
                self.valeurs[(x, y)] = 0
                
        return False

    # Renvoie la valeur actuelle de la case aux coordonnées (x, y)
    def get_valeur(self, x, y):
        return self.valeurs.get((x, y), 0)

    # Modifie la valeur de la case aux coordonnées (x, y)
    def set_valeur(self, x, y, valeur):
        self.valeurs[(x, y)] = valeur

    # Remet toutes les cases de la grille à 0
    def vider_grille(self):
        for case in self.valeurs.keys():
            self.valeurs[case] = 0

