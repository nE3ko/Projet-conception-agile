"""
@file
@Application de planning poker sous forme graphique

"""

# Importation des modules nécessaires
import json
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import PhotoImage

class Joueurs:
    """
    @class Joueurs
    @brief Classe pour gérer une liste de joueurs.
    """
    joueurs = []
    def __init__(self, nb):
        """
        @brief Constructeur de Joueurs.

        @param nb: Nombre de joueurs.
        """
        while(len(self.joueurs) != 0):
            self.joueurs.pop(len(self.joueurs)-1)
        for i in range(nb):
            self.joueurs.append(Joueur())


class Joueur:
    """
    @class Joueur
    @brief Classe pour gérer un joueur.
    """
    def __init__(self):
        """
        @brief Constructeur de Joueur.
        """
        self.vote = None

class Backlog:
    """
    @class Backlog
    @brief Classe pour gérer le fichier backlog.
    """
    def __init__(self, fichier_json):
        """
        @brief Constructeur de Backlog.

        @param fichier_json: Chemin du fichier backlog.
        """
        self.fichier_json = fichier_json
        self.backlog = []

    def charger_depuis_json(self):
        """
        @brief Permet d'ouvrir le fichier .json et le stocker dans l'attribut backlog
        """
        with open(self.fichier_json, 'r') as fichier:
            donnees = json.load(fichier)
        if "backlog" in donnees:
            self.backlog = donnees['backlog']

    def sauvegarder_en_json(self):
        """
        @brief Permet de sauvegarder l'attribut backlog dans fichier_json
        """
        donnees = {'backlog': self.backlog}
        with open(self.fichier_json, 'w') as fichier:
            json.dump(donnees, fichier, indent=2)

class Regle:
    """
    @class Regle
    @brief Classe pour représenter une règle de vote.
    """
    def __init__(self, regle):
        """
        @brief Constructeur de Regle.

        @param regle: Objet de règle.
        """
        self.regle = regle

    def changer_regle(self, regle):
        """
        @brief Change la règle actuelle.

        @param regle: Nouvelle règle.
        """
        self.regle = regle

    def valider_votes(self, votes):
        """
        @brief Valide les votes en fonction de la règle.

        @param votes: Liste des votes.
        @return True si les votes sont valides, False sinon.
        """
        return self.regle.valider_votes(votes)


class RegleStrict:
    """
    @class RegleStrict
    @brief Classe pour représenter la règle de vote strict.

    @note Cette règle valide les votes uniquement s'il y a une unanimité.
    """
    def valider_votes(self, votes):
        """
        @brief Valide les votes en vérifiant l'unanimité.

        @param votes: Liste des votes.
        @return True si l'unanimité est atteinte, False sinon.
        """
        return len(set(votes)) == 1


class RegleMoyenne:
    """
    @class RegleMoyenne
    @brief Classe pour représenter la règle de vote moyenne.

    """
    def valider_votes(self, votes):
        """
        @brief Valide les votes selon une logique spécifique.

        @param votes: Liste des votes.
        @return Toujours True, la logique spécifique doit être gérée dans l'application.
        """
        return True

