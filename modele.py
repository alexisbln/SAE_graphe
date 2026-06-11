import json

class Motif:
    def __init__(self, nom):
        """Initialise un motif avec son nom, sa liste de cases et sa taille."""
        self.nom = nom
        self.cases = []
        self.taille = 0

    def ajouter_case(self, x, y):
        """Ajoute les coordonnées d'une case au motif et met à jour sa taille."""
        self.cases.append((x, y))
        self.taille += 1


class Grille:
    def __init__(self):
        """Initialise la grille avec ses dictionnaires de données et cases de départ."""
        self.motifs = {}
        self.valeurs = {}
        self.graphe = {}
        self.cases_initiales = set()

    def charger_json(self, nom_fichier):
        """Charge une grille depuis un fichier JSON, peuple les dictionnaires et génère le graphe."""
        self.cases_initiales.clear()
        with open(nom_fichier, 'r') as f:
            donnees = json.load(f)

        for nom_motif, liste_cases in donnees.items():
            nouveau_motif = Motif(nom_motif)
            for case in liste_cases:
                x, y, valeur = case[0], case[1], case[2]
                nouveau_motif.ajouter_case(x, y)
                self.valeurs[(x, y)] = valeur
                
                if len(case) > 3:
                    est_initial = case[3]
                    if est_initial:
                        self.cases_initiales.add((x, y))
                else:
                    if valeur > 0:
                        self.cases_initiales.add((x, y))
                    
            self.motifs[nom_motif] = nouveau_motif
            
        self.generer_graphe()

    def sauvegarder_json(self, nom_fichier):
        """Sauvegarde la grille actuelle et l'état des cases initiales dans un fichier JSON."""
        donnees_a_sauver = {}
        for nom_motif, motif in self.motifs.items():
            liste_cases = []
            for x, y in motif.cases:
                valeur = self.valeurs.get((x, y), 0)
                est_initial = (x, y) in self.cases_initiales 
                liste_cases.append([x, y, valeur, est_initial])
            donnees_a_sauver[nom_motif] = liste_cases
            
        with open(nom_fichier, 'w') as f:
            json.dump(donnees_a_sauver, f)

    def generer_graphe(self):
        """Crée le dictionnaire d'adjacence reliant chaque case à tous ses voisins (diagonales incluses)."""
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

    def est_coup_valide(self, x, y, test_valeur):
        """Vérifie si une valeur peut être placée en (x, y) selon les règles de voisinage et de motif."""
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
            
    def trouver_case_vide(self):
        """Trouve et renvoie les coordonnées (x, y) de la première case vide (valeur 0) trouvée."""
        for case, valeur in self.valeurs.items():
            if valeur == 0:
                return case
        return None

    def resoudre(self):
        """Résout la grille par essai-erreur (backtracking) et renvoie True si une solution existe."""
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

    def verifier_victoire(self):
        """Vérifie si toutes les cases de la grille sont remplies (condition de victoire)."""
        for valeur in self.valeurs.values():
            if valeur == 0:
                return False
        return True

    def get_valeur(self, x, y):
        """Renvoie la valeur actuelle de la case aux coordonnées demandées."""
        return self.valeurs.get((x, y), 0)

    def set_valeur(self, x, y, valeur):
        """Modifie la valeur de la case aux coordonnées (x, y)."""
        self.valeurs[(x, y)] = valeur

    def vider_grille(self):
        """Remet toutes les cases (sauf celles de départ) de la grille à 0."""
        for (x, y) in self.valeurs.keys():
            if (x, y) not in self.cases_initiales:
                self.valeurs[(x, y)] = 0