from PyQt6.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QPushButton, QTableWidget, QTableWidgetItem, QCheckBox, QComboBox)
from PyQt6.QtGui import QPainter, QPen, QFont, QAction, QColor, QCursor
from PyQt6.QtCore import Qt, QRect

COULEURS_MOTIFS = [
    QColor(255, 200, 200), QColor(200, 220, 255), QColor(200, 255, 200),
    QColor(255, 240, 180), QColor(230, 200, 255), QColor(255, 220, 180),
    QColor(180, 255, 240), QColor(255, 200, 230), QColor(220, 255, 180),
    QColor(200, 240, 255)
]

class ZoneGrille(QWidget):
    """Widget personnalisé responsable du rendu visuel de la grille de jeu."""
    
    def __init__(self, action_clic, action_clavier):
        """Initialise le widget graphique de la grille."""
        super().__init__()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.taille_case = 50
        self.action_clic = action_clic
        self.action_clavier = action_clavier
        self.largeur = 0
        self.hauteur = 0
        self.cases_valeurs = {}
        self.cases_motifs = {}
        self.cases_initiales = set()
        self.case_selectionnee = None
        self.couleurs_par_motif = {}

    def dessiner_grille(self, largeur, hauteur, cases_valeurs, cases_motifs, cases_initiales):
        """Met à jour les données de la grille et déclenche un redessin visuel."""
        self.largeur = largeur
        self.hauteur = hauteur
        self.cases_valeurs = cases_valeurs
        self.cases_motifs = cases_motifs
        self.cases_initiales = cases_initiales
        self._generer_couleurs_motifs()
        self.setFixedSize(largeur * self.taille_case, hauteur * self.taille_case)
        self.update()

    def _generer_couleurs_motifs(self):
        """Associe une couleur unique pastel à chaque motif sans chevauchement avec ses voisins."""
        self.couleurs_par_motif = {}
        noms_motifs = set(self.cases_motifs.values())
        
        adjacences = {nom: set() for nom in noms_motifs}
        for x in range(self.largeur):
            for y in range(self.hauteur):
                motif_actuel = self.cases_motifs.get((x, y))
                if not motif_actuel: continue
                
                voisins = [(x+1, y), (x, y+1)]
                for vx, vy in voisins:
                    motif_voisin = self.cases_motifs.get((vx, vy))
                    if motif_voisin and motif_voisin != motif_actuel:
                        adjacences[motif_actuel].add(motif_voisin)
                        adjacences[motif_voisin].add(motif_actuel)

        for nom in sorted(noms_motifs):
            couleurs_interdites = [self.couleurs_par_motif.get(v) for v in adjacences[nom]]
            for couleur in COULEURS_MOTIFS:
                if couleur not in couleurs_interdites:
                    self.couleurs_par_motif[nom] = couleur
                    break
            if nom not in self.couleurs_par_motif:
                self.couleurs_par_motif[nom] = COULEURS_MOTIFS[0]

    def mettre_a_jour_case(self, x, y, nouvelle_valeur):
        """Met à jour la valeur affichée dans une case spécifique."""
        self.cases_valeurs[(x, y)] = nouvelle_valeur
        self.update()

    def mousePressEvent(self, event):
        """Gère la sélection d'une case au clic gauche de la souris."""
        if event.button() == Qt.MouseButton.LeftButton:
            colonne_x = event.pos().x() // self.taille_case
            ligne_y = event.pos().y() // self.taille_case

            if 0 <= colonne_x < self.largeur and 0 <= ligne_y < self.hauteur:
                self.case_selectionnee = (colonne_x, ligne_y)
                self.update()
                self.action_clic(colonne_x, ligne_y)

    def keyPressEvent(self, event):
        """Gère la modification d'une case via le pavé numérique du clavier."""
        if self.case_selectionnee:
            x, y = self.case_selectionnee
            if event.key() == Qt.Key.Key_Backspace or event.key() == Qt.Key.Key_Delete:
                self.action_clavier(x, y, 0)
            elif Qt.Key.Key_1 <= event.key() <= Qt.Key.Key_9:
                chiffre_tape = event.key() - Qt.Key.Key_0
                self.action_clavier(x, y, chiffre_tape)

    def paintEvent(self, event):
        """Dessine les cases, les motifs, la surbrillance et les valeurs (noires ou bleues)."""
        if self.largeur == 0 or self.hauteur == 0:
            return

        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        for y in range(self.hauteur):
            for x in range(self.largeur):
                x_pixel = x * self.taille_case
                y_pixel = y * self.taille_case
                rect_case = QRect(x_pixel, y_pixel, self.taille_case, self.taille_case)

                nom_motif = self.cases_motifs.get((x, y))
                if nom_motif and nom_motif in self.couleurs_par_motif:
                    painter.fillRect(rect_case, self.couleurs_par_motif[nom_motif])

                if self.case_selectionnee == (x, y):
                    painter.fillRect(rect_case, Qt.GlobalColor.cyan)

                motif_actuel = self.cases_motifs.get((x, y))

                epaisseur_haut = 3 if motif_actuel != self.cases_motifs.get((x, y - 1)) else 1
                painter.setPen(QPen(Qt.GlobalColor.black, epaisseur_haut))
                painter.drawLine(x_pixel, y_pixel, x_pixel + self.taille_case, y_pixel)

                epaisseur_gauche = 3 if motif_actuel != self.cases_motifs.get((x - 1, y)) else 1
                painter.setPen(QPen(Qt.GlobalColor.black, epaisseur_gauche))
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
                    
                    if hasattr(self, 'cases_initiales') and (x, y) in self.cases_initiales:
                        painter.setPen(Qt.GlobalColor.black)
                    else:
                        painter.setPen(Qt.GlobalColor.blue)
                        
                    painter.drawText(rect_case, Qt.AlignmentFlag.AlignCenter, str(valeur))


