import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt6.QtGui import QPainter, QPen, QFont, QAction
from PyQt6.QtCore import Qt, QRect


# Composant qui dessine uniquement la grille
class ZoneGrille(QWidget):
    
    def __init__(self, action_clic):
        super().__init__()
        
        # Taille d'une case
        self.taille_case = 50 
        self.action_clic = action_clic 
        
        # Variables de la grille
        self.largeur = 0
        self.hauteur = 0
        self.cases_valeurs = {}
        self.cases_motifs = {}

    def dessiner_grille(self, largeur, hauteur, cases_valeurs, cases_motifs):
        self.largeur = largeur
        self.hauteur = hauteur
        self.cases_valeurs = cases_valeurs
        self.cases_motifs = cases_motifs

        self.setFixedSize(largeur * self.taille_case, hauteur * self.taille_case)
        self.update()

    def mettre_a_jour_case(self, x, y, nouvelle_valeur):
        self.cases_valeurs[(x, y)] = nouvelle_valeur
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            colonne_x = event.pos().x() // self.taille_case
            ligne_y = event.pos().y() // self.taille_case
            
            if 0 <= colonne_x < self.largeur and 0 <= ligne_y < self.hauteur:
                self.action_clic(colonne_x, ligne_y)

    def paintEvent(self, event):
        if self.largeur == 0 or self.hauteur == 0:
            return 

        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        # On boucle sur toutes les cases
        for y in range(self.hauteur):
            for x in range(self.largeur):
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
                    painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
                    painter.setPen(Qt.GlobalColor.black)
                    boite_texte = QRect(x_pixel, y_pixel, self.taille_case, self.taille_case)
                    painter.drawText(boite_texte, Qt.AlignmentFlag.AlignCenter, str(valeur))


# Fenetre principale complete avec menus et chrono
class VueNeonaure(QMainWindow):
    
    def __init__(self, action_clic):
        super().__init__()
        self.setWindowTitle("Jeu Neonaure")
        
        # On place la grille au centre de la fenetre
        self.zone_grille = ZoneGrille(action_clic)
        self.setCentralWidget(self.zone_grille)
        
        # Creation de la barre de menu en haut
        barre_menu = self.menuBar()
        
        # Menu Fichier
        menu_fichier = barre_menu.addMenu("Fichier")
        self.action_charger = QAction("Charger une grille", self)
        self.action_sauvegarder = QAction("Sauvegarder", self)
        menu_fichier.addAction(self.action_charger)
        menu_fichier.addAction(self.action_sauvegarder)
        
        # Menu Jeu
        menu_jeu = barre_menu.addMenu("Jeu")
        self.action_solution = QAction("Afficher la solution", self)
        menu_jeu.addAction(self.action_solution)
        
        # Creation de la barre de statut en bas pour le chrono
        self.barre_statut = self.statusBar()
        self.label_chrono = QLabel("Temps : 00:00")
        self.barre_statut.addPermanentWidget(self.label_chrono)

    # Fonction appelee par le controleur pour changer le texte du chrono
    def update_chrono(self, temps_str):
        self.label_chrono.setText(f"Temps : {temps_str}")

    # On fait le lien vers la zone de grille pour que le controleur n'ait rien a changer
    def dessiner_grille(self, largeur, hauteur, cases_valeurs, cases_motifs):
        self.zone_grille.dessiner_grille(largeur, hauteur, cases_valeurs, cases_motifs)
        # On adapte la taille de la fenetre a la taille de la grille
        self.adjustSize()

    def mettre_a_jour_case(self, x, y, nouvelle_valeur):
        self.zone_grille.mettre_a_jour_case(x, y, nouvelle_valeur)