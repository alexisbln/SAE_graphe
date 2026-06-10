from PyQt6.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtCore import QTimer

class Controleur :
    def __init__(self, modele, vue):
        self.modele = modele
        self.vue = vue

        self.temps_ecoule = 0
        self.premier_coup_joue = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.mettre_a_jour_temps)
        self.partie_modifiee = False

        if self.vue and self.modele :
            self.connecter_signaux()
            self.configurer_raccourcis()
    def initialiser_etat_boutons(self):
        self.vue.action_sauvegarder.setEnabled(False)
        self.vue.action_solution.setEnabled(False)

    def demarrer_chrono(self):
        self.temps_ecoule = 0
        self.timer.start(1000)
    
    def arreter_chrono(self):
        self.timer.stop()
    
    def mettre_a_jour_temps(self):
        self.temps_ecoule += 1
        minutes = self.temps_ecoule // 60
        secondes = self.temps_ecoule % 60
        temps_formate = f"{minutes} min {secondes} s"
        self.vue.update_chrono(temps_formate)

    def connecter_signaux(self):
        self.vue.action_charger.triggered.connect(self.charger_partie)
        self.vue.action_sauvegarder.triggered.connect(self.sauvegarder_partie)
        self.vue.action_solution.triggered.connect(self.resoudre_grille)
        self.vue.closeEvent = self.gerer_fermeture

    def configurer_raccourcis(self):
        # raccourci sauvegarder (ctrl + s)
        raccourci_sauvegarder = QShortcut(QKeySequence("Ctrl+S"), self.vue)
        raccourci_sauvegarder.activated.connect(self.sauvegarder_partie)

        #raccourci charger (ctrl + o)
        raccourci_charger = QShortcut(QKeySequence("Ctrl+O"), self.vue)
        raccourci_charger.activated.connect(self.charger_partie)

    def gerer_modification_case(self, ligne, colonne, nouvelle_valeur):
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
                
        else :
            self.afficher_avertissement("Coup Invalide", 
                "Ce chiffre ne respecte pas les contraintes (voisinage ou motif).")
            
    def gerer_clic_case(self, x, y, valeur = None):
        if (x, y) in self.modele.cases_initiales:
            self.afficher_avertissement(
                "Case verrouillée", 
                "Vous ne pouvez pas modifier une case de départ !"
            )
            return
        
        if valeur is None:
            valeur, ok = QInputDialog.getInt(self.vue, "Chiffre", "Entrez un numéro (0 pour effacer) :", min=0, max=5)
            if not ok:
                return

        self.gerer_modification_case(x, y, valeur)


    def resoudre_grille(self):
        
        self.arreter_chrono()
        
        if self.modele.resoudre():
            for (x, y), valeur in self.modele.valeurs.items():
                self.vue.mettre_a_jour_case(x, y, valeur)
            self.afficher_information("Solution", "La grille a été résolue !")
        else:
            self.afficher_erreur("Échec", "Impossible de résoudre cette grille.")
    
    def sauvegarder_partie(self):
        chemin_fichier, _ = QFileDialog.getSaveFileName(
            self.vue, 
            "Sauvegarder la grille", 
            "", 
            "Fichiers JSON (*.json)"
        )
        
        if chemin_fichier:
            try:
                self.modele.sauvegarder_json(chemin_fichier)
                self.partie_modifiee = False
                self.afficher_information("Sauvegarde", "Partie sauvegardée avec succès.")
            except Exception as e:
                self.afficher_avertissement("Erreur de Sauvegarde", f"Une erreur est survenue : {str(e)}")
    
    def charger_partie(self):
        chemin_fichier, _ = QFileDialog.getOpenFileName(
            self.vue, 
            "Ouvrir une grille", 
            "", 
            "Fichiers JSON (*.json)"
        )
        
        if chemin_fichier:
            try:
                self.modele.charger_json(chemin_fichier)
                
                largeur = max([x for x, y in self.modele.valeurs.keys()]) + 1
                hauteur = max([y for x, y in self.modele.valeurs.keys()]) + 1
                
                cases_motifs = {}
                for nom_motif, motif in self.modele.motifs.items():
                    for case in motif.cases:
                        cases_motifs[case] = nom_motif
                self.vue.dessiner_grille(largeur, hauteur, self.modele.valeurs, cases_motifs)
                self.arreter_chrono()
                self.temps_ecoule = 0
                self.premier_coup_joue = False
                self.partie_modifiee = False
                self.vue.update_chrono("0 min 0 s")
                
                self.vue.action_sauvegarder.setEnabled(True)
                self.vue.action_solution.setEnabled(True)
            except Exception as e:
                self.afficher_erreur("Erreur de chargement", f"Impossible de lire le fichier : {str(e)}")


    def gerer_fermeture(self, event):
        if self.partie_modifiee:
            reponse = QMessageBox.question(
                self.vue,
                "Confirmation de fermeture",
                "Une partie est en cours et n'a pas été sauvegardée. Voulez-vous vraiment quitter ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reponse == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def afficher_information(self, titre, message):
        QMessageBox.information(self.vue, titre, message)

    def afficher_avertissement(self, titre, message):
        QMessageBox.warning(self.vue, titre, message)

    def afficher_erreur(self, titre, message):
        QMessageBox.critical(self.vue, titre, message)
    