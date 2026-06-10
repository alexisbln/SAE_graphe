from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPainter, QPen, QFont, QAction, QColor
from PyQt6.QtCore import Qt, QRect


# Palette de couleurs pastel pour distinguer les motifs
COULEURS_MOTIFS = [
    QColor(255, 200, 200),  # rose
    QColor(200, 220, 255),  # bleu
    QColor(200, 255, 200),  # vert
    QColor(255, 240, 180),  # jaune
    QColor(230, 200, 255),  # violet
    QColor(255, 220, 180),  # orange
    QColor(180, 255, 240),  # turquoise
    QColor(255, 200, 230),  # fuchsia
    QColor(220, 255, 180),  # lime
    QColor(200, 240, 255),  # cyan clair
]


# Composant qui dessine uniquement la grille
class ZoneGrille(QWidget):

    def __init__(self, action_clic, action_clavier):
        """
        Initialise le widget de la grille.

        :param action_clic: Fonction appelée lors d'un clic sur une case (x, y).
        :param action_clavier: Fonction appelée lors d'une saisie clavier (x, y, valeur).
        """
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

        # Dictionnaire associant chaque nom de motif à une couleur pastel
        self.couleurs_par_motif = {}

    def dessiner_grille(self, largeur, hauteur, cases_valeurs, cases_motifs):
        """
        Met à jour les données de la grille et déclenche un redessin.

        :param largeur: Nombre de colonnes de la grille.
        :param hauteur: Nombre de lignes de la grille.
        :param cases_valeurs: Dictionnaire {(x, y): valeur} des cases.
        :param cases_motifs: Dictionnaire {(x, y): nom_motif} des cases.
        """
        self.largeur = largeur
        self.hauteur = hauteur
        self.cases_valeurs = cases_valeurs
        self.cases_motifs = cases_motifs
        self._generer_couleurs_motifs()
        self.setFixedSize(largeur * self.taille_case, hauteur * self.taille_case)
        self.update()

    def _generer_couleurs_motifs(self):
        """
        Associe une couleur pastel unique à chaque nom de motif présent dans la grille.
        Les couleurs sont choisies dans la palette COULEURS_MOTIFS de façon cyclique.
        """
        noms_motifs = set(self.cases_motifs.values())
        self.couleurs_par_motif = {}
        for i, nom in enumerate(sorted(noms_motifs)):
            self.couleurs_par_motif[nom] = COULEURS_MOTIFS[i % len(COULEURS_MOTIFS)]

    def mettre_a_jour_case(self, x, y, nouvelle_valeur):
        """
        Met à jour la valeur d'une case et redessine le widget.

        :param x: Colonne de la case.
        :param y: Ligne de la case.
        :param nouvelle_valeur: Nouvelle valeur à afficher dans la case.
        """
        self.cases_valeurs[(x, y)] = nouvelle_valeur
        self.update()

    def mousePressEvent(self, event):
        """
        Gère le clic gauche sur le widget : sélectionne la case cliquée
        et appelle le gestionnaire de clic du contrôleur.

        :param event: Événement souris PyQt6.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            colonne_x = event.pos().x() // self.taille_case
            ligne_y = event.pos().y() // self.taille_case

            if 0 <= colonne_x < self.largeur and 0 <= ligne_y < self.hauteur:
                # Active la surbrillance
                self.case_selectionnee = (colonne_x, ligne_y)
                self.update()

                # Appelle le gestionnaire du controleur
                self.action_clic(colonne_x, ligne_y)

    def keyPressEvent(self, event):
        """
        Gère la saisie clavier sur la case sélectionnée.
        Les touches 1-9 placent un chiffre, Backspace/Delete effacent la case.

        :param event: Événement clavier PyQt6.
        """
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
        """
        Redessine entièrement la grille : couleurs de fond des motifs,
        surbrillance de la case sélectionnée, bordures et valeurs des cases.

        :param event: Événement de dessin PyQt6.
        """
        if self.largeur == 0 or self.hauteur == 0:
            return

        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        for y in range(self.hauteur):
            for x in range(self.largeur):
                x_pixel = x * self.taille_case
                y_pixel = y * self.taille_case
                rect_case = QRect(x_pixel, y_pixel, self.taille_case, self.taille_case)

                # Couleur de fond du motif
                nom_motif = self.cases_motifs.get((x, y))
                if nom_motif and nom_motif in self.couleurs_par_motif:
                    painter.fillRect(rect_case, self.couleurs_par_motif[nom_motif])

                # Surbrillance cyan par-dessus la couleur du motif
                if self.case_selectionnee == (x, y):
                    painter.fillRect(rect_case, Qt.GlobalColor.cyan)

                motif_actuel = self.cases_motifs.get((x, y))

                # Bordure haute
                motif_haut = self.cases_motifs.get((x, y - 1))
                epaisseur = 3 if motif_actuel != motif_haut else 1
                painter.setPen(QPen(Qt.GlobalColor.black, epaisseur))
                painter.drawLine(x_pixel, y_pixel, x_pixel + self.taille_case, y_pixel)

                # Bordure gauche
                motif_gauche = self.cases_motifs.get((x - 1, y))
                epaisseur = 3 if motif_actuel != motif_gauche else 1
                painter.setPen(QPen(Qt.GlobalColor.black, epaisseur))
                painter.drawLine(x_pixel, y_pixel, x_pixel, y_pixel + self.taille_case)

                # Bordure basse (derniere ligne)
                if y == self.hauteur - 1:
                    painter.setPen(QPen(Qt.GlobalColor.black, 3))
                    painter.drawLine(x_pixel, y_pixel + self.taille_case,
                                     x_pixel + self.taille_case, y_pixel + self.taille_case)

                # Bordure droite (derniere colonne)
                if x == self.largeur - 1:
                    painter.setPen(QPen(Qt.GlobalColor.black, 3))
                    painter.drawLine(x_pixel + self.taille_case, y_pixel,
                                     x_pixel + self.taille_case, y_pixel + self.taille_case)

                # Affichage de la valeur
                valeur = self.cases_valeurs.get((x, y), 0)
                if valeur > 0:
                    painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
                    painter.setPen(Qt.GlobalColor.black)
                    painter.drawText(rect_case, Qt.AlignmentFlag.AlignCenter, str(valeur))


# Fenetre principale
class VueNeonaure(QMainWindow):

    def __init__(self, action_clic, action_clavier=None):
        """
        Initialise la fenêtre principale avec le menu, la grille et la barre de statut.

        :param action_clic: Fonction transmise à ZoneGrille pour les clics souris.
        :param action_clavier: Fonction transmise à ZoneGrille pour la saisie clavier.
        """
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
        """
        Met à jour l'affichage du chronomètre dans la barre de statut.

        :param temps_str: Chaîne de caractères à afficher (ex: '2 min 35 s').
        """
        self.label_chrono.setText(f"Temps : {temps_str}")

    def dessiner_grille(self, largeur, hauteur, cases_valeurs, cases_motifs):
        """
        Transmet les données de la grille au widget ZoneGrille et redimensionne la fenêtre.

        :param largeur: Nombre de colonnes.
        :param hauteur: Nombre de lignes.
        :param cases_valeurs: Dictionnaire {(x, y): valeur}.
        :param cases_motifs: Dictionnaire {(x, y): nom_motif}.
        """
        self.zone_grille.dessiner_grille(largeur, hauteur, cases_valeurs, cases_motifs)
        self.adjustSize()

    def mettre_a_jour_case(self, x, y, nouvelle_valeur):
        """
        Met à jour la valeur d'une case affichée dans la grille.

        :param x: Colonne de la case.
        :param y: Ligne de la case.
        :param nouvelle_valeur: Valeur à afficher.
        """
        self.zone_grille.mettre_a_jour_case(x, y, nouvelle_valeur)