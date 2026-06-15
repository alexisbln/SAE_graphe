# 🧩 Jeu Néonaure (SAE Graphe)

**Projet de BUT 1 Informatique**
*Réalisé par : Alexis Blouin, Théo Duriez, François Goddefroy*

Bienvenue sur notre implémentation en Python/PyQt6 du jeu **Néonaure** . Ce projet a été développé en respectant strictement l'architecture **MVC** (Modèle-Vue-Contrôleur).

---

## 📜 Règles du Jeu

Le but du jeu est de remplir toutes les cases de la grille avec des chiffres en respectant trois règles simples :
1. **Un chiffre par case.**
2. **Voisinage :** Deux cases adjacentes (y compris en diagonale) ne peuvent **pas** contenir le même chiffre.
3. **Motifs :** La grille est divisée en blocs (motifs) délimités par des traits gras. Un motif composé de *N* cases doit obligatoirement contenir tous les chiffres de 1 à *N*.

---

## ✨ Fonctionnalités Principales

* **Dashboard interactif :** Un menu d'accueil complet avec gestion des parties, des scores et des paramètres.
* **Jouabilité Adaptative :** Jouable 100% à la souris (via des pop-ups) ou 100% au clavier de manière fluide (option modifiable dans les paramètres).
* **Système de Difficulté :** Facile, Normal ou Difficile (efface un pourcentage des cases de départ pour augmenter le défi).
* **Assistance & Easter Egg :** Un système d'indices basé sur un solveur en arrière-plan, avec une petite surprise ("Troll") si vous épuisez tous vos crédits !
* **Sauvegarde & Scores :** Possibilité de sauvegarder/charger une partie (JSON) et enregistrement des meilleurs temps dans un fichier `scores.csv`.

---

## ⌨️ Raccourcis Clavier

Pour une expérience de jeu optimale et rapide, voici les raccourcis disponibles une fois une case sélectionnée :

| Touche(s) | Action |
| :--- | :--- |
| **1 à 9** (Pavé num.) | Saisir un chiffre directement dans la case |
| **Retour Arrière / Suppr** | Effacer le contenu de la case |
| **V** | Vérifier et bloquer la case (si le chiffre est mathématiquement correct) |
| **Ctrl + I** | Demander un indice |
| **Ctrl + S** | Sauvegarder la partie en cours |
| **Ctrl + O** | Charger une nouvelle grille |

---

## 🛠️ Installation et Lancement

**Prérequis :** Python 3.x et la bibliothèque PyQt6.

1. Installez PyQt6 (si ce n'est pas déjà fait) :
   ```bash
   pip install PyQt6
   ```
2. Clonez le dépôt et placez-vous dans le dossier :
   ```bash
   git clone https://github.com/alexisbln/SAE_graphe.git
   cd SAE_graphe
   ```
3. Lancez le jeu :
   ```bash
   python main.py
   ```

---

## ⚙️ Générateur de Grilles (`generateur.py`)

Nous avons également développé notre propre générateur de grilles aléatoires de A à Z. Il découpe aléatoirement une grille en motifs et utilise un algorithme d'essai-erreur récursif (**Backtracking**) pour la remplir de manière valide.

**⚠️ AVERTISSEMENT :** Le générateur est **100% fonctionnel**, mais la génération de grilles peut être **très longue** (plusieurs minutes selon la taille). 
Générer une grille aléatoire avec des motifs complexes de manière purement mathématique demande énormément de calculs (des millions d'itérations). L'algorithme est conçu pour abandonner et recommencer s'il tombe sur une impasse géométrique trop complexe.

**Pour l'utiliser :**
   ```bash
   python generateur.py
   ```
Les grilles générées apparaîtront dans le dossier `grilles_generees/` au format JSON, prêtes à être copiées dans le dossier `grille/` de l'application principale.

---
*Projet réalisé dans le cadre de la SAE Graphe - 2026*