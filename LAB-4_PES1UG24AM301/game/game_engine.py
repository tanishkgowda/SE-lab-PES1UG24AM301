"""
GameEngine: owns the frog and all vehicles, and runs one frame's worth
of game logic.

Starter version: the frog can move, hop across the road, and reach the
goal. Task 2 adds a 3-life system, a hit effect and respawn, and a
Game Over state. Collision detection lives in game/collisions.py.
"""

import random

import pygame

from game.frog import Frog
from game.vehicle import Vehicle
from game.collisions import check_collision
from game.renderer import (
    GRID_COLS, GRID_ROWS, GOAL_ROW, ROAD_ROWS, START_ROW, CELL_SIZE, WIDTH, HEIGHT,
)

LANE_SPEEDS = [1.5, -2, 2, -2.5, 1.5, -2]   # one entry per road row, alternating direction

STARTING_LIVES = 3
HIT_DURATION_FRAMES = 45   # ~0.75 s at 60 FPS; the game logic is frame-based like vehicle speeds


class GameEngine:
    def __init__(self):
        self._build_entities()

    def _build_entities(self):
        self.lives = STARTING_LIVES
        self.hit_timer = 0          # frames left in the hit effect (0 = not being hit)
        self.game_over = False

        start_col = GRID_COLS // 2
        self.frog = Frog(
            col=start_col, row=START_ROW,
            start_col=start_col, start_row=START_ROW,
            cols=GRID_COLS, start_row_limit=START_ROW,
        )
        frog_x_range = (start_col * CELL_SIZE, start_col * CELL_SIZE + CELL_SIZE)

        self.vehicles = []
        for i, row in enumerate(ROAD_ROWS):
            speed = LANE_SPEEDS[i % len(LANE_SPEEDS)]
            vehicle_width = 40 if i % 2 == 0 else 70   # mix of cars and wider trucks
            spacing = 300
            count = 2

            # Try a few random phases and keep the first one that doesn't
            # already overlap the frog's starting column - guarantees a
            # safe first lane instead of leaving it to chance.
            for _attempt in range(20):
                phase = random.randint(0, spacing - 1)
                positions = []
                safe = True
                for n in range(count):
                    offset = phase + n * spacing
                    x = offset if speed > 0 else WIDTH - offset - vehicle_width
                    positions.append(x)
                    if not (x + vehicle_width <= frog_x_range[0] or x >= frog_x_range[1]):
                        safe = False
                if safe:
                    break

            for x in positions:
                self.vehicles.append(Vehicle(x=x, row=row, width=vehicle_width,
                                              height=CELL_SIZE - 8, speed=speed))

    def handle_keydown(self, key):
        # R always works: restarts the whole game with full lives.
        if key == pygame.K_r:
            self._build_entities()
            return

        # No movement during the hit effect or after game over.
        if self.game_over or self.hit_timer > 0:
            return

        if key == pygame.K_UP:
            self.frog.move(0, -1)
        elif key == pygame.K_DOWN:
            self.frog.move(0, 1)
        elif key == pygame.K_LEFT:
            self.frog.move(-1, 0)
        elif key == pygame.K_RIGHT:
            self.frog.move(1, 0)

    def update(self):
        # Vehicles keep moving the whole time, even during the hit effect.
        for v in self.vehicles:
            v.update(road_width_px=WIDTH)

        if self.game_over:
            return

        # Hit effect running: no collision checks, then respawn when it ends.
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer == 0:
                self.frog.reset()
            return

        if check_collision(self.frog, self.vehicles):
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.hit_timer = HIT_DURATION_FRAMES
            return

        if self.frog.row == GOAL_ROW:
            self.frog.reset()

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.frog, self.vehicles)

        # Hit effect: frog turns red where it was hit (stays red on game over).
        if self.hit_timer > 0 or self.game_over:
            pygame.draw.rect(surface, (220, 40, 40),
                             self.frog.get_rect(CELL_SIZE), border_radius=6)

        renderer.draw_text(surface, font, f"Lives: {self.lives}", (10, 10))
        renderer.draw_text(surface, font, "Arrow keys to move. R to restart.", (10, HEIGHT - 24))

        if self.game_over:
            msg = "GAME OVER - press R to restart"
            w, h = font.size(msg)
            x, y = (WIDTH - w) // 2, HEIGHT // 2 - h // 2
            pygame.draw.rect(surface, (0, 0, 0), (x - 12, y - 8, w + 24, h + 16))
            renderer.draw_text(surface, font, msg, (x, y))