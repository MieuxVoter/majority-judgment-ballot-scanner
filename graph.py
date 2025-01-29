import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


class Graph(tk.Frame):
    def __init__(self, parent, config, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.config = config
        self.mentions = config["mentions"]  # Liste des mentions (labels des catégories)
        self.propositions = config["propositions"]  # Liste des propositions
        #self.colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]  # Couleurs pour les mentions
        #self.colors = ["#00ff00", "#66ff00", "#ccff00", "#ffcc00", "#ff3300", "#ff0000"]  # Couleurs pour les mentions
        self.colors = ["#0000ff", "#00ffff", "#00ff00", "#a0ff00", "#ffa000", "#ff0000"]  # Couleurs pour les mentions

        # Initialisation de la figure Matplotlib
        self.figure, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Configuration de l'axe des abscisses
        self.ax.set_xlim(0, 100)  # Pourcentages de 0 à 100
        self.ax.set_xticks(np.arange(0, 101, 10))  # Grille tous les 10 %
        self.ax.grid(axis="x", linestyle="--", alpha=0.7)  # Grille verticale

        # Configuration de l'axe des ordonnées
        self.ax.set_yticks(range(len(config["propositions"])))
        self.ax.set_yticklabels(config["propositions"])

        # Initialisation des barres (vide)
        self.bars = None
        self.update_graph({prop: {mention: 0 for mention in config["mentions"]} for prop in config["propositions"]})

    def update_graph(self, results):
        """
        Met à jour le graphique avec de nouveaux résultats.
        :param results: Dictionnaire contenant les pourcentages de chaque mention pour chaque proposition.
                        Exemple :
                        {
                            "1": {"Très bien": 40, "Bien": 30, "Assez bien": 20, "Passable": 10, ...},
                            "2": {...},
                            ...
                        }
        """
        self.ax.clear()  # Réinitialiser le graphique

        # Préparer les données pour chaque proposition
        y_positions = range(len(self.config["propositions"]))
        bar_starts = np.zeros(len(self.config["propositions"]))  # Début des segments de barre
        for i, mention in enumerate(self.config["mentions"]):
            bar_widths = [results[prop][mention] for prop in self.config["propositions"]]
            self.ax.barh(y_positions, bar_widths, left=bar_starts, color=self.colors[i], label=mention)
            bar_starts += bar_widths  # Mettre à jour le point de départ

        # Configuration des axes
        self.ax.set_xlim(0, 100)
        self.ax.set_xticks(np.arange(0, 101, 10))
        self.ax.set_yticks(y_positions)
        self.ax.set_yticklabels(self.config["propositions"])
        self.ax.grid(axis="x", linestyle="--", alpha=0.7)
        self.ax.legend(title="Mentions")

        self.ax.set_xlabel("Pourcentage")
        self.ax.set_title("Répartition des mentions par proposition")

        # Rafraîchir le graphique
        self.canvas.draw()

    def clear_graph(self):
        """Efface le graphique en le réinitialisant avec des données à 0 %."""
        empty_results = {prop: {mention: 0 for mention in self.config["mentions"]} for prop in self.config["propositions"]}
        self.update_graph(empty_results)