class Jeu:
    """
    @class Jeu
    @brief Classe principale représentant le jeu.

    @param joueurs: Instance de la classe Joueurs représentant la liste des joueurs.
    @param backlog: Instance de la classe Backlog représentant le backlog des fonctionnalités.
    @param regle: Instance de la classe Regle représentant la règle de vote utilisée.
    """
    def __init__(self, joueurs, backlog, regle):
        self.joueurs = Joueurs
        self.backlog = backlog
        self.regle = regle

    def voter_sur_backlog(self, frame):
        """
        @brief Permet aux joueurs de voter sur le backlog.

        @param frame: Instance de la classe PageVote utilisée pour afficher les informations du vote.
        """
        self.backlog.charger_depuis_json()

        # Parcours de la liste de fonctionnalités importée du backlog
        for fonctionnalite, valeur in self.backlog.backlog.items():
            if valeur:  # Si la fonctionnalité a déjà été votée, passe à la suivante
                continue

            tour = 1
            unanime = False

            # Boucle de vote des joueurs
            while not unanime:
                frame.explication.set(f"Votez sur la difficulté de la fonctionnalité ci-dessus.")
                cafe = 0
                inttero = False

                # Traitement du vote de chaque joueur
                for i, joueur in enumerate(self.joueurs.joueurs):
                    joueur.vote = frame.vote_joueur_n(i + 1, fonctionnalite)
                    if joueur.vote == "cafe":
                        cafe += 1
                    elif joueur.vote == "interro":
                        inttero = True

                # Retour au menu si tous les joueurs ont voté 'café'
                if cafe == len(self.joueurs.joueurs):
                    frame.master.afficher_page_menu()
                    return

                # Vérification de l'unanimité des votes
                if tour == 1:
                    unanime = RegleStrict().valider_votes([joueur.vote for joueur in self.joueurs.joueurs])
                else:
                    unanime = self.regle.valider_votes([joueur.vote for joueur in self.joueurs.joueurs])

                # Affichage de l'état des votes
                if not unanime:
                    frame.erreur.set("Les votes ne correspondent pas. Veuillez revoter.")
                elif inttero or (cafe > 0 and cafe < len(self.joueurs.joueurs)):
                    frame.erreur.set("Un ou plusieurs joueurs ont voté '?' ou 'café'. Veuillez revoter.")
                    unanime = False
                tour += 1

            # Moyenne du vote pour la fonctionnalité en cours
            votes = [int(joueur.vote) for joueur in self.joueurs.joueurs]
            moyenne_vote = round(sum(votes) / len(votes))

            # Enregistrement dans le fichier
            self.backlog.backlog[fonctionnalite] = str(moyenne_vote)
            self.backlog.sauvegarder_en_json()

            # Reset affichage erreur
            frame.erreur.set("")

        # Passage à la page des résultats lorsque toutes les fonctionnalités ont été traitées
        frame.master.afficher_page_resultat(self.backlog.backlog)

