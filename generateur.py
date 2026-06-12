import random
import json
import os

def generer_partition(largeur, hauteur, taille_max=5):
    """Divise la grille en plusieurs motifs aléatoires de taille 1 à 5."""
    non_assignees = set((x, y) for x in range(largeur) for y in range(hauteur))
    motifs = []
    
    while non_assignees:
        depart = random.choice(list(non_assignees))
        motif_actuel = [depart]
        non_assignees.remove(depart)
        taille_cible = random.randint(1, taille_max)
        
        for _ in range(taille_cible - 1):
            voisins = set()
            for cx, cy in motif_actuel:
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) in non_assignees:
                        voisins.add((nx, ny))
            
            if not voisins:
                break
                
            prochaine_case = random.choice(list(voisins))
            motif_actuel.append(prochaine_case)
            non_assignees.remove(prochaine_case)
            
        motifs.append(motif_actuel)
    return motifs

def resoudre_grille(largeur, hauteur, motifs):
    """Remplit la grille avec des chiffres valides selon les règles du jeu (Néonaure)."""
    valeurs = {}
    case_vers_motif = {}
    
    for index, motif in enumerate(motifs):
        for case in motif:
            case_vers_motif[case] = (index, len(motif))
            
    def est_valide(x, y, v):
        """Vérifie si un chiffre respecte les contraintes de voisinage et de motif."""
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                if valeurs.get((x+dx, y+dy)) == v:
                    return False
                    
        m_index, _ = case_vers_motif[(x, y)]
        for cx, cy in motifs[m_index]:
            if valeurs.get((cx, cy)) == v:
                return False
        return True

    cases = [(x, y) for x in range(largeur) for y in range(hauteur)]
    iterations = [0]
    
    def backtrack(index_case):
        """Algorithme récursif d'essai-erreur pour trouver une solution valide."""
        iterations[0] += 1
        if iterations[0] > 3000:
            return False
            
        if index_case == len(cases):
            return True
            
        cx, cy = cases[index_case]
        _, taille_m = case_vers_motif[(cx, cy)]
        
        chiffres_possibles = list(range(1, taille_m + 1))
        random.shuffle(chiffres_possibles)
        
        for v in chiffres_possibles:
            if est_valide(cx, cy, v):
                valeurs[(cx, cy)] = v
                if backtrack(index_case + 1):
                    return True
                del valeurs[(cx, cy)]
        return False

    if backtrack(0):
        return valeurs
    return None

def generer_grilles_massives(nombre_de_grilles=100, dossier_sortie="grilles_generees"):
    """Génère un nombre défini de grilles valides et les exporte au format JSON."""
    os.makedirs(dossier_sortie, exist_ok=True)
    compteur = 0
    
    print(f"Début de la génération de {nombre_de_grilles} grilles...")
    
    while compteur < nombre_de_grilles:
        largeur = random.randint(6, 8)
        hauteur = random.randint(6, 8)
        
        motifs = generer_partition(largeur, hauteur)
        valeurs = resoudre_grille(largeur, hauteur, motifs)
        
        if valeurs:
            difficulte = random.uniform(0.5, 0.75) 
            
            json_final = {}
            for i, motif in enumerate(motifs):
                motif_data = []
                for cx, cy in motif:
                    if random.random() < difficulte:
                        v = 0
                    else:
                        v = valeurs[(cx, cy)]
                    motif_data.append([cx, cy, v])
                json_final[f"motif{i+1}"] = motif_data
                
            nom_fichier = os.path.join(dossier_sortie, f"grille_auto_{compteur+1}.json")
            with open(nom_fichier, 'w') as f:
                json.dump(json_final, f)
                
            compteur += 1
            print(f"[{compteur}/{nombre_de_grilles}] -> {nom_fichier} générée avec succès !")

if __name__ == "__main__":
    """Point d'entrée du script pour lancer la génération de masse."""
    generer_grilles_massives(100)
    print("Terminé ! Vous pouvez copier les grilles dans le dossier de votre jeu.")