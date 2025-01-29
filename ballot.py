import tkinter as tk


class Ballot(tk.Frame):
    def __init__(self, parent, config, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.cells = {}  # Dictionnaire pour stocker l'état des cases
        self.warnings = []
        self.config = config

        # Créer la grille
        for row in range(len(config["lignes"])):
            for col in range(len(config["colonnes"])):
                # Chaque case est un bouton
                cell_button = tk.Button(
                    self,
                    text=" ",
                    width=2,
                    height=1,
                    relief="raised",
                    command=lambda r=row, c=col: self.toggle_cell(r, c)
                )
                cell_button.grid(row=row, column=col+1, padx=2, pady=2)
                label = tk.Label(self, text=config["propositions"][row])
                label.grid(row=row, column=0)

                # Initialiser l'état de la case (False = décoché)
                self.cells[(row, col)] = {"button": cell_button, "checked": False}
            warning_label = tk.Label(self, text="", font=("Arial", 12), fg="red")
            warning_label.grid(row=row, column=len(config["colonnes"]) + 1, padx=5)
            self.warnings.append(warning_label)

    def toggle_cell(self, row, col):
        """Inverser l'état de la case (coché/décoché)"""
        cell = self.cells[(row, col)]
        cell["checked"] = not cell["checked"]
        cell["button"]["relief"] = "sunken" if cell["checked"] else "raised"
        cell["button"]["text"] = "X" if cell["checked"] else " "
        self._update_warnings()

    def _update_warnings(self):
        # Mettre à jour les avertissements pour chaque ligne
        rowCount=[0]*len(self.config["propositions"])
        for (row, col) in self.cells:
            if self.cells[(row, col)]["checked"]:
                rowCount[row] = rowCount[row] + 1
        for row, row_buttons in enumerate(self.warnings):
            if rowCount[row] == 0:
                self.warnings[row]["text"] = "⚠️ Aucun"
            elif rowCount[row] > 1:
                self.warnings[row]["text"] = "⚠️ Plusieurs"
            else:
                self.warnings[row]["text"] = ""

    def set_cell(self, row, col, checked):
        """Cocher ou décocher une case de manière programmatique"""
        if (row, col) in self.cells:
            self.cells[(row, col)]["checked"] = checked
            self.cells[(row, col)]["button"]["relief"] = "sunken" if checked else "raised"
            self.cells[(row, col)]["button"]["text"] = "X" if checked else " "
            self._update_warnings()

    def get_grid(self):
        """Récupérer toutes les cases cochées"""
        grid = {}
        for (row, col), cell in self.cells.items():
            grid[(row, col)] = cell["checked"]
        return grid

    def set_grid(self, grid):
        for (row, col), cell in self.cells.items():
            checked = grid[(row, col)]
            cell["checked"] = checked
            cell["button"]["relief"] = "sunken" if checked else "raised"
            cell["button"]["text"] = "X" if checked else " "
        self._update_warnings()

    def clear(self):
        for (row, col), cell in self.cells.items():
            cell["checked"] = False
            cell["button"]["relief"] = "raised"
            cell["button"]["text"] = " "
        self._update_warnings()


