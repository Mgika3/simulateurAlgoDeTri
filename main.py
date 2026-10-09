"""Simulateur graphique de tris, propulsé par Pygame."""

import random
import time

import pygame

from algorithmes import ALGORITHMS


WIDTH, HEIGHT = 1400, 750
SIDEBAR_WIDTH = 300
BG = (10, 15, 29)
PANEL = (17, 25, 44)
PANEL_ALT = (21, 31, 53)
EDGE = (37, 50, 76)
TEXT = (237, 242, 252)
MUTED = (135, 151, 178)
TEAL = (65, 224, 204)
PURPLE = (147, 120, 255)
GREEN = (83, 220, 158)
ORANGE = (255, 166, 106)


def rounded(surface, color, rect, radius=12, border=0, border_color=EDGE):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


class SortingVisualizer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("SORT LAB")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.fonts = {
            "tiny": pygame.font.SysFont("segoeui", 12),
            "small": pygame.font.SysFont("segoeui", 14),
            "body": pygame.font.SysFont("segoeui", 16),
            "medium": pygame.font.SysFont("segoeui", 19, bold=True),
            "title": pygame.font.SysFont("segoeui", 30, bold=True),
            "brand": pygame.font.SysFont("segoeui", 22, bold=True),
        }
        self.selected = 0
        self.data_size = 72
        self.normal_size = self.data_size
        self.speed = 42
        self.values = self._random_values(self.data_size)
        self.active = ()
        self.details = None
        self.generator = None
        self.history = []
        self.history_index = -1
        self.generator_exhausted = False
        self.running = False
        self.finished = False
        self.steps = 0
        self.elapsed = 0.0
        self.started_at = 0.0
        self.step_accumulator = 0.0
        self.sidebar_scroll = 0
        self.dragging = None
        self.toast = ""
        self.toast_until = 0.0
        self.running_loop = True

    @staticmethod
    def _random_values(count):
        return [random.randint(8, 100) for _ in range(count)]

    @property
    def algorithm(self):
        return ALGORITHMS[self.selected]

    @property
    def is_bogo(self):
        return self.algorithm[0] == "Bogosort"

    def show_toast(self, message):
        self.toast = message
        self.toast_until = time.monotonic() + 2.8

    def reset(self, shuffle=False):
        self.generator = None
        self.history = []
        self.history_index = -1
        self.generator_exhausted = False
        self.running = False
        self.finished = False
        self.active = ()
        self.details = None
        self.steps = 0
        self.elapsed = 0.0
        self.started_at = 0.0
        self.step_accumulator = 0.0
        if shuffle:
            random.shuffle(self.values)
        else:
            self.values = self._random_values(self.data_size)

    def select_algorithm(self, index):
        if index == self.selected:
            return
        was_bogo = self.is_bogo
        self.selected = index
        if self.is_bogo and not was_bogo:
            self.normal_size = self.data_size
            self.data_size = min(7, self.data_size)
            self.values = self._random_values(self.data_size)
            self.show_toast("Bogosort est limité à 7 valeurs pour rester interactif.")
        elif was_bogo and not self.is_bogo:
            self.data_size = self.normal_size
            self.values = self._random_values(self.data_size)
        self.reset()

    def start_or_pause(self):
        if self.running:
            self.running = False
            self.elapsed += time.monotonic() - self.started_at
            self.started_at = 0.0
            return
        if self.finished:
            self.reset()
        if self.generator is None:
            self._initialize_history()
        self.running = True
        self.started_at = time.monotonic()

    def _initialize_history(self):
        self.generator = self.algorithm[2].sort_steps(self.values)
        self.history = [(tuple(self.values), (), None)]
        self.history_index = 0
        self.generator_exhausted = False

    def _restore_history_state(self):
        values, self.active, self.details = self.history[self.history_index]
        self.values = list(values)
        self.steps = self.history_index
        self.finished = self.generator_exhausted and self.history_index == len(self.history) - 1

    def step_forward(self):
        if self.running:
            self.start_or_pause()
        if self.generator is None:
            self._initialize_history()
        self._advance_one_step()

    def _advance_one_step(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._restore_history_state()
            if self.finished and self.running:
                self.running = False
                self.elapsed += time.monotonic() - self.started_at
                self.started_at = 0.0
            return
        if self.generator_exhausted:
            return
        try:
            state = next(self.generator)
            snapshot, active = state[:2]
            details = state[2] if len(state) > 2 else None
            self.history.append((tuple(snapshot), tuple(active), details))
            self.history_index += 1
            self._restore_history_state()
        except StopIteration:
            self.generator_exhausted = True
            self.finished = True
            self.running = False
            self.active = ()
            if self.started_at:
                self.elapsed += time.monotonic() - self.started_at
            self.started_at = 0.0
            self.show_toast("Tri terminé ! Le tableau est ordonné.")

    def step_backward(self):
        if self.running:
            self.start_or_pause()
        if self.generator is None or self.history_index <= 0:
            return
        self.history_index -= 1
        self._restore_history_state()

    def set_size_from_x(self, x, track):
        count = 7 if self.is_bogo else 160
        low = 3 if self.is_bogo else 16
        fraction = max(0.0, min(1.0, (x - track.left) / max(1, track.width)))
        self.data_size = round(low + fraction * (count - low))
        self.values = self._random_values(self.data_size)
        if not self.is_bogo:
            self.normal_size = self.data_size
        self.reset()

    def set_speed_from_x(self, x, track):
        fraction = max(0.0, min(1.0, (x - track.left) / max(1, track.width)))
        self.speed = round(1 + fraction * 99)

    def update(self, dt):
        if not self.running:
            return
        self.step_accumulator += dt
        interval = 1.0 / self.speed
        steps_this_frame = min(120, int(self.step_accumulator / interval))
        if steps_this_frame < 1:
            return
        self.step_accumulator -= steps_this_frame * interval
        for _ in range(steps_this_frame):
            previous_steps = self.steps
            self._advance_one_step()
            if self.steps == previous_steps:
                self.running = False
                break

    def _draw_text(self, text, x, y, font="body", color=TEXT, surface=None):
        target = surface or self.screen
        rendered = self.fonts[font].render(str(text), True, color)
        target.blit(rendered, (int(x), int(y)))
        return rendered.get_rect(topleft=(int(x), int(y)))

    def _draw_sidebar(self, height):
        panel = pygame.Rect(0, 0, SIDEBAR_WIDTH, height)
        pygame.draw.rect(self.screen, (13, 20, 36), panel)
        pygame.draw.line(self.screen, EDGE, (SIDEBAR_WIDTH - 1, 0), (SIDEBAR_WIDTH - 1, height), 1)
        rounded(self.screen, (34, 57, 72), pygame.Rect(22, 24, 38, 38), 11)
        pygame.draw.line(self.screen, TEAL, (32, 44), (40, 52), 3)
        pygame.draw.line(self.screen, TEAL, (40, 52), (52, 34), 3)
        self._draw_text("SORT LAB", 72, 25, "brand")
        self._draw_text("ALGORITHMES DE TRI", 72, 54, "tiny", MUTED)
        rounded(self.screen, (22, 33, 54), pygame.Rect(20, 91, 260, 55), 12, 1)
        self._draw_text("16", 35, 101, "medium", TEAL)
        self._draw_text("algorithmes à explorer", 69, 106, "small", TEXT)
        self._draw_text("choisis une méthode pour commencer", 35, 125, "tiny", MUTED)
        self._draw_text("BIBLIOTHÈQUE", 24, 169, "tiny", MUTED)

        viewport = pygame.Rect(12, 194, SIDEBAR_WIDTH - 24, max(80, height - 253))
        row_height = 39
        content_height = len(ALGORITHMS) * row_height
        max_scroll = max(0, content_height - viewport.height)
        self.sidebar_scroll = max(0, min(max_scroll, self.sidebar_scroll))
        self.screen.set_clip(viewport)
        for index, (name, detail, _) in enumerate(ALGORITHMS):
            y = viewport.y + index * row_height - self.sidebar_scroll
            row = pygame.Rect(14, y, SIDEBAR_WIDTH - 28, 35)
            if index == self.selected:
                rounded(self.screen, (32, 48, 69), row, 9)
                pygame.draw.rect(self.screen, TEAL, pygame.Rect(row.x, row.y + 7, 3, 21), border_radius=2)
            self._draw_text(f"{index + 1:02d}", row.x + 11, row.y + 9, "tiny", TEAL if index == self.selected else MUTED)
            color = TEXT if index == self.selected else (185, 197, 216)
            self._draw_text(name, row.x + 43, row.y + 7, "small", color)
        self.screen.set_clip(None)
        if max_scroll:
            rail = pygame.Rect(SIDEBAR_WIDTH - 7, viewport.y, 3, viewport.height)
            pygame.draw.rect(self.screen, (27, 38, 58), rail, border_radius=2)
            thumb_h = max(32, int(viewport.height * viewport.height / content_height))
            thumb_y = viewport.y + int((viewport.height - thumb_h) * self.sidebar_scroll / max_scroll)
            pygame.draw.rect(self.screen, TEAL, (rail.x, thumb_y, rail.width, thumb_h), border_radius=2)
        self._draw_text("ESPACE  Lire / pause", 24, height - 43, "tiny", MUTED)

    def _draw_header(self, left, right):
        name, detail, _ = self.algorithm
        self._draw_text("ESPACE DE VISUALISATION  /  TRI", left, 25, "tiny", TEAL)
        self._draw_text(name, left, 48, "title")
        self._draw_text(detail, left + 2, 88, "small", MUTED)
        state = "EN COURS" if self.running else "TERMINÉ" if self.finished else "EN PAUSE" if self.generator else "PRÊT"
        state_color = GREEN if self.finished else TEAL if self.running else MUTED
        badge = pygame.Rect(right - 123, 45, 123, 34)
        rounded(self.screen, (24, 39, 57), badge, 17)
        pygame.draw.circle(self.screen, state_color, (badge.x + 15, badge.centery), 4)
        self._draw_text(state, badge.x + 27, badge.y + 9, "tiny", state_color)

    def _draw_stat_card(self, rect, label, value, accent):
        rounded(self.screen, PANEL, rect, 13, 1)
        self._draw_text(label.upper(), rect.x + 15, rect.y + 12, "tiny", MUTED)
        self._draw_text(value, rect.x + 15, rect.y + 34, "medium", accent)

    def _draw_chart(self, rect):
        rounded(self.screen, PANEL, rect, 16, 1)
        self._draw_text("TABLEAU DE DONNÉES", rect.x + 20, rect.y + 16, "small", TEXT)
        legend_y = rect.y + 20
        pygame.draw.circle(self.screen, TEAL, (rect.right - 148, legend_y + 3), 4)
        self._draw_text("valeurs", rect.right - 137, legend_y - 5, "tiny", MUTED)
        pygame.draw.circle(self.screen, ORANGE, (rect.right - 69, legend_y + 3), 4)
        self._draw_text("actives", rect.right - 59, legend_y - 5, "tiny", MUTED)
        has_details = self.algorithm[0] in ("Tri par base", "Tri par paquets", "Tri comptage")
        plot_width = int(rect.width * 0.54) if has_details else rect.width - 42
        plot = pygame.Rect(rect.x + 21, rect.y + 52, plot_width, rect.height - 77)
        for level in range(1, 5):
            y = plot.y + int(plot.height * level / 5)
            pygame.draw.line(self.screen, (31, 43, 65), (plot.x, y), (plot.right, y), 1)
        if not self.values:
            return
        minimum = min(self.values)
        maximum = max(self.values)
        span = max(1, maximum - minimum)
        gap = 2 if len(self.values) < 100 else 1
        bar_width = max(1, (plot.width - gap * (len(self.values) - 1)) // len(self.values))
        for index, value in enumerate(self.values):
            height = max(4, int((value - minimum + span * 0.12) / (span * 1.12) * (plot.height - 8)))
            x = plot.x + index * (bar_width + gap)
            y = plot.bottom - height
            if self.finished:
                color = GREEN
            else:
                ratio = index / max(1, len(self.values) - 1)
                color = tuple(int(TEAL[c] * (1 - ratio) + PURPLE[c] * ratio) for c in range(3))
            if index in self.active:
                color = ORANGE
            pygame.draw.rect(self.screen, color, (x, y, bar_width, height), border_radius=min(4, bar_width // 2))
        if has_details:
            detail_rect = pygame.Rect(plot.right + 14, rect.y + 48, rect.right - plot.right - 28, rect.height - 62)
            self._draw_bucket_details(detail_rect)

    def _draw_bucket_details(self, rect):
        rounded(self.screen, PANEL_ALT, rect, 12, 1)
        if not self.details:
            headings = {
                "Tri par base": "TRI PAR CHIFFRES",
                "Tri par paquets": "TRI PAR PAQUETS",
                "Tri comptage": "TRI COMPTAGE",
            }
            heading = headings[self.algorithm[0]]
            self._draw_text(heading, rect.x + 12, rect.y + 10, "tiny", TEAL)
            self._draw_text("Avance d’un pas pour voir la distribution.", rect.x + 12, rect.y + 34, "tiny", MUTED)
            return
        title = self.details["title"]
        subtitle = self.details["subtitle"]
        self._draw_text(title.upper(), rect.x + 12, rect.y + 9, "tiny", TEAL)
        self._draw_text(subtitle, rect.x + 12, rect.y + 27, "tiny", MUTED)
        if "counts" in self.details:
            counts = self.details["counts"]
            self._draw_text(f"{len(counts)} valeurs possibles", rect.x + 12, rect.y + 44, "tiny", MUTED)
            self._draw_count_details(rect, counts, self.details["current_value"])
            return
        buckets = self.details["buckets"]
        columns = min(5, len(buckets))
        rows = (len(buckets) + columns - 1) // columns
        gap = 5
        card_width = (rect.width - 20 - gap * (columns - 1)) // columns
        top = rect.y + 49
        card_height = max(34, (rect.bottom - top - gap * (rows - 1) - 8) // rows)
        for index, (label, values) in enumerate(buckets):
            column, row = index % columns, index // columns
            card = pygame.Rect(
                rect.x + 10 + column * (card_width + gap),
                top + row * (card_height + gap),
                card_width,
                card_height,
            )
            rounded(self.screen, (25, 38, 62), card, 6, 1)
            self._draw_text(label, card.x + 5, card.y + 4, "tiny", ORANGE)
            value_text = ", ".join(str(value) for value in values) or "—"
            font = self.fonts["tiny"]
            available_width = card.width - 10
            lines = []
            line = ""
            for value in value_text.split(", "):
                candidate = f"{line}, {value}" if line else value
                if font.size(candidate)[0] <= available_width:
                    line = candidate
                else:
                    if line:
                        lines.append(line)
                    line = value
            if line:
                lines.append(line)
            max_lines = max(1, (card.height - 23) // 13)
            if len(lines) > max_lines:
                lines = lines[:max_lines]
                lines[-1] = f"... +{len(values) - sum(len(line.split(', ')) for line in lines[:-1])}"
            for line_index, line in enumerate(lines):
                self._draw_text(line, card.x + 5, card.y + 20 + line_index * 13, "tiny", TEXT)

    def _draw_count_details(self, rect, counts, current_value):
        gap = 4
        inner_width = rect.width - 20
        columns = max(1, min(12, inner_width // 44))
        rows = (len(counts) + columns - 1) // columns
        top = rect.y + 63
        cell_height = max(14, min(24, (rect.bottom - top - 8) // max(1, rows)))
        cell_width = (inner_width - gap * (columns - 1)) // columns
        previous_clip = self.screen.get_clip()
        self.screen.set_clip(rect)
        for index, (value, count) in enumerate(counts):
            column, row = index % columns, index // columns
            cell = pygame.Rect(
                rect.x + 10 + column * (cell_width + gap),
                top + row * (cell_height + gap),
                cell_width,
                cell_height,
            )
            focused = value == current_value
            color = (71, 62, 53) if focused else (25, 38, 62)
            rounded(self.screen, color, cell, 4, 1, ORANGE if focused else EDGE)
            label = f"{value}:{count}"
            text = self.fonts["tiny"].render(label, True, TEXT if count else MUTED)
            self.screen.blit(text, text.get_rect(center=cell.center))
        self.screen.set_clip(previous_clip)

    def _draw_slider(self, label, value_text, track, value_fraction, accent):
        self._draw_text(label, track.x, track.y - 30, "small", TEXT)
        rendered = self.fonts["tiny"].render(value_text, True, accent)
        self.screen.blit(rendered, (track.right - rendered.get_width(), track.y - 29))
        pygame.draw.line(self.screen, (43, 56, 79), (track.left, track.centery), (track.right, track.centery), 4)
        fill_x = track.left + int(track.width * value_fraction)
        pygame.draw.line(self.screen, accent, (track.left, track.centery), (fill_x, track.centery), 4)
        pygame.draw.circle(self.screen, accent, (fill_x, track.centery), 8)
        pygame.draw.circle(self.screen, (237, 245, 255), (fill_x, track.centery), 3)

    def _draw_controls(self, rect):
        rounded(self.screen, PANEL, rect, 16, 1)
        button_y = rect.y + 34
        play = pygame.Rect(rect.x + 18, button_y, 135, 48)
        rounded(self.screen, (32, 184, 166) if self.running else (49, 205, 185), play, 12)
        label = "PAUSE" if self.running else "REPRENDRE" if self.generator and not self.finished else "LANCER LE TRI"
        text = self.fonts["small"].render(label, True, (8, 24, 31))
        self.screen.blit(text, text.get_rect(center=play.center))
        backward = pygame.Rect(rect.x + 162, button_y, 52, 48)
        forward = pygame.Rect(rect.x + 221, button_y, 52, 48)
        rounded(self.screen, PANEL_ALT, backward, 12, 1)
        rounded(self.screen, PANEL_ALT, forward, 12, 1)
        for button, label in ((backward, "< PAS"), (forward, "PAS >")):
            text = self.fonts["tiny"].render(label, True, TEXT)
            self.screen.blit(text, text.get_rect(center=button.center))
        shuffle = pygame.Rect(rect.x + 282, button_y, 111, 48)
        rounded(self.screen, PANEL_ALT, shuffle, 12, 1)
        text = self.fonts["small"].render("MÉLANGER", True, TEXT)
        self.screen.blit(text, text.get_rect(center=shuffle.center))
        reset = pygame.Rect(rect.x + 401, button_y, 102, 48)
        rounded(self.screen, PANEL_ALT, reset, 12, 1)
        text = self.fonts["small"].render("RÉINITIALISER", True, TEXT)
        self.screen.blit(text, text.get_rect(center=reset.center))
        slider_start = rect.x + 520
        available = max(190, rect.right - slider_start - 24)
        slider_width = max(100, (available - 54) // 2)
        size_track = pygame.Rect(slider_start, rect.y + 64, slider_width, 18)
        speed_track = pygame.Rect(slider_start + slider_width + 54, rect.y + 64, slider_width, 18)
        size_min, size_max = (3, 7) if self.is_bogo else (16, 160)
        size_fraction = (self.data_size - size_min) / max(1, size_max - size_min)
        speed_fraction = (self.speed - 1) / 99
        self._draw_slider("TAILLE DU TABLEAU", f"{self.data_size} valeurs", size_track, size_fraction, TEAL)
        self._draw_slider("VITESSE DE LECTURE", f"{self.speed} étapes/s", speed_track, speed_fraction, PURPLE)
        hint = ""
        if self.is_bogo:
            hint = "Mode expérimental : maximum 7 valeurs (temps aléatoire)."
        elif self.finished:
            hint = "Tri terminé. Mélange le tableau pour recommencer."
        elif self.running:
            hint = "Lecture en cours : espace / Pause. Flèches ← → : un pas."
        elif self.generator:
            hint = "‹ PAS / PAS › pour naviguer, espace pour reprendre."
        self._draw_text(hint, rect.x + 19, rect.y + 104, "tiny", MUTED)
        return play, backward, forward, shuffle, reset, size_track, speed_track

    def draw(self):
        width, height = self.screen.get_size()
        self.screen.fill(BG)
        self._draw_sidebar(height)
        left = SIDEBAR_WIDTH + 28
        right = width - 28
        content_width = right - left
        self._draw_header(left, right)
        stat_y = 128
        stat_gap = 12
        stat_w = (content_width - stat_gap * 3) // 4
        elapsed = self.elapsed + (time.monotonic() - self.started_at if self.running else 0)
        stats = (
            ("TAILLE", str(len(self.values)), TEAL),
            ("ÉTAPES", f"{self.steps:,}".replace(",", " "), PURPLE),
            ("TEMPS ÉCOULÉ", f"{elapsed:.1f} s", ORANGE),
            ("VITESSE", f"{self.speed} étapes/s", GREEN),
        )
        for index, (label, value, accent) in enumerate(stats):
            rect = pygame.Rect(left + index * (stat_w + stat_gap), stat_y, stat_w, 78)
            self._draw_stat_card(rect, label, value, accent)
        chart_y = 222
        controls_y = height - 181
        chart_rect = pygame.Rect(left, chart_y, content_width, max(235, controls_y - chart_y - 24))
        self._draw_chart(chart_rect)
        controls_rect = pygame.Rect(left, controls_y, content_width, 158)
        buttons = self._draw_controls(controls_rect)
        if self.toast and time.monotonic() < self.toast_until:
            toast_width = min(520, content_width - 30)
            toast = pygame.Rect(right - toast_width, 91, toast_width, 30)
            rounded(self.screen, (27, 47, 61), toast, 10, 1, (56, 89, 100))
            self._draw_text(self.toast, toast.x + 11, toast.y + 7, "tiny", TEAL)
        pygame.display.flip()
        return buttons

    def _handle_click(self, position):
        x, y = position
        height = self.screen.get_height()
        viewport = pygame.Rect(12, 194, SIDEBAR_WIDTH - 24, max(80, height - 253))
        if viewport.collidepoint(position):
            index = (y - viewport.y + self.sidebar_scroll) // 39
            if 0 <= index < len(ALGORITHMS):
                self.select_algorithm(index)
            return
        left = SIDEBAR_WIDTH + 28
        controls = pygame.Rect(left, height - 181, self.screen.get_width() - left - 28, 158)
        if not controls.collidepoint(position):
            return
        play, backward, forward, shuffle, reset, size_track, speed_track = self._control_geometry(controls)
        if play.collidepoint(position):
            self.start_or_pause()
        elif backward.collidepoint(position):
            self.step_backward()
        elif forward.collidepoint(position):
            self.step_forward()
        elif shuffle.collidepoint(position):
            self.reset(shuffle=True)
        elif reset.collidepoint(position):
            self.reset()
        elif size_track.inflate(0, 36).collidepoint(position):
            self.dragging = "size"
            self.set_size_from_x(x, size_track)
        elif speed_track.inflate(0, 36).collidepoint(position):
            self.dragging = "speed"
            self.set_speed_from_x(x, speed_track)

    def _control_geometry(self, rect):
        button_y = rect.y + 34
        play = pygame.Rect(rect.x + 18, button_y, 135, 48)
        backward = pygame.Rect(rect.x + 162, button_y, 52, 48)
        forward = pygame.Rect(rect.x + 221, button_y, 52, 48)
        shuffle = pygame.Rect(rect.x + 282, button_y, 111, 48)
        reset = pygame.Rect(rect.x + 401, button_y, 102, 48)
        slider_start = rect.x + 520
        available = max(190, rect.right - slider_start - 24)
        slider_width = max(100, (available - 54) // 2)
        size_track = pygame.Rect(slider_start, rect.y + 64, slider_width, 18)
        speed_track = pygame.Rect(slider_start + slider_width + 54, rect.y + 64, slider_width, 18)
        return play, backward, forward, shuffle, reset, size_track, speed_track

    def run(self):
        while self.running_loop:
            dt = self.clock.tick(60) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running_loop = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running_loop = False
                    elif event.key == pygame.K_SPACE:
                        self.start_or_pause()
                    elif event.key == pygame.K_LEFT:
                        self.step_backward()
                    elif event.key == pygame.K_RIGHT:
                        self.step_forward()
                    elif event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_n:
                        self.reset(shuffle=True)
                elif event.type == pygame.MOUSEWHEEL:
                    if pygame.mouse.get_pos()[0] < SIDEBAR_WIDTH:
                        self.sidebar_scroll -= event.y * 39
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging = None
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    height = self.screen.get_height()
                    controls = pygame.Rect(SIDEBAR_WIDTH + 28, height - 181, self.screen.get_width() - SIDEBAR_WIDTH - 56, 158)
                    _, _, _, _, _, size_track, speed_track = self._control_geometry(controls)
                    if self.dragging == "size":
                        self.set_size_from_x(event.pos[0], size_track)
                    else:
                        self.set_speed_from_x(event.pos[0], speed_track)
            self.update(dt)
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    SortingVisualizer().run()
