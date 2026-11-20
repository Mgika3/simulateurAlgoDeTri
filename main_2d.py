import math

import pygame

from main import (
    MUTED,
    PANEL,
    PANEL_ALT,
    PURPLE,
    YELLOW,
    ORANGE,
    EDGE,
    SortingVisualizer,
    rounded,
    RED,
)


class SortingVisualizer2D(SortingVisualizer):
    def __init__(self):
        super().__init__()
        self.item_label = "points"
        self.size_label = "NUAGE"
        pygame.display.set_caption("SORT LAB — 2D")

    def _draw_chart(self, rect):
        rounded(self.screen, PANEL, rect, 16, 1)
        self._draw_text("GRILLE DE POINTS 2D", rect.x + 20, rect.y + 16, "small")
        legend_y = rect.y + 20
        pygame.draw.circle(self.screen, RED, (rect.right - 190, legend_y + 3), 4)
        self._draw_text("faible", rect.right - 180, legend_y - 5, "tiny", MUTED)
        pygame.draw.circle(self.screen, YELLOW, (rect.right - 125, legend_y + 3), 4)
        self._draw_text("élevée", rect.right - 115, legend_y - 5, "tiny", MUTED)
        pygame.draw.circle(self.screen, ORANGE, (rect.right - 48, legend_y + 3), 4)
        self._draw_text("active", rect.right - 38, legend_y - 5, "tiny", MUTED)

        has_details = self.algorithm[0] in ("Tri par base", "Tri par paquets", "Tri comptage")
        plot_width = int(rect.width * 0.54) if has_details else rect.width - 42
        plot = pygame.Rect(rect.x + 21, rect.y + 52, plot_width, rect.height - 77)
        rounded(self.screen, PANEL_ALT, plot, 10)

        if self.values:
            initial_values = self.history[0][0] if self.history else self.values
            minimum = min(initial_values)
            span = max(1, max(initial_values) - minimum)
            columns = max(1, math.ceil(math.sqrt(len(self.values) * plot.width / max(1, plot.height))))
            rows = math.ceil(len(self.values) / columns)
            cell_width = plot.width / columns
            cell_height = plot.height / rows
            radius = max(2, int(min(cell_width, cell_height) * 0.34))

            for index, value in enumerate(self.values):
                column, row = index % columns, index // columns
                center = (
                    round(plot.x + (column + 0.5) * cell_width),
                    round(plot.y + (row + 0.5) * cell_height),
                )
                ratio = max(0.0, min(1.0, (value - minimum) / span))
                color = tuple(
                    round(RED[channel] * (1 - ratio) + YELLOW[channel] * ratio)
                    for channel in range(3)
                )
                if index in self.active:
                    color = ORANGE
                    pygame.draw.circle(self.screen, (255, 226, 194), center, radius + 2)
                pygame.draw.circle(self.screen, color, center, radius)

        if has_details:
            detail_rect = pygame.Rect(
                plot.right + 14,
                rect.y + 48,
                rect.right - plot.right - 28,
                rect.height - 62,
            )
            self._draw_bucket_details(detail_rect)


if __name__ == "__main__":
    SortingVisualizer2D().run()
