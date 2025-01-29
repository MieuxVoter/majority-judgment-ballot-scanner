import tkinter as tk
from tkinter import ttk


class DebugSettings(tk.Frame):
    def __init__(self, parent, debug_config, *args, **kwargs):
        """
        Initialise la zone de réglage debug.

        :param parent: Parent Tkinter.
        :param debug_config: Dictionnaire avec les paramètres de débogage (debug=True/False).
        """
        super().__init__(parent, *args, **kwargs)
        self.debug_config = debug_config
        self.brightness = None

        # Vérifie si le mode debug est activé
        #if not self.debug_config.get("debug", True):
        #    return

        # Labels pour la section des curseurs
        tk.Label(self, text="Réglages de Debug", font=("Arial", 14, "bold")).pack(pady=5)

        # Curseurs pour cv2.HoughCircles
        self.hough_dp = self._create_slider("Hough dp", 1, 5, 1, 1)
        self.hough_min_dist = self._create_slider("Hough Min Dist", 1, 100, 1, 40)
        self.hough_param1 = self._create_slider("Hough Param1", 10, 200, 10, 60)
        self.hough_param2 = self._create_slider("Hough Param2", 10, 100, 5, 30)
        self.hough_min_radius = self._create_slider("Hough Min Radius", 0, 50, 1, 13)
        self.hough_max_radius = self._create_slider("Hough Max Radius", 0, 100, 1, 25)

        # Curseurs pour cv2.threshold
        self.brightness_value = self._create_slider("Seuil Luminosité", 0, 255, 5, 11) # 61 #19

        # Curseur pour le seuil de case cochée
        self.checked_threshold = self._create_slider("Seuil Case Cochée", 0, 20, 0, 4) #1

        # Affichage des valeurs des cercles de détection
        self.circle_brightness_label = tk.Label(self, text="Luminosité des cercles : N/A", font=("Arial", 12))
        self.circle_brightness_label.pack(pady=5)

        # Bouton pour actualiser les valeurs des cercles
        tk.Button(self, text="Actualiser Luminosité Cercles", command=self._update_circle_brightness).pack(pady=5)

    def _create_slider(self, label, from_, to, resolution, default):
        """
        Crée un curseur avec un label associé.

        :param label: Nom du paramètre.
        :param from_: Valeur minimale.
        :param to: Valeur maximale.
        :param resolution: Pas du curseur.
        :param default: Valeur par défaut.
        :return: Référence au Scale Tkinter créé.
        """
        frame = tk.Frame(self)
        frame.pack(fill=tk.X, padx=10, pady=2)

        tk.Label(frame, text=label, width=20, anchor="w").pack(side=tk.LEFT)
        slider_value = tk.DoubleVar(value=default)
        scale = ttk.Scale(frame, from_=from_, to=to, orient=tk.HORIZONTAL, length=200, variable=slider_value)
        scale.set(default)
        scale.pack(side=tk.RIGHT, padx=10)
        value_label = tk.Label(frame, text=f"{default:.2f}")
        value_label.pack(side=tk.RIGHT, padx=10)

        def update_label(*args):
            value_label.config(text=f"{slider_value.get():.2f}")

        slider_value.trace_add("write", update_label)  # Mise à jour dynamique du label
        return scale

    def _update_circle_brightness(self):
        """
        Met à jour l'affichage de la luminosité des cercles en appelant la fonction de callback.
        """
        if self.brightness is not None:
            self.circle_brightness_label.config(
                text=f"Luminosité des cercles : "
                     f"Top-Left: {self.brightness['top_left']}, Top-Right: {self.brightness['top_right']}, "
                     f"Bottom-Left: {self.brightness['bottom_left']}, Bottom-Right: {self.brightness['bottom_right']}"
            )
        else:
            self.circle_brightness_label.config(text="Luminosité des cercles : Erreur")

    def set_circle_brightness(self, brightness):
        self.brightness = brightness

    def get_hough_params(self):
        """
        Récupère les paramètres actuels pour cv2.HoughCircles.
        :return: Dictionnaire avec les paramètres.
        """
        return {
            "dp": self.hough_dp.get(),
            "minDist": self.hough_min_dist.get(),
            "param1": self.hough_param1.get(),
            "param2": self.hough_param2.get(),
            "minRadius": self.hough_min_radius.get(),
            "maxRadius": self.hough_max_radius.get(),
            "brightness": self.brightness_value.get(),
            "checked_threshold": self.checked_threshold.get()
        }
