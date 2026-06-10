import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt6.QtGui import QPainter, QPen, QFont, QAction
from PyQt6.QtCore import Qt, QRect


# Composant qui dessine uniquement la grille
# Composant qui dessine uniquement la grille
class ZoneGrille(QWidget):
    
    def __init__(self, action_clic, action_clavier):
        super().__init__()
        
        # Indispensable pour que le composant puisse écouter le clavier
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        self.taille_case = 50 
        self.action_clic = action_clic 
        self.action_clavier = action_clavier # NOUVEAU : La fonction pour envoyer le chiffre
        
        self.largeur = 0
        self.hauteur = 0
        self.cases_valeurs = {}
        self.cases_motifs = {}
        
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
                self.case_selectionnee = (colonne_x, ligne_y)
                self.update()
                self.action_clic(colonne_x, ligne_y)

    # La fonction s'active quand on tape sur le clavier
    def keyPressEvent(self, event):
        # On verifie qu'une case est bien selectionnee
        if self.case_selectionnee:
            x, y = self.case_selectionnee
            
            # Si on appuie sur la touche Supprimer ou Retour Arriere -> on efface (envoie 0)
            if event.key() == Qt.Key.Key_Backspace or event.key() == Qt.Key.Key_Delete:
                self.action_clavier(x, y, 0)
                
            # Si on tape un chiffre de 1 a 9 sur le clavier
            elif Qt.Key.Key_1 <= event.key() <= Qt.Key.Key_9:
                # On convertit le code de la touche en vrai chiffre mathématique
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

# Fenetre principale complete avec menus et chrono
class VueNeonaure(QMainWindow):
    
    # On recoit maintenant les deux fonctions
    def __init__(self, action_clic, action_clavier):
        super().__init__()
        self.setWindowTitle("Jeu Neonaure")
        
        # On les transmet a la zone de dessin
        self.zone_grille = ZoneGrille(action_clic, action_clavier)
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


# Test rapide du fichier
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    def clic_bidon(x, y):
        print(f"Clic sur {x}, {y}")

    # Nouvelle fonction de test pour le clavier
    def clavier_bidon(x, y, chiffre):
        print(f"Clavier sur {x}, {y} : chiffre {chiffre}")
        
    # On donne bien les DEUX fonctions a la vue
    ma_vue = VueNeonaure(clic_bidon, clavier_bidon)
    
    fausses_valeurs = {(0, 0): 5, (2, 2): 1} 
    faux_motifs = {
        (0, 0): 1, (1, 0): 1, (2, 0): 1,  
        (0, 1): 2, (1, 1): 2, (2, 1): 2,  
        (0, 2): 2, (1, 2): 2, (2, 2): 2
    }
    
    ma_vue.dessiner_grille(3, 3, fausses_valeurs, faux_motifs)
    ma_vue.update_chrono("01:45")
    ma_vue.show()
    sys.exit(app.exec())