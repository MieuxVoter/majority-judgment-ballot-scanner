import tkinter as tk

class Counting(tk.Frame):
    def __init__(self, parent, config, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.config = config
        self.results = {}
        self.results = {prop: {mention: 0 for mention in self.config["mentions"]} for prop in
                        self.config["propositions"]}
        for r in self.results.values():
            r["Blanc"] = 0  # Nombre de bulletins blancs
            r["Nul"] = 0  # Nombre de bulletins nuls

        # Grille d'affichage des résultats
        self.grid_labels = {}
        for i, mention in enumerate(["Propositions"] + self.config["mentions"] + ["Blanc", "Nul", "Rang", "Mention"]):
            tk.Label(self, text=mention, font=("Arial", 10, "bold"), borderwidth=2, relief="ridge").grid(row=0, column=i, sticky="nsew", padx=2, pady=2)

        for i, prop in enumerate(self.config["propositions"]):
            tk.Label(self, text=prop, font=("Arial", 10), borderwidth=2, relief="ridge").grid(row=i + 1, column=0, sticky="nsew", padx=2, pady=2)

            self.grid_labels[prop] = {}
            for j, mention in enumerate(self.results[prop].keys()):  # enumerate((self.config["mentions"])):
                label_text = tk.StringVar(value="0 (0.0%)")
                label = tk.Label(self, textvariable=label_text, font=("Arial", 10), borderwidth=2, relief="ridge")
                label.grid(row=i + 1, column=j + 1, sticky="nsew", padx=2, pady=2)
                self.grid_labels[prop][mention] = label_text

            label_text = tk.StringVar(value="?")
            label = tk.Label(self, textvariable=label_text, font=("Arial", 10), borderwidth=2, relief="ridge")
            label.grid(row=i + 1, column=len(self.results[prop].keys()) + 1, sticky="nsew", padx=2, pady=2)
            self.grid_labels[prop][1] = label_text

            label_text = tk.StringVar(value="?")
            label = tk.Label(self, textvariable=label_text, font=("Arial", 10), borderwidth=2, relief="ridge")
            label.grid(row=i + 1, column=len(self.results[prop].keys()) + 2, sticky="nsew", padx=2, pady=2)
            self.grid_labels[prop][2] = label_text

    def clear(self):
        """Efface tous les résultats"""
        self.results = {prop: {mention: 0 for mention in self.config["mentions"]} for prop in self.config["propositions"]}
        for r in self.results.values():
            r["Blanc"] = 0  # Nombre de bulletins blancs
            r["Nul"] = 0  # Nombre de bulletins nuls
        self.update_display()

    def add_ballot(self, grid):
        """
        Comptabilise un bulletin.
        :param ballot: Dictionnaire avec une clé par proposition et une liste de mentions cochées pour chaque proposition.
        """
        mentions = {}
        for p in self.config["propositions"]:
            mentions[p] = []
        for (row, col), cell in grid.items():
            if cell:
                mentions[self.config["propositions"][row]].append(self.config["mentions"][col])
        for p in self.config["propositions"]:
            if len(mentions[p]) == 0:  # Aucun vote, c'est un bulletin blanc
                self.results[p]["Blanc"] += 1
            elif len(mentions[p]) > 1:  # Plus d'une mention cochée, c'est un bulletin nul
                self.results[p]["Nul"] += 1
            else:  # Comptabiliser la mention
                self.results[p][mentions[p][0]] += 1
        self.update_display()

    def get_results(self):
        """
        Récupère les résultats sous forme de dictionnaire.
        :return: Un dictionnaire contenant les totaux pour chaque mention et les totaux blancs/nuls.
        """
        return self.results

    def update_display(self):
        """Met à jour l'affichage de la grille des résultats"""
        all_mentions = []
        for prop, mentions in self.results.items():
            total_votes = sum(mentions.values())
            cumul = 0.
            mention_found = False
            for mention, count in mentions.items():
                percentage = (count / total_votes * 100) if total_votes > 0 else 0
                cumul += percentage
                if not mention_found and cumul > 50.:
                    mention_found = True
                    all_mentions.append({
                        "proposition": prop,
                        "mention": mention,
                        "percentage": cumul
                    })
                    self.grid_labels[prop][2].set(mention)
                self.grid_labels[prop][mention].set(f"{count} ({percentage:.1f}%)")
        rang = 1
        for m in self.config["mentions"]:
            propositions = sorted([a for a in all_mentions if a["mention"] == m], key=lambda a: a["percentage"], reverse=True)
            for p in propositions:
                self.grid_labels[p["proposition"]][1].set(str(rang))
                rang = rang + 1

