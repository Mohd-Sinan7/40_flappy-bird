import pygame
from .bird import Bird
from .pipe import Pipe
from .sound import SoundManager

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)

# Difficulty presets: pipe speed (px/frame) and gap height (px).
DIFFICULTIES = {
    "Easy":   {"speed": 3, "gap": 200},
    "Medium": {"speed": 4, "gap": 150},
    "Hard":   {"speed": 6, "gap": 120},
}
DEFAULT_DIFFICULTY = "Medium"
PIPE_SPACING = 360  # horizontal distance between pipes, kept constant across difficulties


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)

        self.sounds = SoundManager()
        self._build_menu_buttons()
        self.reset(DEFAULT_DIFFICULTY)

    # ------------------------------------------------------------------ setup
    def reset(self, difficulty):
        """Start a fresh game with the chosen difficulty."""
        self.difficulty = difficulty
        settings = DIFFICULTIES[difficulty]
        self.pipe_speed = settings["speed"]
        self.pipe_gap = settings["gap"]
        self.pipe_interval = round(PIPE_SPACING / self.pipe_speed)  # frames between spawns

        self.bird = Bird(self.width // 4, self.height // 2)
        self._spawn_timer = 0
        self.pipes = [Pipe(self.width + 100, self.height, gap=self.pipe_gap, speed=self.pipe_speed)]

        self.score = 0
        self.game_over = False

    def _build_menu_buttons(self):
        """Clickable difficulty buttons shown on the Game Over screen."""
        btn_w, btn_h, spacing = 260, 48, 14
        top = self.height // 2 + 40
        self.menu_buttons = []
        for i, name in enumerate(DIFFICULTIES):
            rect = pygame.Rect(0, 0, btn_w, btn_h)
            rect.center = (self.width // 2, top + i * (btn_h + spacing) + btn_h // 2)
            self.menu_buttons.append((name, rect))

    # ------------------------------------------------------------------ input
    def handle_event(self, event):
        if self.game_over:
            self._handle_game_over_event(event)
            return

        # Flap is edge-triggered (KEYDOWN / MOUSEBUTTONDOWN), not held.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._flap()
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._flap()

    def _flap(self):
        self.bird.flap()
        self.sounds.flap()

    def _end_game(self):
        """Mark the game as over (and play the death sound exactly once)."""
        if not self.game_over:
            self.game_over = True
            self.sounds.die()

    def _handle_game_over_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_1:
                self.reset("Easy")
            elif event.key == pygame.K_2:
                self.reset("Medium")
            elif event.key == pygame.K_3:
                self.reset("Hard")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self.menu_buttons:
                if rect.collidepoint(event.pos):
                    self.reset(name)
                    break

    def handle_input(self):
        # Reserved for continuously-held-key input; flapping is handled
        # in handle_event instead, so there's nothing to poll here.
        pass

    # ----------------------------------------------------------------- update
    def update(self):
        if self.game_over:
            return

        self.bird.update()

        if self.bird.y - self.bird.radius <= 0 or self.bird.y + self.bird.radius >= self.height:
            self._end_game()
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0
            self.pipes.append(Pipe(self.width, self.height, gap=self.pipe_gap, speed=self.pipe_speed))

        for pipe in self.pipes:
            pipe.move()

            # Collision uses the bird's full circular body (not just its
            # center point), so clipping a pipe edge is always detected.
            if self.bird.collides_with_rect(pipe.top_rect()) or self.bird.collides_with_rect(pipe.bottom_rect()):
                self._end_game()

            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1
                self.sounds.score()

        self.pipes = [p for p in self.pipes if not p.off_screen()]

    # ----------------------------------------------------------------- render
    def render(self, screen):
        for pipe in self.pipes:
            pygame.draw.rect(screen, GREEN, pipe.top_rect())
            pygame.draw.rect(screen, GREEN, pipe.bottom_rect())

        pygame.draw.circle(screen, WHITE, (int(self.bird.x), int(self.bird.y)), self.bird.radius)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        mode_text = self.small_font.render(self.difficulty, True, WHITE)
        screen.blit(mode_text, mode_text.get_rect(topright=(self.width - 10, 12)))

        if self.game_over:
            self._render_game_over(screen)

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        lines = [
            (self.big_font, "GAME OVER", (255, 80, 80), self.height // 2 - 130),
            (self.font, f"Final Score: {self.score}", WHITE, self.height // 2 - 70),
            (self.small_font, "Play again - choose difficulty:", WHITE, self.height // 2 + 10),
        ]
        for font, text, color, y in lines:
            surf = font.render(text, True, color)
            screen.blit(surf, surf.get_rect(center=(self.width // 2, y)))

        mouse_pos = pygame.mouse.get_pos()
        for i, (name, rect) in enumerate(self.menu_buttons, start=1):
            hovered = rect.collidepoint(mouse_pos)
            pygame.draw.rect(screen, (60, 170, 60) if hovered else (40, 120, 40), rect, border_radius=8)
            pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=8)
            label = self.small_font.render(f"[{i}] {name}", True, WHITE)
            screen.blit(label, label.get_rect(center=rect.center))

        hint = self.small_font.render("Press ESC or Q to exit", True, WHITE)
        screen.blit(hint, hint.get_rect(center=(self.width // 2, self.height - 60)))
