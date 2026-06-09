from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QKeySequence, QShortcut

class Controleur :
    def __init__(self, modele, vue):
        self.modele = modele
        self.vue = vue

        if self.vue and self.modele :
            self.connecter_signaux()
            self.configurer_raccourcis()
        
    def connecter_signaux(self):
        # à compléter avec le code de françois
        pass

    def configurer_raccourcis(self):
        # raccourci sauvegarder (ctrl + s)
        raccourci_sauvegarder = QShortcut(QKeySequence("Ctrl+S"), self.vue)
        raccourci_sauvegarder.activated.connect(self.sauvegarder_partie)

        #raccourci charger (ctrl + o)
        raccourci_charger = QShortcut(QKeySequence("Ctrl+O"), self.vue)
        raccourci_charger.activated.connect(self.charger_partie)

    def gerer_modification_case(self, ligne, colonne, nouvelle_valeur):
        
        est_valide = self.modele.verifier_coup(ligne, colonne, nouvelle_valeur)

        if est_valide :
            self.modele.mettre_a_jour_case(ligne, colonne, nouvelle_valeur)
            self.vue.actualiser_affichage()
        
        else :
            self.afficher_avertissement("Coup Invalide", 
                "Ce chiffre ne respecte pas les contraintes (voisinage ou motif).")
            
    def sauvegarder_partie(self):

        try :
            self.afficher_information("Sauvegarde", "Partie sauvegardée avec succès.")
        except Exception as e :
            self.afficher_avertissement("Erreur de Sauvegarde", f"Une erreur est survenue lors de la sauvegarde : {str(e)}")
    
    def charger_partie(self):
        pass

    def afficher_information(self, titre, message):
        QMessageBox.information(self.vue, titre, message)

    def afficher_avertissement(self, titre, message):
        QMessageBox.warning(self.vue, titre, message)

    def afficher_erreur(self, titre, message):
        QMessageBox.critical(self.vue, titre, message)
    