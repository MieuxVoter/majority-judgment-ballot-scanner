import tkinter as tk
from tkinter import filedialog, Frame

from PIL import Image, ImageTk
import cv2
import matplotlib.pyplot as plt

import scanner
from analyse import process_ballot, calculate_results, generate_merit_profile
import ballot
import counting
import graph
import debug_settings
from copy import deepcopy


DEFAULT_CONFIG = {
    "mentions": ["Très bien", "Bien", "Assez bien", "Passable", "Insuffisant", "À rejeter"],
    "valeurs": [1, 2, 3, 4, 5, 6],
    "propositions": ["A", "B","C","D","E","F","G","H","I","J"],
    "lignes": [[30, 20], [70, 20], [110, 20], [150, 20], [190, 20], [230, 20], [270, 20], [310, 20], [350, 20], [390, 20]],
    "colonnes": [[30, 20], [70, 20], [110, 20], [150, 20], [190, 20], [230, 20]],
    "hauteur": 440,
    "largeur": 280
}


class VotingApp:
    config = DEFAULT_CONFIG

    def __init__(self, root):
        self.root = root
        self.root.title("Application de Vote - Jugement Majoritaire")

        left_frame = Frame(root)
        left_frame.grid(row=0, column=0, padx=10, pady=5)

        right_frame = Frame(root)
        right_frame.grid(row=0, column=1, padx=10, pady=5)

        debug_frame = Frame(root)
        debug_frame.grid(row=0, column=2, padx=10, pady=5)

        # Section 1 : Importer le modèle
        self.model_file_label = tk.Label(left_frame, text="Modèle de bulletin :")
        self.model_file_label.pack()
        self.model_button = tk.Button(left_frame, text="Importer", command=self.load_model)
        self.model_button.pack()

        # Section 2 : Vue caméra
        self.camera_frame = tk.Label(left_frame, text="Vue caméra ici")
        self.camera_frame.pack()
        self.capture_button = tk.Button(left_frame, text="Capturer", command=self.capture_image)
        self.capture_button.pack()

        # Section 3 : Bulletin
        self.ballot = ballot.Ballot(left_frame, self.config)
        self.ballot.pack()
        self.counting_button = tk.Button(left_frame, text="Comptabiliser", command=self.count_ballot)
        self.counting_button.pack()

        # Section 3 : Résultats
        self.results_label = tk.Label(right_frame, text="Résultats :")
        self.results_label.pack()
        self.counting = counting.Counting(right_frame, self.config)
        self.counting.pack()
        self.graph = graph.Graph(right_frame, self.config)
        self.graph.pack()

        # Graphique
        self.graph_frame = tk.Frame(right_frame)
        self.graph_frame.pack()

        self.debug_settings = debug_settings.DebugSettings(debug_frame, {"debug": True})
        self.debug_settings.pack()

        self.scanner = scanner.Scanner(self.config)
        self.update_webcam()

    def load_model(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")])
        if file_path:
            # Charger et traiter le fichier modèle
            print(f"Fichier modèle chargé : {file_path}")

    def capture_image(self):
        self.ballot.set_grid(self.scanner.get_grid())
        return

    def update_webcam(self):
        # Utiliser OpenCV pour capturer une image
        image = self.scanner.capture(self.debug_settings.get_hough_params())
        if image is not None:
            # Afficher l'image capturée
            image = Image.fromarray(image)
            img_tk = ImageTk.PhotoImage(image)
            self.camera_frame.configure(image=img_tk)
            self.camera_frame.image = img_tk
        self.root.after(200, self.update_webcam)

    def count_ballot(self):
        self.counting.add_ballot(self.ballot.get_grid())
        self.ballot.clear()
        results = deepcopy(self.counting.get_results())
        for r in results.values():
            total = sum([r[m] for m in self.config["mentions"]])
            if total == 0:
                for m in self.config["mentions"]:
                    r[m] = 0
            else:
                for m in self.config["mentions"]:
                    r[m] = r[m] * 100 / total
        self.graph.update_graph(results)

    def show_results(self, processed_data):
        # Afficher les résultats dans Tkinter
        # Générer et afficher un graphique des profils de mérite
        fig = plt.figure()
        generate_merit_profile(fig, processed_data)
        plt.show()

    def close_app(self):
        """Ferme l'application."""
        self.scanner.release()
        self.root.destroy()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = tk.Tk()
    app = VotingApp(root)
    root.mainloop()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
