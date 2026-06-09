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

    # Charge une grille depuis un fichier JSON et peuple les dictionnaires
    def charger_json(self, nom_fichier):
        with open(nom_fichier, 'r') as f:
            donnees = json.load(f)

        for nom_motif, liste_cases in donnees.items():
            nouveau_motif = Motif(nom_motif)
            for case in liste_cases:
                x, y, valeur = case[0], case[1], case[2]
                nouveau_motif.ajouter_case(x, y)
                self.valeurs[(x, y)] = valeur
                
            self.motifs[nom_motif] = nouveau_motif
            
        self.generer_graphe()

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


if __name__ == "__main__":
    ma_grille = Grille()
    ma_grille.charger_json("grille/grille1.json")
    
    print("--- TEST DU GRAPHE ---")
    print("Voisins de la case (0, 0) :", ma_grille.graphe[(0, 0)])
    print("Voisins de la case (1, 1) :", ma_grille.graphe[(1, 1)])