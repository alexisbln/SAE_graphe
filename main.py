import sys
from PyQt6.QtWidgets import QApplication

from modele import Grille
from vue import VueNeonaure
from controleur import Controleur

def main():
    app = QApplication(sys.argv)

    modele = Grille()
    controleur = Controleur(modele, None)
    vue = VueNeonaure(controleur.gerer_clic_case, controleur.gerer_modification_case)

    controleur.vue = vue
    controleur.connecter_signaux()
    controleur.configurer_raccourcis()
    
    vue.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()