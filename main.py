import sys
from PyQt6.QtWidgets import QApplication


from controleur import Controleur

def main():
    app = QApplication(sys.argv)

    modele = None
    vue = None

    controleur = Controleur(modele, vue)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()