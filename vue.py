import tkinter as tk

class VueNeonaure(tk.Frame):
    def __init__(self, parent):
        """
        Initialise le composant visuel de la grille.
        'parent' sera la fenêtre principale créée par le Contrôleur.
        """
        super().__init__(parent)
        self.taille_case = 50 # Taille en pixels d'une case
        
        # Création du Canvas pour dessiner la grille
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(padx=20, pady=20)
        
        # Dictionnaire pour garder une trace des textes affichés (pour les mettre à jour plus tard)
        self.identifiants_textes = {}

    def dessiner_grille(self, largeur, hauteur, cases_valeurs, cases_motifs):
        """
        Méthode appelée par le Contrôleur pour dessiner la grille.
        - largeur, hauteur : dimensions de la grille (ex: 8, 8 ou 5, 13)
        - cases_valeurs : dict {(x, y): valeur_chiffre} (0 si case vide)
        - cases_motifs : dict {(x, y): id_du_motif}
        """
        # 1. Ajuster la taille du Canvas et le vider
        self.canvas.config(width=largeur * self.taille_case, height=hauteur * self.taille_case)
        self.canvas.delete("all")
        self.identifiants_textes.clear()

        # 2. Dessiner chaque case
        for y in range(hauteur):
            for x in range(largeur):
                x_pixel = x * self.taille_case
                y_pixel = y * self.taille_case
                
                # Récupérer l'ID du motif actuel
                motif_actuel = cases_motifs.get((x, y))
                
                # --- DESSIN DES BORDURES (Logique des traits gras) ---
                
                # Bordure HAUT
                motif_haut = cases_motifs.get((x, y - 1))
                epaisseur_haut = 3 if motif_actuel != motif_haut else 1
                self.canvas.create_line(x_pixel, y_pixel, x_pixel + self.taille_case, y_pixel, width=epaisseur_haut)

                # Bordure GAUCHE
                motif_gauche = cases_motifs.get((x - 1, y))
                epaisseur_gauche = 3 if motif_actuel != motif_gauche else 1
                self.canvas.create_line(x_pixel, y_pixel, x_pixel, y_pixel + self.taille_case, width=epaisseur_gauche)

                # Bordure BAS (Gérée par le haut de la case du dessous, sauf pour la dernière ligne)
                if y == hauteur - 1:
                    self.canvas.create_line(x_pixel, y_pixel + self.taille_case, x_pixel + self.taille_case, y_pixel + self.taille_case, width=3)
                    
                # Bordure DROITE (Gérée par la gauche de la case d'à côté, sauf pour la dernière colonne)
                if x == largeur - 1:
                    self.canvas.create_line(x_pixel + self.taille_case, y_pixel, x_pixel + self.taille_case, y_pixel + self.taille_case, width=3)

                # --- DESSIN DES CHIFFRES ---
                valeur = cases_valeurs.get((x, y), 0)
                if valeur > 0:
                    # C'est un indice fixe, on l'affiche en gras
                    self.canvas.create_text(
                        x_pixel + self.taille_case / 2, 
                        y_pixel + self.taille_case / 2, 
                        text=str(valeur), 
                        font=("Arial", 16, "bold"),
                        fill="black"
                    )
                else:
                    # C'est une case vide à remplir, on prépare un texte invisible/vide
                    id_texte = self.canvas.create_text(
                        x_pixel + self.taille_case / 2, 
                        y_pixel + self.taille_case / 2, 
                        text="", 
                        font=("Arial", 16, "normal"),
                        fill="blue" # En bleu pour différencier les entrées du joueur
                    )
                    self.identifiants_textes[(x, y)] = id_texte

    def mettre_a_jour_case(self, x, y, nouvelle_valeur):
        """Méthode pour afficher un chiffre tapé par le joueur."""
        if (x, y) in self.identifiants_textes:
            id_texte = self.identifiants_textes[(x, y)]
            texte_a_afficher = str(nouvelle_valeur) if nouvelle_valeur > 0 else ""
            self.canvas.itemconfig(id_texte, text=texte_a_afficher)