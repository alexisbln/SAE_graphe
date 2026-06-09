import tkinter as tk

class VueNeonaure(tk.Frame):
    
    def __init__(self, parent, action_clic):
        super().__init__(parent)
        
        # Taille d'une case en pixels
        self.taille_case = 50 
        
        # Fonction à appeler quand le joueur clique
        self.action_clic = action_clic 
        
        # Zone de dessin pour la grille
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(padx=20, pady=20)
        
        # On écoute les clics de la souris sur la zone de dessin
        self.canvas.bind("<Button-1>", self._au_clic)
        
        # Dictionnaire pour retrouver les textes affichés
        self.identifiants_textes = {}

    def _au_clic(self, event):
        # Calcul de la colonne et de la ligne cliquées
        colonne_x = event.x // self.taille_case
        ligne_y = event.y // self.taille_case
        
        # On prévient le contrôleur du clic
        self.action_clic(colonne_x, ligne_y)

    def dessiner_grille(self, largeur, hauteur, cases_valeurs, cases_motifs):
        # On ajuste la taille de la zone et on efface tout
        self.canvas.config(width=largeur * self.taille_case, height=hauteur * self.taille_case)
        self.canvas.delete("all")
        self.identifiants_textes.clear()

        # On parcourt chaque case de la grille
        for y in range(hauteur):
            for x in range(largeur):
                
                # Calcul de la position en pixels
                x_pixel = x * self.taille_case
                y_pixel = y * self.taille_case
                
                # Numéro du motif de la case actuelle
                motif_actuel = cases_motifs.get((x, y))
                
                # Bordure du haut : trait épais si le motif au-dessus est différent
                motif_haut = cases_motifs.get((x, y - 1))
                epaisseur_haut = 3 if motif_actuel != motif_haut else 1
                self.canvas.create_line(x_pixel, y_pixel, x_pixel + self.taille_case, y_pixel, width=epaisseur_haut)

                # Bordure de gauche : trait épais si le motif à gauche est différent
                motif_gauche = cases_motifs.get((x - 1, y))
                epaisseur_gauche = 3 if motif_actuel != motif_gauche else 1
                self.canvas.create_line(x_pixel, y_pixel, x_pixel, y_pixel + self.taille_case, width=epaisseur_gauche)

                # Bordure du bas : trait épais si on est sur la dernière ligne
                if y == hauteur - 1:
                    self.canvas.create_line(x_pixel, y_pixel + self.taille_case, x_pixel + self.taille_case, y_pixel + self.taille_case, width=3)
                    
                # Bordure de droite : trait épais si on est sur la dernière colonne
                if x == largeur - 1:
                    self.canvas.create_line(x_pixel + self.taille_case, y_pixel, x_pixel + self.taille_case, y_pixel + self.taille_case, width=3)

                # Valeur à afficher dans la case
                valeur = cases_valeurs.get((x, y), 0)
                
                if valeur > 0:
                    # Case avec un chiffre de départ
                    self.canvas.create_text(
                        x_pixel + self.taille_case / 2, 
                        y_pixel + self.taille_case / 2, 
                        text=str(valeur), 
                        font=("Arial", 16, "bold"),
                        fill="black"
                    )
                else:
                    # Case vide à remplir par le joueur
                    id_texte = self.canvas.create_text(
                        x_pixel + self.taille_case / 2, 
                        y_pixel + self.taille_case / 2, 
                        text="", 
                        font=("Arial", 16, "normal"),
                        fill="blue" 
                    )
                    # On garde l'identifiant pour modifier le texte plus tard
                    self.identifiants_textes[(x, y)] = id_texte

    def mettre_a_jour_case(self, x, y, nouvelle_valeur):
        # Met à jour l'affichage d'une case si elle existe
        if (x, y) in self.identifiants_textes:
            id_texte = self.identifiants_textes[(x, y)]
            texte_a_afficher = str(nouvelle_valeur) if nouvelle_valeur > 0 else ""
            self.canvas.itemconfig(id_texte, text=texte_a_afficher)