import sys
from PyQt6.QtWidgets import QApplication

from modele import Grille
from vue import VueNeonaure
from controleur import Controleur

def main():
    app = QApplication(sys.argv)

    modele = Grille()
    
    vue = VueNeonaure(action_clic=None, action_clavier=None)

    controleur = Controleur(modele, vue)

    vue.zone_grille.action_clic = controleur.gerer_clic_case
    vue.zone_grille.action_clavier = controleur.gerer_modification_case

   
    controleur.initialiser_etat_boutons()
    
    vue.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()