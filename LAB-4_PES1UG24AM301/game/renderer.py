"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

CELL_SIZE = 50
GRID_COLS = 12
GRID_ROWS = 8

WIDTH = CELL_SIZE * GRID_COLS
HEIGHT = CELL_SIZE * GRID_ROWS
WINDOW_SIZE = (WIDTH, HEIGHT)

GOAL_ROW = 0
ROAD_ROWS = list(range(1, GRID_ROWS - 1))   # rows 1..6
START_ROW = GRID_ROWS - 1                     # row 7

COLOR_BG = (20, 20, 25)
COLOR_GOAL = (40, 130, 60)
COLOR_ROAD = (45, 45, 50)
COLOR_START = (40, 90, 60)
COLOR_LANE_LINE = (90, 90, 90)
COLOR_FROG = (80, 220, 100)
COLOR_VEHICLE = (220, 80, 70)
COLOR_TEXT = (255, 255, 255)


def draw_scene(surface, frog, vehicles):
    surface.fill(COLOR_BG)

    for row in range(GRID_ROWS):
        rect = pygame.Rect(0, row * CELL_SIZE, WIDTH, CELL_SIZE)
        if row == GOAL_ROW:
            pygame.draw.rect(surface, COLOR_GOAL, rect)
        elif row == START_ROW:
            pygame.draw.rect(surface, COLOR_START, rect)
        else:
            pygame.draw.rect(surface, COLOR_ROAD, rect)
            pygame.draw.line(surface, COLOR_LANE_LINE, (0, row * CELL_SIZE), (WIDTH, row * CELL_SIZE), 1)

    for v in vehicles:
        pygame.draw.rect(surface, COLOR_VEHICLE, v.get_rect(CELL_SIZE), border_radius=6)

    pygame.draw.rect(surface, COLOR_FROG, frog.get_rect(CELL_SIZE), border_radius=8)


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, text, size=72, color=(255, 220, 80)):
    """Large, centered message on a dark panel."""
    big_font = pygame.font.Font(None, size)
    label = big_font.render(text, True, color)
    rect = label.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    panel = rect.inflate(60, 40)
    pygame.draw.rect(surface, (0, 0, 0), panel, border_radius=12)
    pygame.draw.rect(surface, color, panel, width=3, border_radius=12)
    surface.blit(label, rect)