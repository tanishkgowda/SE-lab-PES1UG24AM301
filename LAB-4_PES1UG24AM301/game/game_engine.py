"""
GameEngine: owns the frog and all vehicles, and runs one frame's worth
of game logic.

Features: a 3-life system with a hit effect and respawn, a Game Over
state, goal/score tracking with a win state, and a 30-second countdown
per attempt. Collision detection lives in game/collisions.py.
"""

import math
import random
import time

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
SCORE_PER_CROSSING = 100
TIME_LIMIT = 30.0          # seconds per attempt
MAX_DT = 0.1               # cap on a single frame's elapsed time (guards against stalls)


class GameEngine:
    def __init__(self):
        self._build_entities()

    def _build_entities(self):
        self.lives = STARTING_LIVES
        self.hit_timer = 0          # frames left in the hit effect (0 = not being hit)
        self.game_over = False
        self.score = 0
        self.won = False
        self.time_left = TIME_LIMIT
        self._last_tick = time.perf_counter()
        self.hit_reason = None      # "vehicle" or "time", for the on-screen indication

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
        # R always works: restarts the whole game with full lives, score 0 and a fresh timer.
        if key == pygame.K_r:
            self._build_entities()
            return

        # No movement during the hit effect, after game over, or after winning.
        if self.game_over or self.won or self.hit_timer > 0:
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
        # Real elapsed time since the previous update (not frame counting).
        now = time.perf_counter()
        dt = min(now - self._last_tick, MAX_DT)
        self._last_tick = now

        # Vehicles keep moving the whole time, even during the hit effect.
        for v in self.vehicles:
            v.update(road_width_px=WIDTH)

        # After a win or game over: no collisions, no life changes, timer frozen.
        if self.game_over or self.won:
            return

        # Hit effect running: timer frozen, no collision checks, respawn when it ends.
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer == 0:
                self.frog.reset()
                self.hit_reason = None
                self._last_tick = time.perf_counter()   # new attempt starts now
            return

        if check_collision(self.frog, self.vehicles):
            self._lose_life("vehicle")
            return

        # Goal reached: register the crossing, add score, end the game.
        # Checked before the timer so reaching the goal always beats the clock.
        if self.frog.row == GOAL_ROW:
            self.score += SCORE_PER_CROSSING
            self.won = True
            return

        # Countdown for the current attempt.
        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0.0
            self._lose_life("time")

    def _lose_life(self, reason):
        self.lives -= 1
        self.hit_reason = reason
        if self.lives <= 0:
            self.game_over = True
        else:
            self.hit_timer = HIT_DURATION_FRAMES
            self.time_left = TIME_LIMIT      # each attempt gets its own 30 seconds

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.frog, self.vehicles)

        # Hit effect: frog turns red where it was hit (stays red on game over).
        if self.hit_timer > 0 or self.game_over:
            pygame.draw.rect(surface, (220, 40, 40),
                             self.frog.get_rect(CELL_SIZE), border_radius=6)

        renderer.draw_text(surface, font, f"Lives: {self.lives}", (10, 10))
        renderer.draw_text(surface, font, f"Time: {math.ceil(self.time_left)}", (WIDTH // 2 - 40, 10))
        renderer.draw_text(surface, font, f"Score: {self.score}", (WIDTH - 140, 10))
        renderer.draw_text(surface, font, "Arrow keys to move. R to restart.", (10, HEIGHT - 24))

        # Banners are drawn last so nothing covers them.
        if self.game_over:
            renderer.draw_banner(surface, "Game Over")
        elif self.won:
            renderer.draw_banner(surface, "You Won!")
        elif self.hit_timer > 0 and self.hit_reason == "time":
            renderer.draw_banner(surface, "Time's Up!", size=48)