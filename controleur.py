from PyQt6.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from PyQt6.QtGui import QKeySequence, QShortcut, QActionGroup
from PyQt6.QtCore import QTimer
import random

class Controleur :
    def __init__(self, modele, vue):
        '''Initialise le contrôleur en liant le modèle et la vue, et en configurant les interactions.
        :param modele: instance de la classe Grille représentant l'état du jeu
        :param vue: instance de la classe VueNeonaure représentant l'interface utilisateur
        '''
        self.modele = modele
        self.vue = vue

        self.temps_ecoule = 0
        self.premier_coup_joue = False
        self.niveau_difficulte = "Facile"

        self.timer = QTimer()
        self.timer.timeout.connect(self.mettre_a_jour_temps)
        self.partie_modifiee = False
        self.indices_restants = 0

        if self.vue and self.modele :
            self.connecter_signaux()
            self.configurer_raccourcis()


    def initialiser_etat_boutons(self):
        '''Configure l'état initial des boutons de la barre de menu.
        Les actions "Sauvegarder", "Solution" et "Indice" sont désactivées'''
        self.vue.action_sauvegarder.setEnabled(False)
        self.vue.action_solution.setEnabled(False)
        self.vue.action_indice.setEnabled(False)

    def demarrer_chrono(self):
        '''Fonction qui démarre le chronomètre en réinitialisant le temps a 0 le temps se met a jour toutes les secondes 
        '''
        self.temps_ecoule = 0
        self.timer.start(1000)
    
    def arreter_chrono(self):
        '''Fonction qui arrête le chronomètre'''
        self.timer.stop()
    
    def mettre_a_jour_temps(self):
        '''Fonction qui met à jour le temps écoulé et affiche le temps formaté dans la vue'''
        self.temps_ecoule += 1
        minutes = self.temps_ecoule // 60
        secondes = self.temps_ecoule % 60
        temps_formate = f"{minutes} min {secondes} s"
        self.vue.update_chrono(temps_formate)

    def connecter_signaux(self):
        '''Connecte les signaux des éléments de l'interface utilisateur aux méthodes du contrôleur.
        Les actions de la barre de menu sont reliées à leurs fonctions respectives, et la
        fermeture de la fenêtre est gérée pour prévenir la perte de données non sauvegardées.'''
        self.vue.action_charger.triggered.connect(self.charger_partie)
        self.vue.action_sauvegarder.triggered.connect(self.sauvegarder_partie)
        self.vue.action_solution.triggered.connect(self.resoudre_grille)
        self.vue.action_aide.triggered.connect(self.afficher_regles)
        self.vue.closeEvent = self.gerer_fermeture

        self.vue.action_indice.triggered.connect(self.donner_indice)
        self.vue.action_verifier.triggered.connect(self.verifier_et_bloquer_case)
    
        # Regroupe les actions de difficulté pour qu'une seule soit active à la fois
        self.groupe_difficulte = QActionGroup(self.vue)
        self.groupe_difficulte.addAction(self.vue.action_diff_facile)
        self.groupe_difficulte.addAction(self.vue.action_diff_normal)
        self.groupe_difficulte.addAction(self.vue.action_diff_difficile)
        
        self.vue.action_diff_facile.triggered.connect(lambda: self.changer_difficulte("Facile"))
        self.vue.action_diff_normal.triggered.connect(lambda: self.changer_difficulte("Normal"))
        self.vue.action_diff_difficile.triggered.connect(lambda: self.changer_difficulte("Difficile"))

    def configurer_raccourcis(self):
        '''Configure les raccourcis clavier pour les actions courantes du jeu, améliorant ainsi l'expérience utilisateur.
         - Ctrl+S pour sauvegarder la partie
         - Ctrl+O pour charger une partie
         - V pour vérifier et bloquer une case sélectionnée'''
        raccourci_sauvegarder = QShortcut(QKeySequence("Ctrl+S"), self.vue)
        raccourci_sauvegarder.activated.connect(self.sauvegarder_partie)

        raccourci_charger = QShortcut(QKeySequence("Ctrl+O"), self.vue)
        raccourci_charger.activated.connect(self.charger_partie)

        raccourci_verifier = QShortcut(QKeySequence("V"), self.vue)
        raccourci_verifier.activated.connect(self.verifier_et_bloquer_case)

    def gerer_modification_case(self, ligne, colonne, nouvelle_valeur):
        ''' Gère la modification d'une case de la grille en vérifiant la validité du coup avant de l'appliquer.
        :param ligne: l'indice de la ligne de la case modifiée
        :param colonne: l'indice de la colonne de la case modifiée
        :param nouvelle_valeur: la nouvelle valeur que le joueur souhaite placer dans la case
        '''
        # Autorise l'effacement (0) sans vérification de contraintes
        if nouvelle_valeur == 0:
            est_valide = True
        else:
            est_valide = self.modele.est_coup_valide(ligne, colonne, nouvelle_valeur)

        if est_valide :
            self.modele.set_valeur(ligne, colonne, nouvelle_valeur)
            self.partie_modifiee = True
            self.vue.mettre_a_jour_case(ligne, colonne, nouvelle_valeur)
            
            # Déclenche le chronomètre au premier coup réel joué
            if nouvelle_valeur != 0 and not self.premier_coup_joue:
                self.premier_coup_joue = True
                self.demarrer_chrono()
        else :
            self.afficher_avertissement("Coup Invalide", "Ce chiffre ne respecte pas les contraintes (voisinage ou motif).")
            
    def gerer_clic_case(self, x, y, valeur = None):
        '''Gère le clic sur une case de la grille, permettant au joueur de modifier la valeur d'une case.
        :param x: l'indice de la ligne de la case cliquée
        :param y: l'indice de la colonne de la case cliquée
        :param valeur: la nouvelle valeur à placer dans la case (optionnelle, si None, une boîte de dialogue demandera la valeur)
        '''
        # Empêche la modification des cases de départ (indices initiaux)
        if (x, y) in self.modele.cases_initiales:
            self.afficher_avertissement("Case verrouillée", "Vous ne pouvez pas modifier une case de départ !")
            return
        
        if valeur is None:
            valeur, ok = QInputDialog.getInt(self.vue, "Chiffre", "Entrez un numéro (0 pour effacer) :", min=0, max=5)
            if not ok:
                return

        self.gerer_modification_case(x, y, valeur)

    def verifier_et_bloquer_case(self):
        '''Vérifie si la valeur placée dans la case sélectionnée est valide et,
        si c'est le cas, bloque la case pour empêcher toute modification future.
        '''
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

        # Sauvegarde l'état actuel avant simulation
        valeurs_joueur = self.modele.valeurs.copy()

        # Vide temporairement les cases du joueur (sauf la cible) pour tester la validité globale
        for case in self.modele.valeurs.keys():
            if case not in self.modele.cases_initiales and case != (x, y):
                self.modele.valeurs[case] = 0

        est_valide = self.modele.resoudre()

        # Restaure la grille du joueur après la simulation
        self.modele.valeurs.update(valeurs_joueur)

        if est_valide:
            self.modele.cases_initiales.add((x, y))
            self.partie_modifiee = True
            self.afficher_information("Succès !", "Bien joué ! Ce chiffre fait partie d'une solution valide. Il est verrouillé.")
        else:
            self.afficher_erreur("Erreur", "Aïe... Si tu laisses ce chiffre ici, il sera impossible de finir la grille !")

    def resoudre_grille(self):
        '''Résout la grille en utilisant l'algorithme de résolution du modèle, et met à jour la vue avec la solution trouvée.
        Si la grille est résolue avec succès, les cases sont mises à jour avec les valeurs de la solution. 
        Sinon, un message d'erreur est affiché.'''
        self.arreter_chrono()
        
        if self.modele.resoudre():
            for (x, y), valeur in self.modele.valeurs.items():
                self.vue.mettre_a_jour_case(x, y, valeur)
            self.afficher_information("Solution", "La grille a été résolue !")
        else:
            self.afficher_erreur("Échec", "Impossible de résoudre cette grille.")
    
    def sauvegarder_partie(self):
        '''Permet au joueur de sauvegarder l'état actuel de la partie dans un fichier JSON.'''
        chemin_fichier, _ = QFileDialog.getSaveFileName(self.vue, "Sauvegarder la grille", "", "Fichiers JSON (*.json)")
        
        if chemin_fichier:
            try:
                self.modele.sauvegarder_json(chemin_fichier)
                self.partie_modifiee = False
                self.afficher_information("Sauvegarde", "Partie sauvegardée avec succès.")
            except Exception as e:
                self.afficher_avertissement("Erreur de Sauvegarde", f"Une erreur est survenue : {str(e)}")
    
    def charger_partie(self):
        '''Permet au joueur de charger une partie à partir d'un fichier JSON.'''
        chemin_fichier, _ = QFileDialog.getOpenFileName(self.vue, "Ouvrir une grille", "", "Fichiers JSON (*.json)")
        
        if chemin_fichier:
            try:
                self.modele.charger_json(chemin_fichier)
                
                # Applique la difficulté en masquant un pourcentage des cases initiales
                if self.niveau_difficulte != "Facile":
                    cases_depart = list(self.modele.cases_initiales)
                    pourcentage = 0.75 if self.niveau_difficulte == "Normal" else 0.50
                    nombre_a_garder = max(1, int(len(cases_depart) * pourcentage))
                    
                    cases_conservees = set(random.sample(cases_depart, nombre_a_garder))
                    
                    for case in cases_depart:
                        if case not in cases_conservees:
                            self.modele.cases_initiales.remove(case)
                            self.modele.set_valeur(case[0], case[1], 0)
                
                # Détermine les dimensions dynamiquement à partir des clés du dictionnaire
                largeur = max([x for x, y in self.modele.valeurs.keys()]) + 1
                hauteur = max([y for x, y in self.modele.valeurs.keys()]) + 1
                
                # Prépare la cartographie des motifs pour l'affichage visuel
                cases_motifs = {}
                for nom_motif, motif in self.modele.motifs.items():
                    for case in motif.cases:
                        cases_motifs[case] = nom_motif
                        
                self.vue.dessiner_grille(largeur, hauteur, self.modele.valeurs, cases_motifs)
                
                # Réinitialisation de l'état de la partie
                self.arreter_chrono()
                self.temps_ecoule = 0
                self.premier_coup_joue = False
                self.partie_modifiee = False
                self.vue.update_chrono("0 min 0 s")
                
                # Attribution des indices selon la difficulté
                if self.niveau_difficulte == "Facile":
                    self.indices_restants = 5
                elif self.niveau_difficulte == "Normal":
                    self.indices_restants = 3
                elif self.niveau_difficulte == "Difficile":
                    self.indices_restants = 1
                
                self.vue.action_indice.setText(f"Donner un indice ({self.indices_restants} restants)")
                
                # Activation des fonctionnalités de jeu en cours
                self.vue.action_sauvegarder.setEnabled(True)
                self.vue.action_solution.setEnabled(True)
                self.vue.action_indice.setEnabled(True)
                
            except Exception as e:
                self.afficher_erreur("Erreur de chargement", f"Impossible de lire le fichier : {str(e)}")


    def afficher_regles(self):
        '''Affiche les règles du Néonaure dans une boîte de dialogue d'information.'''
        regles = (
            "Règles du Néonaure :\n\n"
            "• Un chiffre par case.\n"
            "• Un chiffre doit être entouré de chiffres différents (y compris en diagonale).\n"
            "• Un motif de N cases doit comporter tous les chiffres de 1 à N."
        )
        self.afficher_information("Aide", regles)


    def changer_difficulte(self, niveau):
        '''Change le niveau de difficulté du jeu, 
        ce qui affectera le nombre de cases initiales affichées lors du chargement d'une nouvelle grille.
        :param niveau: le niveau de difficulté sélectionné ("Facile", "Normal" ou "Difficile")
        '''
        self.niveau_difficulte = niveau
        self.afficher_information("Difficulté modifiée", f"Niveau réglé sur : {niveau}.\nCe réglage s'appliquera à la prochaine grille chargée.")

    def donner_indice(self):
        '''Fournit un indice au joueur en révélant la valeur correcte d'une case sélectionnée ou d'une case aléatoire si aucune n'est sélectionnée.
        Le nombre d'indices disponibles est limité en fonction du niveau de difficulté, et le joueur est averti lorsque les indices sont épuisés.'''
        if self.indices_restants <= 0:
            self.afficher_avertissement("Plus d'indices", "Vous avez épuisé tous vos indices pour cette partie !")
            return

        case_cible = self.vue.zone_grille.case_selectionnee
        
        # Sélectionne une case vide au hasard si aucune case n'est ciblée
        if not case_cible or self.modele.get_valeur(case_cible[0], case_cible[1]) != 0:
            cases_vides = [case for case, valeur in self.modele.valeurs.items() if valeur == 0]
            
            if not cases_vides:
                self.afficher_information("Indice", "La grille est déjà complètement remplie !")
                return
                
            case_cible = random.choice(cases_vides)

        # Cherche la solution sans affecter la grille en cours
        valeurs_sauvegardees = self.modele.valeurs.copy()
        
        if self.modele.resoudre():
            bonne_valeur = self.modele.valeurs[case_cible]
            self.modele.valeurs.update(valeurs_sauvegardees)
            
            # Applique et verrouille l'indice trouvé
            self.modele.set_valeur(case_cible[0], case_cible[1], bonne_valeur)
            self.modele.cases_initiales.add(case_cible)
            self.vue.mettre_a_jour_case(case_cible[0], case_cible[1], bonne_valeur)
            self.partie_modifiee = True

            self.indices_restants -= 1
            self.vue.action_indice.setText(f"Donner un indice ({self.indices_restants} restants)")
            
            if self.indices_restants == 0:
                self.vue.action_indice.setEnabled(False)
        else:
            self.modele.valeurs.update(valeurs_sauvegardees)
            self.afficher_avertissement("Impossible d'aider", "Je ne peux pas trouver d'indice.\nVous avez probablement placé un mauvais chiffre précédemment qui bloque la résolution !")

    def gerer_fermeture(self, event):
        '''Gère la tentative de fermeture de la fenêtre en vérifiant si une partie est en cours et non sauvegardée,
        et en demandant confirmation à l'utilisateur pour éviter la perte de données.
        :param event: l'événement de fermeture de la fenêtre
        '''
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
        '''Affiche un message d'information à l'utilisateur dans une boîte de dialogue.
        :param titre: le titre de la boîte de dialogue
        :param message: le message à afficher
        '''
        QMessageBox.information(self.vue, titre, message)

    def afficher_avertissement(self, titre, message):
        '''Affiche un message d'avertissement à l'utilisateur dans une boîte de dialogue.
        :param titre: le titre de la boîte de dialogue
        :param message: le message à afficher
        '''
        QMessageBox.warning(self.vue, titre, message)

    def afficher_erreur(self, titre, message):
        '''Affiche un message d'erreur à l'utilisateur dans une boîte de dialogue.
        :param titre: le titre de la boîte de dialogue
        :param message: le message à afficher
        '''
        QMessageBox.critical(self.vue, titre, message)