import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPainter, QPen, QFont, QAction
from PyQt6.QtCore import Qt, QRect

# Composant qui dessine uniquement la grille
class ZoneGrille(QWidget):
    
    def __init__(self, action_clic, action_clavier):
        super().__init__()
        
        # Indispensable pour ecouter le clavier
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.taille_case = 50 
        self.action_clic = action_clic 
        self.action_clavier = action_clavier 
        
        self.largeur = 0
        self.hauteur = 0
        self.cases_valeurs = {}
        self.cases_motifs = {}
        
        # Memoire de la case en surbrillance
        self.case_selectionnee = None

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
                # Active la surbrillance
                self.case_selectionnee = (colonne_x, ligne_y)
                self.update()
                
                # declenche le pop-up du collegue si on veut jouer a la souris
                self.action_clic(colonne_x, ligne_y)

    def keyPressEvent(self, event):
        # Saisie au clavier directement sur la case en surbrillance
        if self.case_selectionnee:
            x, y = self.case_selectionnee
            
            # Touche Supprimer pour effacer
            if event.key() == Qt.Key.Key_Backspace or event.key() == Qt.Key.Key_Delete:
                self.action_clavier(x, y, 0)
                
            # Touches 1 a 9 pour jouer
            elif Qt.Key.Key_1 <= event.key() <= Qt.Key.Key_9:
                chiffre_tape = event.key() - Qt.Key.Key_0
                self.action_clavier(x, y, chiffre_tape)

    def paintEvent(self, event):
        if self.largeur == 0 or self.hauteur == 0:
            return 

        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        for y in range(self.hauteur):
            for x in range(self.largeur):
                x_pixel = x * self.taille_case
                y_pixel = y * self.taille_case
                
                # Dessin de la surbrillance cyan
                if self.case_selectionnee == (x, y):
                    rect_case = QRect(x_pixel, y_pixel, self.taille_case, self.taille_case)
                    painter.fillRect(rect_case, Qt.GlobalColor.cyan)
                
                motif_actuel = self.cases_motifs.get((x, y))
                
                motif_haut = self.cases_motifs.get((x, y - 1))
                epaisseur = 3 if motif_actuel != motif_haut else 1
                painter.setPen(QPen(Qt.GlobalColor.black, epaisseur))
                painter.drawLine(x_pixel, y_pixel, x_pixel + self.taille_case, y_pixel)

                motif_gauche = self.cases_motifs.get((x - 1, y))
                epaisseur = 3 if motif_actuel != motif_gauche else 1
                painter.setPen(QPen(Qt.GlobalColor.black, epaisseur))
                painter.drawLine(x_pixel, y_pixel, x_pixel, y_pixel + self.taille_case)

                if y == self.hauteur - 1:
                    painter.setPen(QPen(Qt.GlobalColor.black, 3))
                    painter.drawLine(x_pixel, y_pixel + self.taille_case, x_pixel + self.taille_case, y_pixel + self.taille_case)
                    
                if x == self.largeur - 1:
                    painter.setPen(QPen(Qt.GlobalColor.black, 3))
                    painter.drawLine(x_pixel + self.taille_case, y_pixel, x_pixel + self.taille_case, y_pixel + self.taille_case)

                valeur = self.cases_valeurs.get((x, y), 0)
                if valeur > 0:
                    painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
                    painter.setPen(Qt.GlobalColor.black)
                    boite_texte = QRect(x_pixel, y_pixel, self.taille_case, self.taille_case)
                    painter.drawText(boite_texte, Qt.AlignmentFlag.AlignCenter, str(valeur))


# Fenetre principale
class VueNeonaure(QMainWindow):
    
    def __init__(self, action_clic, action_clavier=None):
        super().__init__()
        self.setWindowTitle("Jeu Neonaure")
        
        # Création d'un conteneur pour centrer la grille
        conteneur_principal = QWidget()
        layout_centre = QVBoxLayout(conteneur_principal)
        layout_centre.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        # On crée la grille et on l'ajoute dans notre layout centré
        self.zone_grille = ZoneGrille(action_clic, action_clavier)
        layout_centre.addWidget(self.zone_grille)
        
        # On dit à la fenêtre d'utiliser ce conteneur
        self.setCentralWidget(conteneur_principal)
          
        barre_menu = self.menuBar()
        
        menu_fichier = barre_menu.addMenu("Fichier")
        self.action_charger = QAction("Charger une grille", self)
        self.action_sauvegarder = QAction("Sauvegarder", self)
        menu_fichier.addAction(self.action_charger)
        menu_fichier.addAction(self.action_sauvegarder)
        
        menu_jeu = barre_menu.addMenu("Jeu")
        self.action_solution = QAction("Afficher la solution", self)
        menu_jeu.addAction(self.action_solution)
        
        self.barre_statut = self.statusBar()
        self.label_chrono = QLabel("Temps : 0 min 0 s")
        self.barre_statut.addPermanentWidget(self.label_chrono)

    def update_chrono(self, temps_str):
        self.label_chrono.setText(f"Temps : {temps_str}")

    def dessiner_grille(self, largeur, hauteur, cases_valeurs, cases_motifs):
        self.zone_grille.dessiner_grille(largeur, hauteur, cases_valeurs, cases_motifs)
        self.adjustSize()

    def mettre_a_jour_case(self, x, y, nouvelle_valeur):
        self.zone_grille.mettre_a_jour_case(x, y, nouvelle_valeur)