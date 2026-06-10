import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QFont
from PyQt6.QtCore import Qt, QRect

class VueNeonaure(QWidget):
    
    def __init__(self, action_clic):
        super().__init__()
        
        # Taille d'une case
        self.taille_case = 50 
        
        # Fonction du controleur pour gerer le clic
        self.action_clic = action_clic 
        
        # Variables de la grille
        self.largeur = 0
        self.hauteur = 0
        self.cases_valeurs = {}
        self.cases_motifs = {}

    def dessiner_grille(self, largeur, hauteur, cases_valeurs, cases_motifs):
        # On recupere les donnees
        self.largeur = largeur
        self.hauteur = hauteur
        self.cases_valeurs = cases_valeurs
        self.cases_motifs = cases_motifs

        # On fixe la taille de la fenetre
        self.setFixedSize(largeur * self.taille_case, hauteur * self.taille_case)
        
        # On force la mise a jour de l'affichage
        self.update()

    def mettre_a_jour_case(self, x, y, nouvelle_valeur):
        # On change la valeur dans notre memoire
        self.cases_valeurs[(x, y)] = nouvelle_valeur
        # On rafraichit l'ecran
        self.update()

    def mousePressEvent(self, event):
        # On reagit au clic gauche
        if event.button() == Qt.MouseButton.LeftButton:
            
            # On calcule ou le joueur a clique
            colonne_x = event.pos().x() // self.taille_case
            ligne_y = event.pos().y() // self.taille_case
            
            # On verifie que le clic est bien dans la grille
            if 0 <= colonne_x < self.largeur and 0 <= ligne_y < self.hauteur:
                # On previent le controleur
                self.action_clic(colonne_x, ligne_y)

    def paintEvent(self, event):
        # C'est ici qu'on dessine tout
        if self.largeur == 0 or self.hauteur == 0:
            return 

        painter = QPainter(self)
        
        # Fond blanc
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        # On boucle sur toutes les cases
        for y in range(self.hauteur):
            for x in range(self.largeur):
                
                # Position sur l'ecran
                x_pixel = x * self.taille_case
                y_pixel = y * self.taille_case
                
                motif_actuel = self.cases_motifs.get((x, y))
                
                # Bordure du haut
                motif_haut = self.cases_motifs.get((x, y - 1))
                epaisseur = 3 if motif_actuel != motif_haut else 1
                painter.setPen(QPen(Qt.GlobalColor.black, epaisseur))
                painter.drawLine(x_pixel, y_pixel, x_pixel + self.taille_case, y_pixel)

                # Bordure de gauche
                motif_gauche = self.cases_motifs.get((x - 1, y))
                epaisseur = 3 if motif_actuel != motif_gauche else 1
                painter.setPen(QPen(Qt.GlobalColor.black, epaisseur))
                painter.drawLine(x_pixel, y_pixel, x_pixel, y_pixel + self.taille_case)

                # On ferme la grille en bas
                if y == self.hauteur - 1:
                    painter.setPen(QPen(Qt.GlobalColor.black, 3))
                    painter.drawLine(x_pixel, y_pixel + self.taille_case, x_pixel + self.taille_case, y_pixel + self.taille_case)
                    
                # On ferme la grille a droite
                if x == self.largeur - 1:
                    painter.setPen(QPen(Qt.GlobalColor.black, 3))
                    painter.drawLine(x_pixel + self.taille_case, y_pixel, x_pixel + self.taille_case, y_pixel + self.taille_case)

                # Affichage des chiffres
                valeur = self.cases_valeurs.get((x, y), 0)
                
                if valeur > 0:
                    # Police du texte
                    painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
                    painter.setPen(Qt.GlobalColor.black)
                    
                    # On centre le chiffre dans la case
                    boite_texte = QRect(x_pixel, y_pixel, self.taille_case, self.taille_case)
                    painter.drawText(boite_texte, Qt.AlignmentFlag.AlignCenter, str(valeur))


# Test rapide du fichier
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    def clic_bidon(x, y):
        print(f"Clic sur {x}, {y}")
        
    ma_vue = VueNeonaure(clic_bidon)
    ma_vue.setWindowTitle("Test")
    
    fausses_valeurs = {(0, 0): 5, (2, 2): 1} 
    faux_motifs = {
        (0, 0): 1, (1, 0): 1, (2, 0): 1,  
        (0, 1): 2, (1, 1): 2, (2, 1): 2,  
        (0, 2): 2, (1, 2): 2, (2, 2): 2
    }
    
    ma_vue.dessiner_grille(3, 3, fausses_valeurs, faux_motifs)
    ma_vue.show()
    sys.exit(app.exec())