class VueNeonaure(QMainWindow):
    """Fenêtre principale de l'application gérant les menus et l'interface utilisateur."""
    
    def __init__(self, action_clic, action_clavier=None):
        """Initialise la fenêtre principale et gère la navigation entre les menus via un QStackedWidget."""
        super().__init__()
        self.setWindowTitle("Jeu Neonaure")
        self.resize(700, 600)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.page_accueil = QWidget()
        self.page_jeu = QWidget()
        self.page_parametres = QWidget()
        self.page_scores = QWidget()

        self.stacked_widget.addWidget(self.page_accueil)
        self.stacked_widget.addWidget(self.page_jeu)
        self.stacked_widget.addWidget(self.page_parametres)
        self.stacked_widget.addWidget(self.page_scores)

        self._creer_page_accueil()
        self._creer_page_jeu(action_clic, action_clavier)
        self._creer_page_parametres()
        self._creer_page_scores()

        self._creer_menu()
        self.stacked_widget.setCurrentWidget(self.page_accueil)

    def _creer_page_accueil(self):
        """Construit l'interface du tableau de bord (Dashboard) principal."""
        layout = QVBoxLayout(self.page_accueil)
        
        titre = QLabel("NÉONAURE")
        titre.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titre)

        self.btn_jouer = QPushButton("Jouer")
        self.btn_charger_accueil = QPushButton("Charger une partie")
        self.btn_scores = QPushButton("Meilleurs Temps")
        self.btn_parametres = QPushButton("Paramètres")

        for btn in [self.btn_jouer, self.btn_charger_accueil, self.btn_scores, self.btn_parametres]:
            btn.setFixedSize(200, 40)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        footer = QLabel('<a href="https://github.com/alexisbln/SAE_graphe">Fait par Alexis Blouin, Théo Duriez, François Goddefroy</a>')
        footer.setOpenExternalLinks(True)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

    def _creer_page_jeu(self, action_clic, action_clavier):
        """Construit l'interface de la grille de jeu avec le bouton Retour."""
        layout = QVBoxLayout(self.page_jeu)
        
        self.btn_retour_accueil_jeu = QPushButton("Retour au Menu Principal")
        self.btn_retour_accueil_jeu.setFixedSize(250, 40)
        self.btn_retour_accueil_jeu.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_retour_accueil_jeu.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_retour_accueil_jeu, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addSpacing(20)
        
        conteneur_grille = QHBoxLayout()
        self.zone_grille = ZoneGrille(action_clic, action_clavier)
        conteneur_grille.addStretch()
        conteneur_grille.addWidget(self.zone_grille)
        conteneur_grille.addStretch()
        
        layout.addLayout(conteneur_grille)
        layout.addStretch()

    def _creer_page_parametres(self):
        """Construit l'interface des paramètres (activation/désactivation du Pop-up et choix difficulté)."""
        layout = QVBoxLayout(self.page_parametres)
        
        titre = QLabel("Paramètres")
        titre.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(titre, alignment=Qt.AlignmentFlag.AlignCenter)

        self.check_popup = QCheckBox("Activer la Saisie par Pop-up au clic (Désactiver pour jouer 100% clavier)")
        self.check_popup.setChecked(True)
        layout.addWidget(self.check_popup, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(30)

        label_diff = QLabel("Niveau de difficulté par défaut :")
        label_diff.setFont(QFont("Arial", 12))
        layout.addWidget(label_diff, alignment=Qt.AlignmentFlag.AlignCenter)

        self.combo_difficulte = QComboBox()
        self.combo_difficulte.addItems(["Facile", "Normal", "Difficile"])
        self.combo_difficulte.setFixedSize(200, 35)
        layout.addWidget(self.combo_difficulte, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        self.btn_retour_param = QPushButton("Retour au Menu")
        self.btn_retour_param.setFixedSize(200, 40)
        layout.addWidget(self.btn_retour_param, alignment=Qt.AlignmentFlag.AlignCenter)

    def _creer_page_scores(self):
        """Construit l'interface du classement des meilleurs temps."""
        layout = QVBoxLayout(self.page_scores)
        titre = QLabel("Meilleurs Temps")
        titre.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        layout.addWidget(titre, alignment=Qt.AlignmentFlag.AlignCenter)

        self.table_scores = QTableWidget(0, 3)
        self.table_scores.setHorizontalHeaderLabels(["Pseudo", "Temps (s)", "Difficulté"])
        self.table_scores.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table_scores)

        self.btn_retour_scores = QPushButton("Retour au Menu")
        layout.addWidget(self.btn_retour_scores, alignment=Qt.AlignmentFlag.AlignCenter)

    def _creer_menu(self):
        """Génère la barre de menu supérieure (visible uniquement en jeu)."""
        self.barre_menu = self.menuBar()

        menu_fichier = self.barre_menu.addMenu("Fichier")
        self.action_accueil = QAction("Menu Principal", self)
        self.action_charger = QAction("Charger une grille", self)
        self.action_sauvegarder = QAction("Sauvegarder", self)
        menu_fichier.addActions([self.action_accueil, self.action_charger, self.action_sauvegarder])

        menu_jeu = self.barre_menu.addMenu("Jeu")
        self.action_solution = QAction("Afficher la solution", self)
        self.action_indice = QAction("Donner un indice", self) 
        self.action_verifier = QAction("Vérifier et bloquer la case", self)
        menu_jeu.addActions([self.action_solution, self.action_indice, self.action_verifier])

        menu_difficulte = self.barre_menu.addMenu("Difficulté")
        self.action_diff_facile = QAction("Facile", self, checkable=True)
        self.action_diff_normal = QAction("Normal", self, checkable=True)
        self.action_diff_difficile = QAction("Difficile", self, checkable=True)
        self.action_diff_facile.setChecked(True) 
        menu_difficulte.addActions([self.action_diff_facile, self.action_diff_normal, self.action_diff_difficile])

        menu_aide = self.barre_menu.addMenu("Aide")
        self.action_aide = QAction("Règles du jeu", self)
        menu_aide.addAction(self.action_aide)

        self.barre_statut = self.statusBar()
        self.label_chrono = QLabel("Temps : 0 min 0 s")
        self.barre_statut.addPermanentWidget(self.label_chrono)

    def update_chrono(self, temps_str):
        """Met à jour l'affichage texte du chronomètre en bas de l'écran."""
        self.label_chrono.setText(f"Temps : {temps_str}")

    def dessiner_grille(self, largeur, hauteur, cases_valeurs, cases_motifs, cases_initiales):
        """Transmet les données du modèle à la zone de grille pour l'affichage."""
        self.zone_grille.dessiner_grille(largeur, hauteur, cases_valeurs, cases_motifs, cases_initiales)

    def mettre_a_jour_case(self, x, y, nouvelle_valeur):
        """Transmet une modification locale de case à l'interface."""
        self.zone_grille.mettre_a_jour_case(x, y, nouvelle_valeur)