"""Textile Pattern Studio. Start in PyCharm mit Python 3.12, Java 21 und py5.

Im verwendeten Python-Interpreter einmal `python -m pip install py5`
ausführen. Danach diese Datei starten. Das aktuelle Projekt lebt im
Arbeitsspeicher und bleibt beim Wechsel zwischen den Ansichten erhalten.
"""

import math

import py5

STAGE_HOME, STAGE_DRAW, STAGE_PATTERN = range(3)
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 650
CANVAS_X, CANVAS_Y = 32, 172
CANVAS_WIDTH, CANVAS_HEIGHT = 680, 434
MIN_SPACING, MAX_SPACING = 40, 320
SIDEBAR_X = 744

INK = "#261D38"
MUTED = "#635D6F"
PAPER = "#FAF7F1"
WHITE = "#FFFFFF"
LINE = "#DED7E4"
PURPLE = "#593982"
LILAC = "#E4D8F2"
GREEN = "#235A4D"


class Studio:
    def __init__(self):
        self.stage = STAGE_HOME
        self.buttons = []
        self.pending_action = None
        self.reset_project()

    def reset_project(self):
        self.has_project = False
        self.points = []
        self.closed = False
        self.spacing = [142, 122]
        self.dragged_point = None
        self.dragged_slider = None
        self.notice = ""

    def go_to(self, stage):
        if stage == STAGE_DRAW:
            self.has_project = True
        self.stage = stage
        self.notice = ""

    def new_project(self, example=False):
        def start():
            self.reset_project()
            self.go_to(STAGE_DRAW)
            if example:
                self.points = [(285, 218), (316, 172), (342, 201),
                               (386, 183), (369, 234), (321, 257)]
                self.closed = True
                self.go_to(STAGE_PATTERN)

        if self.points:
            self.pending_action = ("Das aktuelle Motiv und seine Einstellungen gehen verloren.", start)
        else:
            start()

    def request_exit(self):
        if self.points:
            self.pending_action = ("Beim Beenden geht das aktuelle Projekt verloren.", py5.exit_sketch)
        else:
            py5.exit_sketch()

    def clear_motif(self):
        def clear():
            self.points.clear()
            self.closed = False
            self.notice = "Die Zeichenfläche ist wieder frei."

        self.pending_action = ("Die gesetzten Punkte werden gelöscht.", clear)

    def close_motif(self):
        if self.has_area():
            self.closed = True
            self.notice = "Form geschlossen. Du kannst zum Muster wechseln."
        else:
            self.notice = "Setze drei Punkte, die kein gerades Segment bilden."

    def has_area(self):
        # Drei unterschiedliche, nicht kollineare Punkte ergeben eine zeichnbare Form.
        if len(self.points) < 3:
            return False
        ax, ay = self.points[0]
        direction = next((p for p in self.points if p != (ax, ay)), None)
        if direction is None:
            return False
        bx, by = direction
        return any((bx - ax) * (cy - ay) != (by - ay) * (cx - ax)
                   for cx, cy in self.points[1:])

    def label(self, value, x, y, size=15, color=INK):
        py5.fill(color)
        py5.text_size(size)
        py5.text(value, x, y)

    def button(self, value, x, y, width, action, *, enabled=True, active=False):
        hovered = x <= py5.mouse_x <= x + width and y <= py5.mouse_y <= y + 38
        py5.no_stroke()
        py5.fill(PURPLE if active else LILAC if hovered and enabled else "#F0EBF3")
        py5.rect(x, y, width, 38, 8)
        self.label(value, x + 13, y + 25, color=WHITE if active else INK if enabled else MUTED)
        if enabled:
            self.buttons.append((x, y, width, 38, action))

    def draw(self):
        self.buttons.clear()
        py5.background(PAPER)
        self.label("Textile Pattern Studio", 32, 48, 30)
        self.button("Start", 32, 66, 105, lambda: self.go_to(STAGE_HOME),
                    active=self.stage == STAGE_HOME)
        self.button("Motiv", 148, 66, 105, lambda: self.go_to(STAGE_DRAW),
                    active=self.stage == STAGE_DRAW)
        self.button("Muster", 264, 66, 105, lambda: self.go_to(STAGE_PATTERN),
                    active=self.stage == STAGE_PATTERN)
        self.button("Beenden", 860, 66, 108, self.request_exit)

        if self.stage == STAGE_HOME:
            self.draw_home()
        else:
            self.draw_workspace()
        if self.pending_action:
            self.draw_confirmation()

    def draw_home(self):
        py5.no_stroke()
        py5.fill(WHITE)
        py5.rect(32, 153, 936, 453, 14)
        self.label("Was willst du heute machen?", 64, 220, 32)
        self.label("Zeichne ein Motiv und wiederhole es zu einem textilen Muster.", 64, 258, 17, MUTED)
        self.button("Neues Projekt", 64, 299, 240, self.new_project, active=True)
        self.button("Aktuelles Projekt fortsetzen", 64, 351, 240,
                    lambda: self.go_to(STAGE_PATTERN if self.closed else STAGE_DRAW),
                    enabled=self.has_project)
        self.button("Beispielmuster ausprobieren", 64, 403, 240,
                    lambda: self.new_project(example=True))
        self.label("Dein Projekt bleibt bis zum Schliessen des Fensters verfügbar.",
                   64, 559, 15, MUTED)

    def draw_workspace(self):
        editing = self.stage == STAGE_DRAW
        self.label("Motiv zeichnen" if editing else "Muster entwickeln", 32, 148, 24)
        py5.stroke(LINE)
        py5.stroke_weight(1)
        py5.fill(WHITE)
        py5.rect(CANVAS_X, CANVAS_Y, CANVAS_WIDTH, CANVAS_HEIGHT)
        py5.push_matrix()
        py5.translate(CANVAS_X, CANVAS_Y)
        py5.clip(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
        if editing:
            self.draw_motif()
        elif self.closed:
            self.draw_pattern()
        else:
            self.label("Zeichne und schliesse zuerst ein Motiv.", 24, 44, 17, MUTED)
        py5.no_clip()
        py5.pop_matrix()

        if editing:
            self.label("Klick setzt einen Eckpunkt.", SIDEBAR_X, 192)
            self.label("Ziehen verschiebt einen Punkt.", SIDEBAR_X, 216)
            self.button("Form schliessen", SIDEBAR_X, 246, 218, self.close_motif,
                        enabled=len(self.points) >= 3 and not self.closed)
            self.button("Motiv löschen", SIDEBAR_X, 295, 218, self.clear_motif,
                        enabled=bool(self.points))
            self.button("Zum Muster", SIDEBAR_X, 344, 218,
                        lambda: self.go_to(STAGE_PATTERN), enabled=self.closed, active=self.closed)
        else:
            self.label("Zentrum zu Zentrum", SIDEBAR_X, 192, 16)
            self.draw_slider(0, "Horizontal", 253)
            self.draw_slider(1, "Vertikal", 334)
            self.button("Motiv bearbeiten", SIDEBAR_X, 380, 218,
                        lambda: self.go_to(STAGE_DRAW))
        self.label(self.notice, 32, 631, 15, MUTED)

    def draw_polygon(self, points, closed):
        py5.stroke(GREEN)
        py5.stroke_weight(2)
        if closed:
            py5.fill(LILAC)
        else:
            py5.no_fill()
        py5.begin_shape()
        for x, y in points:
            py5.vertex(x, y)
        if closed:
            py5.end_shape(py5.CLOSE)
        else:
            py5.end_shape()

    def draw_motif(self):
        if not self.points:
            self.label("Klicke auf die Fläche, um zu beginnen.", 24, 44, 17, MUTED)
            return
        if len(self.points) > 1:
            self.draw_polygon(self.points, self.closed)
        for index, (x, y) in enumerate(self.points):
            py5.no_stroke()
            py5.fill(PURPLE if index == 0 else GREEN)
            py5.circle(x, y, 10)

    def draw_pattern(self):
        # Das Zentrum ist der Mittelpunkt des umschliessenden Rechtecks.
        xs, ys = zip(*self.points)
        center_x = (min(xs) + max(xs)) / 2
        center_y = (min(ys) + max(ys)) / 2
        centered = [(x - center_x, y - center_y) for x, y in self.points]
        half_width = (max(xs) - min(xs)) / 2 + 2
        half_height = (max(ys) - min(ys)) / 2 + 2
        step_x, step_y = self.spacing
        origin_x, origin_y = CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2

        # Auch Motive mit Zentrum ausserhalb der Fläche können am Rand sichtbar sein.
        first_col = math.ceil((-half_width - origin_x) / step_x)
        last_col = math.floor((CANVAS_WIDTH + half_width - origin_x) / step_x)
        first_row = math.ceil((-half_height - origin_y) / step_y)
        last_row = math.floor((CANVAS_HEIGHT + half_height - origin_y) / step_y)
        for row in range(first_row, last_row + 1):
            for col in range(first_col, last_col + 1):
                py5.push_matrix()
                py5.translate(origin_x + col * step_x, origin_y + row * step_y)
                self.draw_polygon(centered, True)
                py5.pop_matrix()

    def draw_slider(self, index, title, y):
        self.label(f"{title}   {self.spacing[index]} px", SIDEBAR_X, y - 20)
        py5.stroke(LINE)
        py5.stroke_weight(4)
        py5.line(SIDEBAR_X, y, SIDEBAR_X + 210, y)
        fraction = (self.spacing[index] - MIN_SPACING) / (MAX_SPACING - MIN_SPACING)
        py5.no_stroke()
        py5.fill(PURPLE)
        py5.circle(SIDEBAR_X + 210 * fraction, y, 16)

    def update_slider(self, x):
        fraction = min(1, max(0, (x - SIDEBAR_X) / 210))
        self.spacing[self.dragged_slider] = round(MIN_SPACING + fraction * (MAX_SPACING - MIN_SPACING))

    def draw_confirmation(self):
        message, action = self.pending_action
        self.buttons.clear()
        py5.no_stroke()
        py5.fill(38, 29, 56, 140)
        py5.rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        py5.fill(WHITE)
        py5.rect(230, 223, 540, 194, 14)
        self.label("Änderungen verwerfen?", 255, 273, 24)
        self.label(message, 255, 307)
        self.button("Abbrechen", 255, 347, 142, self.cancel_confirmation)
        self.button("Verwerfen", 603, 347, 142, lambda: self.confirm(action), active=True)

    def cancel_confirmation(self):
        self.pending_action = None

    def confirm(self, action):
        self.cancel_confirmation()
        action()

    def mouse_pressed(self, x, y):
        for bx, by, width, height, action in self.buttons:
            if bx <= x <= bx + width and by <= y <= by + height:
                action()
                return
        if self.pending_action:
            return
        if self.stage == STAGE_DRAW:
            local_x, local_y = x - CANVAS_X, y - CANVAS_Y
            if 0 <= local_x <= CANVAS_WIDTH and 0 <= local_y <= CANVAS_HEIGHT:
                self.click_canvas(local_x, local_y)
        elif self.stage == STAGE_PATTERN and SIDEBAR_X - 8 <= x <= SIDEBAR_X + 218:
            for index, slider_y in enumerate((253, 334)):
                if abs(y - slider_y) <= 13:
                    self.dragged_slider = index
                    self.update_slider(x)
                    break

    def click_canvas(self, x, y):
        if self.points:
            nearest = min(range(len(self.points)), key=lambda i: math.dist(self.points[i], (x, y)))
            if math.dist(self.points[nearest], (x, y)) <= 8:
                self.dragged_point = nearest
                return
        if not self.closed:
            self.points.append((x, y))
            self.notice = ""

    def mouse_dragged(self, x, y):
        if self.dragged_slider is not None:
            self.update_slider(x)
        if self.dragged_point is not None:
            point = (min(CANVAS_WIDTH, max(0, x - CANVAS_X)),
                     min(CANVAS_HEIGHT, max(0, y - CANVAS_Y)))
            previous = self.points[self.dragged_point]
            self.points[self.dragged_point] = point
            if self.closed and not self.has_area():
                self.points[self.dragged_point] = previous

    def mouse_released(self):
        self.dragged_point = None
        self.dragged_slider = None


studio = Studio()


def settings():
    py5.size(WINDOW_WIDTH, WINDOW_HEIGHT)


def setup():
    py5.window_title("Textile Pattern Studio")
    py5.window_resizable(False)
    py5.frame_rate(30)


def draw():
    studio.draw()


def mouse_pressed():
    studio.mouse_pressed(py5.mouse_x, py5.mouse_y)


def mouse_dragged():
    studio.mouse_dragged(py5.mouse_x, py5.mouse_y)


def mouse_released():
    studio.mouse_released()



if __name__ == "__main__":
    py5.run_sketch()
