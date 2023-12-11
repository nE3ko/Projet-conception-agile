# Importation des modules nécessaires
import json
import time
from abc import ABC, abstractmethod
from typing import List
from unittest.mock import patch, mock_open
from io import StringIO
import unittest
import contextlib

# --- Implémentations ---
# Design pattern : Prototype
# Afin d'avoir la possiblité de créer d'autre acteurs qu'un joueur classique
# Classe abstraite pour représenter les acteurs du jeu
class Personne(ABC):
    @abstractmethod
    def __init__(self, nom):
        pass

# Classe pour représenter un joueur classique
class Joueur(Personne):
    def __init__(self, nom):
        self.nom = nom
        self.vote = None

# Classe pour gérer le backlog des fonctionnalités
class Backlog:
    def __init__(self):
        self.elements = []

    def charger_depuis_json(self, fichier_json):
        with open(fichier_json, 'r') as fichier:
            donnees = json.load(fichier)
            self.elements = donnees['backlog']

    def sauvegarder_en_json(self, fichier_json):
        donnees = {'backlog': self.elements}
        with open(fichier_json, 'w') as fichier:
            json.dump(donnees, fichier, indent=2)

# Classe pour la règle de vote strict
class RegleStrict:
    def valider_votes(self, votes):
        return len(set(votes)) == 1  # Vérifie l'unanimité


# Classe pour la règle de vote moyenne
class RegleMoyenne:
    def valider_votes(self, votes):
        return True  # Logique spécifique pour la règle moyenne

# Design pattern : Factory
# Permet de créer les types de règle du jeu
class FabriqueRegle:
    def creer_regle(self, type_regle):
        if type_regle == 'strict':
            return RegleStrict()
        elif type_regle == 'moyenne':
            return RegleMoyenne()
        else:
            raise ValueError("Type de règle invalide")

# Design pattern : Singleton 
# Possède une seule instance
# Classe principale représentant le jeu
class Jeu:
    def __init__(self, stockage_backlog, fabrique_regle, chronometre):
        self.joueurs = []
        self.backlog_actuel = stockage_backlog
        self.regles_actuelles = None
        self.chronometre = chronometre
        self.fabrique_regle = fabrique_regle

    def demarrer_jeu(self):
        print("=== Bienvenue dans le Planning Poker ===")
        self.configurer_joueurs()
        self.choisir_regles()

        while True:
            print("\nOptions :")
            print("1. Voter sur le Backlog")
            print("2. Charger le Backlog depuis JSON")
            print("3. Sauvegarder le Backlog en JSON")
            print("4. Quitter")

            option = input("Choisissez une option : ")
            if option == '1':
                self.voter_sur_backlog()
            elif option == '2':
                fichier_json = input("Entrez le chemin du fichier JSON pour charger le backlog : ")
                self.backlog_actuel.charger_depuis_json(fichier_json)
            elif option == '3':
                fichier_json = input("Entrez le chemin du fichier JSON pour sauvegarder le backlog : ")
                self.backlog_actuel.sauvegarder_en_json(fichier_json)
            elif option == '4':
                break
            else:
                print("Option invalide. Veuillez choisir une option valide.")

    def configurer_joueurs(self):
        print("\n=== Configuration des Joueurs ===")
        nb_joueurs = int(input("Entrez le nombre de joueurs : "))
        for i in range(nb_joueurs):
            nom = input(f"Entrez le nom du joueur {i + 1} : ")
            self.joueurs.append(Joueur(nom))

    def choisir_regles(self):
        print("\n=== Sélection des Règles ===")
        print("Règles disponibles : strict, moyenne")
        type_regle = input("Choisissez les règles : ")
        self.regles_actuelles = self.fabrique_regle.creer_regle(type_regle)

    def voter_sur_backlog(self):
        print("\n=== Vote sur le Backlog ===")
        indice = 0
        for element in self.backlog_actuel.elements:
            tour = 1
            unanime = False
            while not unanime:
                print(f"\nVotez sur la difficulté de '{element}' :")
                for joueur in self.joueurs:
                    vote = input(f"{joueur.nom}, entrez votre vote (ex. 1-10) : ")
                    joueur.vote = vote

                if tour == 1:
                    unanime = RegleStrict().valider_votes([joueur.vote for joueur in self.joueurs])
                else:
                    unanime = self.regles_actuelles.valider_votes([joueur.vote for joueur in self.joueurs])
                if not unanime:
                    print("Les votes ne correspondent pas. Veuillez revoter.")
                tour += 1
                self.backlog_actuel.elements[indice] = {element: vote}
            self.afficher_resultats(element, vote)
            indice += 1

    def afficher_resultats(self, element, vote):
        print(f"\nFin des votes")
        votes = [int(joueur.vote) for joueur in self.joueurs]
        moyenne_vote = sum(votes) / len(votes)
        print(f"Élément : {element}, Difficulté : {moyenne_vote:.2f}")


# Classe pour gérer le chronomètre
class Chronometre:
    def __init__(self):
        self.temps_depart = 0
        self.temps_fin = 0
        self.est_en_cours = False

    def demarrer(self, duree=60):
        self.temps_depart = time.time()
        self.temps_fin = self.temps_depart + duree
        self.est_en_cours = True
        print(f"\nChronomètre démarré pendant {duree} secondes.")

    def arreter(self):
        if self.est_en_cours:
            temps_ecoule = time.time() - self.temps_depart
            print(f"Chronomètre arrêté. Temps écoulé : {temps_ecoule} secondes.")
            self.est_en_cours = False
        else:
            print("Le chronomètre ne fonctionne pas.")


# Classe principale pour exécuter les tests unitaires
class TestJeu(unittest.TestCase):
    def test_systeme_vote(self):
        # Création d'objets fictifs pour les tests
        stockage_backlog = Backlog()
        fabrique_regle = FabriqueRegle()
        chronometre = Chronometre()

        # Création d'une instance de jeu fictive
        jeu = Jeu(stockage_backlog, fabrique_regle, chronometre)

        # Configuration de joueurs fictifs
        joueur1 = Joueur("Alice")
        joueur2 = Joueur("Bob")
        #joueur3 = Joueur("Lai")
        jeu.joueurs = [joueur1, joueur2]

        # Configuration manuelle d'un backlog pour les tests
        jeu.backlog_actuel.elements = ["Fonctionnalite A", "Fonctionnalite B", "Fonctionnalite C"]

        # Configuration manuelle d'une règle pour les tests (vous pouvez choisir une règle en fonction de vos besoins)
        jeu.regles_actuelles = fabrique_regle.creer_regle("strict")

        # Simulation de l'entrée utilisateur pour les votes (vous pouvez ajuster en fonction de votre implémentation réelle)
        jeu.voter_sur_backlog()

        # ! fonctionne pas !
        # Test sauvegarde en Json avancée backlog
        jeu.backlog_actuel.sauvegarder_en_json("backlog.json")
        jeu.backlog_actuel = Backlog()
        jeu.backlog_actuel.charger_depuis_json("backlog.json")

        jeu.voter_sur_backlog()

        # with patch('builtins.print', side_effect=lambda *args: None):  # Simulation de print pour capturer la sortie
        #     with StringIO() as mock_stdout:
        #         with contextlib.redirect_stdout(mock_stdout):
        #             jeu.afficher_resultats()

        #         resultats_reels = mock_stdout.getvalue()

        # self.assertEqual(resultats_reels.strip(), resultats_attendus.strip())

# --- Exécution Principale ---

if __name__ == '__main__':
    unittest.main()