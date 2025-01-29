import cv2
import numpy as np
import time
import itertools


def distance2(p1, p2):
    return float(np.sqrt((int(p1[0]) - int(p2[0])) ** 2 + (int(p1[1]) - int(p2[1])) ** 2))


class Scanner:

    def __init__(self, config):
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.config = config
        self.valid_time = 0

    def capture(self, thresholds):
        ret, self.frame = self.cap.read()
        if not ret:
            print("Erreur : impossible de capturer l'image.")
            return None
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        # Appliquer un flou pour réduire le bruit
        self.frame = cv2.GaussianBlur(gray, (3, 3), 1.5)

        # 3. Normaliser les niveaux de gris
        # self.frame = cv2.normalize(self.frame, None, 0, 255, cv2.NORM_MINMAX)

        # 4. (Optionnel) Améliorer le contraste
        #self.frame = cv2.equalizeHist(self.frame)

        result = self.detecter_bords(thresholds)
        if not result and time.time_ns() < self.valid_time + 2000000000:
            self.frame = self.valid_frame
        #cap.release()
        #cv2.destroyAllWindows()
        return self.frame

    def _detecter_grand_cercles(self, thresholds):
        # Détection des cercles
        circles = cv2.HoughCircles(
            self.frame,
            cv2.HOUGH_GRADIENT,
            dp=thresholds["dp"],
            minDist=thresholds["minDist"],  # Distance minimale entre les centres de deux cercles
            param1=thresholds["param1"],  # Seuil pour l'algorithme de Canny
            param2=thresholds["param2"],  # Seuil pour la détection des cercles (plus bas -> plus de faux positifs)
            minRadius=int(thresholds["minRadius"]),  # Rayon minimal du cercle
            maxRadius=int(thresholds["maxRadius"])  # Rayon maximal du cercle
        )

        if circles is not None:
            # Arrondir les coordonnées et les rayons
            circles = np.int16(np.around(circles))
            circles = [(x, y, r) for x, y, r in circles[0]]
        return circles

    def _detecter_rectangles(self, circles, thresholds):
        rectangles = []
        same_size_quad = []
        for quad in itertools.combinations(circles, 4):
            is_quad = (len(set(quad)) == 4)
            min_radius = min(quad, key=lambda p : p[2])[2]
            max_radius = max(quad, key=lambda p : p[2])[2]
            if is_quad and min_radius >= max_radius * 0.7:
                same_size_quad.append(quad)

        expected_proportions = self.config["largeur"]/self.config["hauteur"]
        for quad in same_size_quad:
            try:
                top_left = min(quad, key=lambda p: p[0] + p[1])  # Plus petite somme x + y
                top_right = max(quad, key=lambda p: p[0] - p[1])  # Plus grande différence x - y
                bottom_left = min(quad, key=lambda p: p[0] - p[1])  # Plus petite différence x - y
                bottom_right = max(quad, key=lambda p: p[0] + p[1])  # Plus grande somme x + y
                distance_top = distance2(top_right, top_left)
                distance_bottom = distance2(bottom_right, bottom_left)
                distance_left = distance2(top_left, bottom_left)
                distance_right = distance2(top_right, bottom_right)
                top_ratio = min(distance_top, distance_bottom) / max(distance_top, distance_bottom)
                side_ratio = min(distance_left, distance_right) / max(distance_left, distance_right)
                proportions_seen = ((distance_top + distance_bottom) / (distance_left + distance_right)) / expected_proportions
                if proportions_seen > 1.:
                    proportions_seen = 1./proportions_seen
                if top_ratio >= 0.8 and side_ratio >= 0.8 and proportions_seen >= 0.8:
                    rectangles.append({
                        "top_left": top_left,
                        "top_right": top_right,
                        "bottom_left": bottom_left,
                        "bottom_right": bottom_right,
                        "ratio": top_ratio * side_ratio * proportions_seen
                    })
            except:
                pass
        return rectangles

    def _detecter_petits_cercles(self, rectangle, thresholds):
        result = False
        points = (rectangle["top_left"], rectangle["top_right"], rectangle["bottom_left"], rectangle["bottom_right"])
        min_radius = min(points, key= lambda r: r[2])[2]
        # Détection des cercles
        circles = cv2.HoughCircles(
            self.frame,
            cv2.HOUGH_GRADIENT,
            dp=thresholds["dp"],
            minDist=thresholds["minDist"],  # Distance minimale entre les centres de deux cercles
            param1=thresholds["param1"],  # Seuil pour l'algorithme de Canny
            param2=thresholds["param2"],  # Seuil pour la détection des cercles (plus bas -> plus de faux positifs)
            minRadius=2,  # Rayon minimal du cercle
            maxRadius=min_radius-3  # Rayon maximal du cercle
        )

        if circles is not None:
            # Arrondir les coordonnées et les rayons
            circles = np.int16(np.around(circles))
            circles = [(x, y, r) for x, y, r in circles[0]]

            points_detected = []
            for p in points:
                detected = False
                for c in circles:
                    if abs(p[0] - c[0]) < 3 and abs(p[1] - c[1]) < 3:
                        detected = True
                        break
                points_detected.append(detected)
            if len([1 for p in points_detected if p]) == 4:
                result = True
        return result

    def trace_rectangle(self, rectangle):
        top_left = (rectangle["top_left"][0], rectangle["top_left"][1])
        top_right = (rectangle["top_right"][0], rectangle["top_right"][1])
        bottom_left = (rectangle["bottom_left"][0], rectangle["bottom_left"][1])
        bottom_right = (rectangle["bottom_right"][0], rectangle["bottom_right"][1])
        cv2.line(self.frame, top_left, top_right, (0, 0, 255))
        cv2.line(self.frame, bottom_left, bottom_right, (0, 0, 255))
        cv2.line(self.frame, top_left, bottom_left, (0, 0, 255))
        cv2.line(self.frame, top_right, bottom_right, (0, 0, 255))

    def detecter_bords(self, thresholds):
        result = False
        circles = self._detecter_grand_cercles(thresholds)
        rectangles = []
        filtered_rectangles = []

        if circles is not None:
            rectangles = self._detecter_rectangles(circles, thresholds)

        if len(rectangles) > 0:
            rectangles = sorted(rectangles, key=lambda r: r["ratio"], reverse= True)
            for r in rectangles:
                if self._detecter_petits_cercles(r, thresholds):
                    filtered_rectangles.append(r)

        if len(rectangles) > 0:
            self.dimensions = rectangles[0]

            self.trace_grid(thresholds)
            self.valid_frame = self.frame
            self.valid_time = time.time_ns()
            result = True
        if circles is not None:
            for (x, y, r) in circles:
                cv2.putText(self.frame, f"({x},{y})", (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                # Dessiner les cercles détectés
                cv2.circle(self.frame, (x, y), r, (0, 255, 0), 2)  # Cercle extérieur
                cv2.circle(self.frame, (x, y), 2, (0, 0, 255), 3)  # Centre du cercle
        for r in rectangles:
            self.trace_rectangle(r)
        return result

    def trace_grid(self, thresholds):
        self.cells = {}
        left_points = self.interpolate_points(self.dimensions["top_left"], self.dimensions["bottom_left"], self.config["hauteur"], self.config["lignes"])
        right_points = self.interpolate_points(self.dimensions["top_right"], self.dimensions["bottom_right"], self.config["hauteur"], self.config["lignes"])
        for i in range(0, len(left_points), 2):
            top_points = self.interpolate_points(left_points[i], right_points[i], self.config["largeur"], self.config["colonnes"])
            bottom_points = self.interpolate_points(left_points[i+1], right_points[i+1], self.config["largeur"], self.config["colonnes"])
            for j in range(0, len(top_points), 2):
                self.cells[(i/2, j/2)] = {
                    "top_left": top_points[j],
                    "top_right": top_points[j+1],
                    "bottom_left": bottom_points[j],
                    "bottom_right": bottom_points[j+1]
                }
        darkest = self.check_corner_illumination()
        for (row, col), cell in self.cells.items():
            cell["checked"] = self.is_cell_checked(cell, thresholds, darkest-thresholds["brightness"])
            if cell["checked"]:
                #print(cell, "checked")
                self.trace_rectangle(cell)
            #else:
            #    print(cell, "empty")
        return

    def interpolate_points(self, start, end, length, config):
        points = []
        for i in config:
            points.append((
                np.int16(np.around(start[0] + (end[0] - start[0]) * float(i[0]) / float(length))),
                np.int16(np.around(start[1] + (end[1] - start[1]) * float(i[0]) / float(length)))
            ))
            points.append((
                np.int16(np.around(start[0] + (end[0] - start[0]) * float((i[0] + i[1])) / float(length))),
                np.int16(np.around(start[1] + (end[1] - start[1]) * float((i[0] + i[1])) / float(length)))
            ))
        return points

    def check_corner_illumination(self, radius=1):
        darkest = 255
        corners = [self.dimensions["top_left"], self.dimensions["top_right"], self.dimensions["bottom_left"], self.dimensions["bottom_right"]]
        mask = np.zeros(self.frame.shape[:2], dtype=np.uint8)
        for circle_center in corners:
            cv2.circle(mask, (circle_center[0], circle_center[1]), radius, 255, -1)
            mean_intensity = cv2.mean(self.frame, mask=mask)[0]
            #print(mean_intensity)
            if darkest > mean_intensity:
                darkest = mean_intensity
        return darkest

    # Fonction pour vérifier si une case est cochée
    def is_cell_checked(self, cell, thresholds, brightness):
        # Extraire la région de la case
        width = int(np.linalg.norm(np.array(cell["top_right"]) - np.array(cell["top_left"])))
        height = int(np.linalg.norm(np.array(cell["bottom_left"]) - np.array(cell["top_left"])))
        src_points = np.float32([cell["top_left"], cell["top_right"], cell["bottom_left"], cell["bottom_right"]])
        dst_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        cell_roi = cv2.warpPerspective(self.frame, matrix, (width, height))

        # self.frame = cell_roi

        # Convertir en niveaux de gris si l'image est en couleur
        if len(cell_roi.shape) == 3:
            cell_roi = cv2.cvtColor(cell_roi, cv2.COLOR_BGR2GRAY)

        # Calculer la proportion de pixels sombres
        _, binary_image = cv2.threshold(cell_roi, brightness, 255, cv2.THRESH_BINARY_INV)
        total_pixels = binary_image.size
        dark_pixels = cv2.countNonZero(binary_image)
        dark_ratio = dark_pixels / total_pixels

        #print("Cell", cell, dark_ratio)

        # Vérifier si la case est cochée selon le seuil
        return dark_ratio*100 > thresholds["checked_threshold"]

    def get_grid(self):
        grid = {}
        for (row, col), cell in self.cells.items():
            grid[(row, col)] = cell["checked"]
        return grid

    def release(self):
        self.cap.release()
