from PyQt6.QtWidgets import QMessageBox, QFileDialog, QInputDialog, QTableWidgetItem
from PyQt6.QtGui import QKeySequence, QShortcut, QActionGroup, QPixmap
from PyQt6.QtCore import QTimer, Qt
import random
import csv
import os

class Controleur :
    """Classe faisant le lien entre la vue et le modèle, et gérant la logique événementielle."""
    
    def __init__(self, modele, vue):
        """Initialise le contrôleur, lie les pages du dashboard et gère la logique principale."""
        self.modele = modele
        self.vue = vue
        self.temps_ecoule = 0
        self.premier_coup_joue = False
        self.niveau_difficulte = "Facile"
        self.partie_modifiee = False
        self.indices_restants = 0
        self.popup_active = True
        self.grille_solution = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.mettre_a_jour_temps)

        if self.vue and self.modele :
            self.connecter_signaux()
            self.configurer_raccourcis()
            self.afficher_accueil()

    def initialiser_etat_boutons(self):
        """Grise les boutons de jeu tant qu'aucune grille n'est chargée."""
        self.vue.action_sauvegarder.setEnabled(False)
        self.vue.action_solution.setEnabled(False)
        self.vue.action_indice.setEnabled(False)

    def afficher_accueil(self):
        """Arrête le temps, affiche le Dashboard principal et cache la barre d'outils du jeu."""
        self.arreter_chrono()
        self.vue.menuBar().setVisible(False)
        self.vue.barre_statut.setVisible(False)
        self.vue.stacked_widget.setCurrentWidget(self.vue.page_accueil)

    def afficher_jeu(self):
        """Affiche l'écran de grille et réactive les barres de menu et de statut."""
        self.vue.menuBar().setVisible(True)
        self.vue.barre_statut.setVisible(True)
        self.vue.stacked_widget.setCurrentWidget(self.vue.page_jeu)

    def afficher_parametres(self):
        """Affiche l'écran des options (Pop-up On/Off et difficulté)."""
        self.vue.stacked_widget.setCurrentWidget(self.vue.page_parametres)

    def afficher_scores(self):
        """Lit le fichier CSV et construit le tableau des meilleurs temps."""
        self.vue.table_scores.setRowCount(0)
        if os.path.exists("scores.csv"):
            with open("scores.csv", mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                en_tetes = next(reader, None)
                for row_data in reader:
                    row = self.vue.table_scores.rowCount()
                    self.vue.table_scores.insertRow(row)
                    for column, data in enumerate(row_data):
                        self.vue.table_scores.setItem(row, column, QTableWidgetItem(data))
        self.vue.stacked_widget.setCurrentWidget(self.vue.page_scores)

    def gerer_option_popup(self, etat):
        """Active ou désactive la fenêtre de saisie selon la case cochée dans les paramètres."""
        self.popup_active = (etat != 0)

    def demarrer_chrono(self):
        """Lance le décompte du temps de jeu."""
        self.temps_ecoule = 0
        self.timer.start(1000)
    
    def arreter_chrono(self):
        """Stoppe le chronomètre."""
        self.timer.stop()
    
    def mettre_a_jour_temps(self):
        """Calcule les minutes et secondes écoulées pour la barre de statut."""
        self.temps_ecoule += 1
        minutes = self.temps_ecoule // 60
        secondes = self.temps_ecoule % 60
        self.vue.update_chrono(f"{minutes} min {secondes} s")

    def connecter_signaux(self):
        """Relie tous les boutons du Dashboard et du Menu du jeu à leurs fonctions algorithmiques."""
        self.vue.btn_jouer.clicked.connect(self.lancer_jeu_aleatoire)
        self.vue.btn_charger_accueil.clicked.connect(self.charger_partie)
        self.vue.btn_scores.clicked.connect(self.afficher_scores)
        self.vue.btn_parametres.clicked.connect(self.afficher_parametres)

        self.vue.btn_retour_scores.clicked.connect(self.afficher_accueil)
        self.vue.btn_retour_param.clicked.connect(self.afficher_accueil)
        self.vue.btn_retour_accueil_jeu.clicked.connect(self.afficher_accueil)
        
        self.vue.check_popup.stateChanged.connect(self.gerer_option_popup)
        self.vue.combo_difficulte.currentTextChanged.connect(lambda texte: self.changer_difficulte(texte, afficher_popup=False))

        self.vue.action_accueil.triggered.connect(self.afficher_accueil)
        self.vue.action_charger.triggered.connect(self.charger_partie)
        self.vue.action_sauvegarder.triggered.connect(self.sauvegarder_partie)
        self.vue.action_solution.triggered.connect(self.resoudre_grille)
        self.vue.action_aide.triggered.connect(self.afficher_regles)
        self.vue.closeEvent = self.gerer_fermeture

        self.vue.action_indice.triggered.connect(self.donner_indice)
        self.vue.action_verifier.triggered.connect(self.verifier_et_bloquer_case)
    
        self.groupe_difficulte = QActionGroup(self.vue)
        self.groupe_difficulte.addAction(self.vue.action_diff_facile)
        self.groupe_difficulte.addAction(self.vue.action_diff_normal)
        self.groupe_difficulte.addAction(self.vue.action_diff_difficile)
        
        self.vue.action_diff_facile.triggered.connect(lambda: self.changer_difficulte("Facile", afficher_popup=True))
        self.vue.action_diff_normal.triggered.connect(lambda: self.changer_difficulte("Normal", afficher_popup=True))
        self.vue.action_diff_difficile.triggered.connect(lambda: self.changer_difficulte("Difficile", afficher_popup=True))

    def configurer_raccourcis(self):
        """Configure Ctrl+S, Ctrl+O, V et Ctrl+I pour le confort ergonomique."""
        raccourci_sauvegarder = QShortcut(QKeySequence("Ctrl+S"), self.vue)
        raccourci_sauvegarder.activated.connect(self.sauvegarder_partie)

        raccourci_charger = QShortcut(QKeySequence("Ctrl+O"), self.vue)
        raccourci_charger.activated.connect(self.charger_partie)

        raccourci_verifier = QShortcut(QKeySequence("V"), self.vue)
        raccourci_verifier.activated.connect(self.verifier_et_bloquer_case)
        
        
        raccourci_indice = QShortcut(QKeySequence("Ctrl+I"), self.vue)
        raccourci_indice.activated.connect(self.donner_indice)

    def gerer_modification_case(self, ligne, colonne, nouvelle_valeur):
        """Vérifie le coup, l'applique, et lance la procédure de victoire si la grille est pleine."""
        if nouvelle_valeur == 0:
            est_valide = True
        else:
            est_valide = self.modele.est_coup_valide(ligne, colonne, nouvelle_valeur)

        if est_valide :
            self.modele.set_valeur(ligne, colonne, nouvelle_valeur)
            self.partie_modifiee = True
            self.vue.mettre_a_jour_case(ligne, colonne, nouvelle_valeur)
            
            if nouvelle_valeur != 0 and not self.premier_coup_joue:
                self.premier_coup_joue = True
                self.demarrer_chrono()

            if self.modele.verifier_victoire():
                self.arreter_chrono()
                pseudo, ok = QInputDialog.getText(self.vue, "Victoire !", f"Bravo ! Temps: {self.temps_ecoule}s. Entrez votre pseudo :")
                if ok and pseudo:
                    self.sauvegarder_score(pseudo, self.temps_ecoule, self.niveau_difficulte)
                self.partie_modifiee = False
                self.afficher_accueil()
        else :
            self.afficher_avertissement("Coup Invalide", "Ce chiffre ne respecte pas les contraintes (voisinage ou motif).")
            
    def gerer_clic_case(self, x, y, valeur = None):
        """Capte le clic de la souris et affiche le Pop-up de saisie uniquement si l'option est cochée."""
        if (x, y) in self.modele.cases_initiales:
            self.afficher_avertissement("Case verrouillée", "Vous ne pouvez pas modifier une case de départ !")
            return
        
        if self.popup_active and valeur is None:
            valeur, ok = QInputDialog.getInt(self.vue, "Chiffre", "Entrez un numéro (0 pour effacer) :", min=0, max=5)
            if not ok:
                return
        elif not self.popup_active and valeur is None:
            return

        self.gerer_modification_case(x, y, valeur)

    def sauvegarder_score(self, pseudo, temps, difficulte):
        """Écrit un nouveau score validé à la fin du fichier CSV."""
        fichier_existe = os.path.exists("scores.csv")
        with open("scores.csv", mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not fichier_existe:
                writer.writerow(["Pseudo", "Temps (s)", "Difficulté"])
            writer.writerow([pseudo, temps, difficulte])

    def verifier_et_bloquer_case(self):
        """Vérifie mathématiquement si la case ciblée permet de terminer la grille (gère les solutions multiples)."""
        case_cible = self.vue.zone_grille.case_selectionnee
        if not case_cible:
            self.afficher_information("Vérification", "Veuillez d'abord sélectionner une case en cliquant dessus.")
            return

        x, y = case_cible
        valeur_joueur = self.modele.get_valeur(x, y)

        if valeur_joueur == 0:
            self.afficher_information("Vérification", "Cette case est vide ! Mettez un chiffre avant de vérifier.")
            return
        if (x, y) in self.modele.cases_initiales:
            self.afficher_information("Vérification", "Cette case est déjà bloquée (c'est une case valide).")
            return

        # On sauvegarde tout ce que le joueur a tapé
        valeurs_joueur = self.modele.valeurs.copy()
        
        # On nettoie la grille en ne gardant QUE les cases de départ + la case que l'on veut tester
        for case in self.modele.valeurs.keys():
            if case not in self.modele.cases_initiales and case != (x, y):
                self.modele.valeurs[case] = 0

        # On lance le backtracking : existe-t-il au moins UNE solution avec ce chiffre ?
        est_valide = self.modele.resoudre()
        
        # On restaure les chiffres du joueur pour ne pas casser sa partie
        self.modele.valeurs.update(valeurs_joueur)

        if est_valide:
            self.modele.cases_initiales.add((x, y))
            self.partie_modifiee = True
            self.afficher_information("Succès !", "Bien joué ! Ce chiffre fait partie d'une solution valide. Il est verrouillé.")
        else:
            self.afficher_erreur("Erreur", "Aïe... Aucun chemin possible avec ce chiffre. Tu ferais mieux de l'effacer !")

    def resoudre_grille(self):
        """Remplit instantanément la grille avec la solution mise en cache."""
        self.arreter_chrono()
        if self.grille_solution:
            for (x, y), valeur in self.grille_solution.items():
                self.modele.set_valeur(x, y, valeur)
                self.vue.mettre_a_jour_case(x, y, valeur)
            self.afficher_information("Solution", "La grille a été résolue !")
            self.vue.action_indice.setText("Donner un indice (Épuisé)")
            self.indices_restants = 0
        else:
            self.afficher_erreur("Échec", "Impossible de résoudre cette grille (Erreur dans le JSON de base).")
    
    def sauvegarder_partie(self):
        """Génère le fichier de sauvegarde JSON de la partie en cours."""
        chemin_fichier, _ = QFileDialog.getSaveFileName(self.vue, "Sauvegarder la grille", "", "Fichiers JSON (*.json)")
        if chemin_fichier:
            try:
                self.modele.sauvegarder_json(chemin_fichier)
                self.partie_modifiee = False
                self.afficher_information("Sauvegarde", "Partie sauvegardée avec succès.")
            except Exception as e:
                self.afficher_avertissement("Erreur de Sauvegarde", f"Une erreur est survenue : {str(e)}")

    def lancer_jeu_aleatoire(self):
        """Sélectionne une grille au hasard dans le dossier 'grille' et lance la partie."""
        dossier = "grille"
        if os.path.exists(dossier):
            fichiers_json = [f for f in os.listdir(dossier) if f.endswith('.json')]
            if fichiers_json:
                fichier_choisi = random.choice(fichiers_json)
                chemin_complet = os.path.join(dossier, fichier_choisi)
                self.charger_fichier_grille(chemin_complet)
                return
        self.afficher_erreur("Erreur", "Aucun fichier JSON trouvé dans le dossier 'grille'.")
    
    def charger_partie(self):
        """Ouvre un sélecteur de fichier pour choisir une grille spécifique."""
        chemin_fichier, _ = QFileDialog.getOpenFileName(self.vue, "Ouvrir une grille", "grille", "Fichiers JSON (*.json)")
        if chemin_fichier:
            self.charger_fichier_grille(chemin_fichier)

    def charger_fichier_grille(self, chemin_fichier):
        """Charge la grille, calcule la solution complète en arrière-plan, applique la difficulté et lance l'affichage."""
        try:
            self.modele.valeurs.clear()
            self.modele.motifs.clear()
            self.modele.graphe.clear()
            self.grille_solution = None
            
            self.modele.charger_json(chemin_fichier)
            
            valeurs_avant_resolution = self.modele.valeurs.copy()
            for case in self.modele.valeurs.keys():
                if case not in self.modele.cases_initiales:
                    self.modele.valeurs[case] = 0
                    
            if self.modele.resoudre():
                self.grille_solution = self.modele.valeurs.copy()
            else:
                self.grille_solution = None
                
            self.modele.valeurs.update(valeurs_avant_resolution)
            
            if self.niveau_difficulte != "Facile":
                cases_depart = list(self.modele.cases_initiales)
                pourcentage = 0.75 if self.niveau_difficulte == "Normal" else 0.50
                nombre_a_garder = max(1, int(len(cases_depart) * pourcentage))
                cases_conservees = set(random.sample(cases_depart, nombre_a_garder))
                
                for case in cases_depart:
                    if case not in cases_conservees:
                        self.modele.cases_initiales.remove(case)
                        self.modele.set_valeur(case[0], case[1], 0)
            
            largeur = max([x for x, y in self.modele.valeurs.keys()]) + 1
            hauteur = max([y for x, y in self.modele.valeurs.keys()]) + 1
            
            cases_motifs = {}
            for nom_motif, motif in self.modele.motifs.items():
                for case in motif.cases:
                    cases_motifs[case] = nom_motif
                    
            self.vue.dessiner_grille(largeur, hauteur, self.modele.valeurs, cases_motifs, self.modele.cases_initiales)
            
            self.arreter_chrono()
            self.temps_ecoule = 0
            self.premier_coup_joue = False
            self.partie_modifiee = False
            self.vue.update_chrono("0 min 0 s")
            
            if self.niveau_difficulte == "Facile": self.indices_restants = 5
            elif self.niveau_difficulte == "Normal": self.indices_restants = 3
            elif self.niveau_difficulte == "Difficile": self.indices_restants = 1
            
            self.vue.action_indice.setText(f"Donner un indice ({self.indices_restants} restants)")
            self.vue.action_sauvegarder.setEnabled(True)
            self.vue.action_solution.setEnabled(True)
            self.vue.action_indice.setEnabled(True)

            self.afficher_jeu()
            
        except Exception as e:
            self.afficher_erreur("Erreur de chargement", f"Impossible de lire le fichier : {str(e)}")

    def afficher_regles(self):
        """Ouvre la boîte de dialogue textuelle avec les contraintes du jeu et les raccourcis clavier."""
        regles = (
            "Règles du Néonaure :\n\n"
            "• Un chiffre par case.\n"
            "• Un chiffre doit être entouré de chiffres différents (y compris en diagonale).\n"
            "• Un motif de N cases doit comporter tous les chiffres de 1 à N.\n\n"
            "Raccourcis clavier utiles :\n\n"
            "• Pavé numérique (1-9) : Saisir un chiffre dans la case sélectionnée\n"
            "• Retour arrière / Suppr : Effacer la case sélectionnée\n"
            "• Ctrl + S : Sauvegarder la partie\n"
            "• Ctrl + O : Charger une grille\n"
            "• Ctrl + I : Demander un indice\n"
            "• V : Vérifier et bloquer la case sélectionnée"
        )
        self.afficher_information("Aide et Raccourcis", regles)

    def changer_difficulte(self, niveau, afficher_popup=True):
        """Enregistre le réglage de difficulté et synchronise la liste déroulante et le menu."""
        self.niveau_difficulte = niveau
        
        self.vue.combo_difficulte.blockSignals(True)
        self.vue.combo_difficulte.setCurrentText(niveau)
        self.vue.combo_difficulte.blockSignals(False)

        if niveau == "Facile": self.vue.action_diff_facile.setChecked(True)
        elif niveau == "Normal": self.vue.action_diff_normal.setChecked(True)
        elif niveau == "Difficile": self.vue.action_diff_difficile.setChecked(True)

        if afficher_popup:
            self.afficher_information("Difficulté modifiée", f"Niveau réglé sur : {niveau}.\nS'appliquera à la prochaine grille chargée.")

    def donner_indice(self):
        """Révèle un bon chiffre instantanément grâce à la solution en cache, ou active le Pop-up Troll."""
        if self.indices_restants <= 0:
            boite_troll = QMessageBox(self.vue)
            boite_troll.setWindowTitle("Troll !")
            
            chemin_image = os.path.join("grille", "grillec.png")
            if os.path.exists(chemin_image):
                pixmap = QPixmap(chemin_image)
                pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                boite_troll.setIconPixmap(pixmap)
            else:
                boite_troll.setText("Ah ah ! Tu as cru pouvoir cliquer sur un bouton épuisé ?\n\nTu n'as plus d'indices. Travaille ton cerveau !")
                boite_troll.setIcon(QMessageBox.Icon.Warning)
                
            boite_troll.exec()
            return

        case_cible = self.vue.zone_grille.case_selectionnee
        if not case_cible or self.modele.get_valeur(case_cible[0], case_cible[1]) != 0:
            cases_vides = [case for case, valeur in self.modele.valeurs.items() if valeur == 0]
            if not cases_vides:
                self.afficher_information("Indice", "La grille est déjà complètement remplie !")
                return
            case_cible = random.choice(cases_vides)

        if self.grille_solution:
            bonne_valeur = self.grille_solution[case_cible]
            
            self.modele.set_valeur(case_cible[0], case_cible[1], bonne_valeur)
            self.modele.cases_initiales.add(case_cible)
            self.vue.mettre_a_jour_case(case_cible[0], case_cible[1], bonne_valeur)
            self.partie_modifiee = True

            self.indices_restants -= 1
            
            
            if self.indices_restants > 0:
                self.vue.action_indice.setText(f"Donner un indice ({self.indices_restants} restants)")
                self.afficher_information("Coup de pouce", f"Une case a été dévoilée !\n\nIl vous reste {self.indices_restants} indice(s).")
            else:
                self.vue.action_indice.setText("Donner un indice (Épuisé)")
                self.afficher_information("Dernier indice", "Une case a été dévoilée !\n\nAttention, c'était votre dernier indice. À vous de jouer !")
            
        else:
            self.afficher_erreur("Erreur JSON", "La grille de base semble contenir une erreur impossible à résoudre.")

    def gerer_fermeture(self, event):
        """Intercepte la croix rouge de la fenêtre pour éviter de fermer sans sauvegarder."""
        if self.partie_modifiee:
            boite_dialogue = QMessageBox(self.vue)
            boite_dialogue.setIcon(QMessageBox.Icon.Question)
            boite_dialogue.setWindowTitle("Confirmation de fermeture")
            boite_dialogue.setText("Une partie est en cours et n'a pas été sauvegardée. Voulez-vous vraiment quitter ?")
            bouton_oui = boite_dialogue.addButton("Oui", QMessageBox.ButtonRole.YesRole)
            bouton_non = boite_dialogue.addButton("Non", QMessageBox.ButtonRole.NoRole)
            boite_dialogue.setDefaultButton(bouton_non)
            boite_dialogue.exec()
            if boite_dialogue.clickedButton() == bouton_oui:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def afficher_information(self, titre, message):
        """Affiche un Pop-up d'information avec l'icône bleue (i)."""
        QMessageBox.information(self.vue, titre, message)

    def afficher_avertissement(self, titre, message):
        """Affiche un Pop-up d'avertissement avec l'icône jaune (!)."""
        QMessageBox.warning(self.vue, titre, message)

    def afficher_erreur(self, titre, message):
        """Affiche un Pop-up d'erreur avec la croix rouge."""
        QMessageBox.critical(self.vue, titre, message)