class Menu:
    """
    @class Menu
    @brief Classe pour gérer les configurations et lancement du jeu.

    Utilise le modèle de conception Singleton pour s'assurer qu'il n'y a qu'une seule instance de Menu.

    @var _instance: Instance unique de la classe Menu.
    @var jeu: Instance de la classe Jeu pour le jeu en cours.
    """
    _instance = None
    jeu = None

    def __new__(cls):
        """
        @brief Méthode pour créer une nouvelle instance de Menu si elle n'existe pas déjà.

        @return Instance unique de la classe Menu.
        """
        if cls._instance is None:
            cls._instance = super(Menu, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        @brief Méthode d'initialisation de la classe Menu.
        """
        if self._initialized:
            return
        self._initialized = True

    def config_joueurs(self, nb_joueurs):
        """
        @brief Configurer le nombre de joueurs dans le jeu.

        @param nb_joueurs: Nombre de joueurs dans le jeu.
        """
        self.joueurs = Joueurs(nb_joueurs)

    def config_backlog(self, fichier_json):
        """
        @brief Configurer le fichier backlog du jeu.

        @param fichier_json: Chemin du fichier backlog en format JSON.
        """
        self.backlog = Backlog(fichier_json)

    def config_regle(self, regle):
        """
        @brief Configurer la règle de vote du jeu.

        @param regle: Chaîne de caractères représentant la règle de vote ("strict" ou "moyenne").
        """
        if regle == "strict":
            self.regle = RegleStrict()
        elif regle == "moyenne":
            self.regle = RegleMoyenne()

    def lancer_jeu(self):
        """
        @brief Lancer le jeu avec les configurations actuelles.
        """
        self.jeu = Jeu(self.joueurs, self.backlog, self.regle)

class Affichage(tk.Tk):
    """
    @class Affichage
    @brief Classe pour gérer l'affichage de l'application Planning Poker.

    Hérite de la classe Tk de tkinter.

    @var menu: Instance de la classe Menu pour gérer les configurations du jeu.
    @var backlog: Instance de la classe Backlog pour gérer le fichier backlog du jeu.
    @var page_menu: Instance de la classe PageMenu pour afficher la page de configuration.
    @var page_vote: Instance de la classe PageVote pour afficher la page de vote.
    @var page_resultat: Instance de la classe PageResultat pour afficher la page de résultats.
    @var page_courante: Page actuellement affichée.
    """
    def __init__(self):
        """
        @brief Constructeur de la classe Affichage.
        """
        super().__init__()
        self.menu = Menu()
        self.backlog = None

        # Configuration de la fenêtre principale
        self.title("Planning Poker")
        self.geometry("1000x600")
        self.resizable(0, 0)

        # Initialisation des pages
        self.page_menu = PageMenu(self)
        self.page_vote = PageVote(self)
        self.page_resultat = PageResultat(self)
        
        # Affichage page Menu
        self.page_courante = self.page_menu
        self.page_courante.pack(fill=tk.BOTH, expand=True)

    def afficher_page_menu(self):
        """
        @brief Afficher la page de configuration.
        """
        self.page_courante.pack_forget()
        self.page_courante = self.page_menu
        self.page_courante.pack(fill=tk.BOTH, expand=True)

    def afficher_page_vote(self):
        """
        @brief Afficher la page de vote et lancer la fonction de jeu.
        """
        self.page_courante.pack_forget()
        self.page_courante = self.page_vote
        self.page_courante.pack(fill=tk.BOTH, expand=True)
        self.menu.jeu.voter_sur_backlog(self.page_vote)  # Lancement de la fonction de jeu

    def afficher_page_resultat(self, backlog):
        """
        @brief Afficher la page de résultats avec le backlog spécifié.

        @param backlog: Dictionnaire contenant les fonctionnalités et leurs votes.
        """
        self.page_courante.pack_forget()
        self.page_courante = self.page_resultat
        self.page_courante.pack(fill=tk.BOTH, expand=True)
        self.backlog = backlog 
        self.page_resultat.ajouter_fonctionnalites()  # Affichage des fonctionnalités


class PageMenu(tk.Frame):
    """
    @class PageMenu
    @brief Classe pour gérer la page de configuration du Planning Poker.

    Hérite de la classe Frame de tkinter.

    @var regle: Variable de chaîne pour stocker la règle sélectionnée (par défaut: "strict").
    @var liste_deroulante: Menu déroulant pour sélectionner la règle.
    @var message_err: Variable de chaîne pour afficher les messages d'erreur.
    @var etiquette_message: Étiquette pour afficher le message d'erreur.
    @var backlog: Chemin du fichier backlog sélectionné.
    @var valeur_molette: Variable entière pour stocker le nombre de joueurs sélectionné via la molette.
    """
    def __init__(self, master):
        """
        @brief Constructeur de la classe PageMenu.

        @param master: Fenêtre principale de l'application.
        """
        super().__init__(master)

        # Contenu de la page d'accueil

        # Titre
        label_accueil = tk.Label(self, text="Planning Poker")
        label_accueil.pack(pady=50)

        # Liste des règles possibles
        self.regle = tk.StringVar(value="strict")
        regles = ["moyenne", "strict"]
        self.liste_deroulante = tk.OptionMenu(self, self.regle, *regles)
        self.liste_deroulante.pack(pady=10)

        # Message en cas de non-sélection d'un backlog
        self.message_err = tk.StringVar()
        self.etiquette_message = tk.Label(self, textvariable=self.message_err, fg="red")
        self.etiquette_message.pack(pady=10)

        # Bouton sélection d'un fichier backlog
        self.backlog = None
        btn_fichier = tk.Button(self, text="Choix du backlog sur le PC", command=self.choix_fichier)
        btn_fichier.pack()

        # Molette sélection du nombre de joueurs
        self.valeur_molette = tk.IntVar()
        molette = tk.Scale(self, from_=2, to=10, orient=tk.HORIZONTAL, variable=self.valeur_molette, label="Nombre de joueurs", length=140)
        molette.pack(pady=20)

        # Bouton commencer
        btn_start = tk.Button(self, text="Commencer", command=self.commencer)
        btn_start.pack(pady=20)
        
        # Bouton quitter
        btn_quitter = tk.Button(self, text="Quitter", command=master.destroy)
        btn_quitter.pack(side=tk.RIGHT, padx=50)

    def choix_fichier(self):
        """
        @brief Ouvrir une boîte de dialogue pour choisir un fichier backlog en .json.
        """
        self.backlog = filedialog.askopenfilename(title="Choisir un fichier backlog en .json")
    
    def commencer(self):
        """
        @brief Lancer le jeu avec les configurations actuelles.

        - Vérifie si le backlog est sélectionné.
        - Configure le jeu avec la règle, le backlog et le nombre de joueurs.
        - Lance le jeu et affiche la page de vote.
        """
        # Vérification que le backlog est bien rentré par l'utilisateur
        if self.backlog is None:
            self.message_err.set("Erreur : Aucun fichier sélectionné")
            return
        elif not self.backlog.endswith(".json"):
            self.message_err.set("Erreur : Fichier backlog invalide (.json attendu)")
            return
        else:
            self.message_err.set("")

        # Configuration du jeu
        self.master.menu.config_regle(self.regle.get())
        self.master.menu.config_backlog(self.backlog)
        self.master.menu.config_joueurs(self.valeur_molette.get())
        self.master.menu.lancer_jeu()
        self.master.afficher_page_vote()

class PageVote(tk.Frame):
    """
    @class PageVote
    @brief Classe pour gérer la page de vote du Planning Poker.

    Hérite de la classe Frame de tkinter.

    @var vote_j_n: Variable de chaîne pour afficher le numéro du joueur.
    @var explication: Variable de chaîne pour afficher l'explication du vote.
    @var fonctionnalite: Variable de chaîne pour afficher le titre de la fonctionnalité.
    @var vote: Variable de chaîne pour stocker le vote sélectionné par le joueur.
    @var erreur: Variable de chaîne pour afficher les messages d'erreur.
    """
    def __init__(self, master):
        """
        @brief Constructeur de la classe PageVote.

        @param master: Fenêtre principale de l'application.
        """
        super().__init__(master)
        self.vote_j_n = tk.StringVar()
        self.explication = tk.StringVar()
        self.fonctionnalite = tk.StringVar()
        self.vote = tk.StringVar()
        self.erreur = tk.StringVar()

        # Numéro du joueur
        label_j_n = tk.Label(self, textvariable=self.vote_j_n)
        label_j_n.grid(row=0, pady=20, columnspan=6)

        # Explication
        label_explication = tk.Label(self, textvariable=self.explication, fg="green")
        label_explication.grid(row=1, pady=10, columnspan=6)

        # Titre fonctionnalité
        label_fonctionnalite = tk.Label(self, textvariable=self.fonctionnalite)
        label_fonctionnalite.grid(row=2, pady=10, columnspan=6)

        # Créer et afficher des boutons pour chaque cartes
        noms_images_png = ["cartes_0.png", "cartes_1.png", "cartes_2.png", "cartes_3.png", "cartes_5.png", "cartes_8.png", "cartes_13.png", "cartes_20.png", "cartes_40.png", "cartes_100.png", "cartes_cafe.png", "cartes_interro.png"]
        for i, nom_image in enumerate(noms_images_png):
            chemin_image = f"./cartes/{nom_image}"
            self.ajouter_bouton_image(chemin_image, (i // 6) + 3, (i % 6))

        # Vote sélectionné
        label_erreur = tk.Label(self, textvariable=self.erreur, fg="red")
        label_erreur.grid(row=5, pady=10, columnspan=6)

    def ajouter_bouton_image(self, chemin_image, ligne, colonne):
        """
        @brief Ajouter un bouton avec une image à la grille.

        @param chemin_image: Chemin de l'image à afficher sur le bouton.
        @param ligne: Ligne de la grille où placer le bouton.
        @param colonne: Colonne de la grille où placer le bouton.
        """
        # Charger l'image PNG
        largeur = 206 // 2
        hauteur = 320 // 2
        image = tk.PhotoImage(file=chemin_image)
        image_redimensionnee = image.subsample(int(image.width() / largeur), int(image.height() / hauteur))

        # Créer un bouton avec l'image
        bouton_image = tk.Button(self, image=image_redimensionnee, command=lambda chemin=chemin_image: self.carte_choisie(chemin))
        bouton_image.image = image_redimensionnee  # Pour éviter que la référence à l'objet image soit perdue
        bouton_image.grid(row=ligne, column=colonne, pady=10, padx=28)

    def carte_choisie(self, chemin_image):
        """
        @brief Mettre à jour la variable de vote en fonction de l'image sélectionnée.

        @param chemin_image: Chemin de l'image sélectionnée.
        """
        # Conversion chemin de la carte en son nom
        chemin = chemin_image.split("_")
        self.vote.set(chemin[len(chemin) - 1].split(".png")[0])

    def vote_joueur_n(self, n, fonctionnalite):
        """
        @brief Afficher les éléments nécessaires pour le vote du joueur n.

        @param n: Numéro du joueur.
        @param fonctionnalite: Titre de la fonctionnalité à voter.
        @return: Le vote du joueur.
        """
        # Affichage
        self.vote_j_n.set(f"Joueur n°{n}")
        self.explication.set("Votez pour la fonctionnalité")
        self.fonctionnalite.set(fonctionnalite)

        # Attendre le vote de l'utilisateur
        self.wait_variable(self.vote)

        return self.vote.get()

class PageResultat(tk.Frame):
    """
    @class PageResultat
    @brief Classe pour gérer la page de résultats du Planning Poker.

    Hérite de la classe Frame de tkinter.

    @var canvas: Widget Canvas pour permettre le défilement vertical.
    @var scrollbar: Barre de défilement associée au Canvas.
    @var cadre_fonctionnalites: Cadre pour contenir les fonctionnalités affichées.
    @var tableau: Widget Treeview pour afficher les fonctionnalités et les votes.
    """
    def __init__(self, master):
        """
        @brief Constructeur de la classe PageResultat.

        @param master: Fenêtre principale de l'application.
        """
        super().__init__(master)

        # Contenu de la page d'accueil
        label_accueil = tk.Label(self, text="Resultats")
        label_accueil.pack(pady=10)

        # Créer un Canvas avec une barre de défilement
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Ajouter un cadre pour contenir les fonctionnalités
        self.cadre_fonctionnalites = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.cadre_fonctionnalites, anchor="n")

        # Bouton pour passer à la page de configuration
        bouton_configuration = tk.Button(self, text="Menu", command=master.afficher_page_menu)
        bouton_configuration.pack(pady=10)

        # Créer le tableau
        self.tableau = ttk.Treeview(self.cadre_fonctionnalites, columns=("Fonctionnalités", "Votes"), show="headings")
        self.tableau.heading("Fonctionnalités", text="Fonctionnalités")
        self.tableau.heading("Votes", text="Votes")
        self.tableau.pack(fill="both", expand=True)

    def ajouter_fonctionnalites(self):
        """
        @brief Ajoute les fonctionnalités et les votes au tableau.
        """
        # Supprimer les fonctionnalités des précédents backlogs
        self.tableau.delete(*self.tableau.get_children())

        # Ajouter les fonctionnalités au tableau
        for fonctionnalite, note in self.master.backlog.items():
            self.tableau.insert("", "end", values=(fonctionnalite, note))

        # Configurer la barre de défilement pour suivre le contenu du Canvas
        self.cadre_fonctionnalites.bind("<Configure>", self.on_cadre_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_cadre_configure(self, event):
        """
        @brief Met à jour la taille du Canvas quand le cadre intérieur change de taille.

        @param event: Événement de configuration du cadre intérieur.
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """
        @brief Ajuste la largeur du cadre intérieur pour correspondre à la largeur du Canvas.

        @param event: Événement de configuration du Canvas.
        """
        window_id = self.canvas.create_window((0, 0), window=self.cadre_fonctionnalites, anchor="nw")
        self.canvas.itemconfig(window_id, width=event.width)
        
# --- Exécution Principale --- #
if __name__ == '__main__':
    app = Affichage()
    app.mainloop()
    