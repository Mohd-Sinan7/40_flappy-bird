import pygame
from .bird import Bird
from .pipe import Pipe

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.bird = Bird(width // 4, height // 2)
        self.pipe_speed = 4
        self.pipe_interval = 90  # frames between pipe spawns
        self._spawn_timer = 0
        self.pipes = [Pipe(width + 100, height, speed=self.pipe_speed)]

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 56, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.game_over = False

    def handle_event(self, event):
        if self.game_over:
            # Game Over screen: wait for input. ESC / Q requests quit.
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            return

        # Flap is edge-triggered (KEYDOWN / MOUSEBUTTONDOWN), not held.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.bird.flap()
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bird.flap()

    def handle_input(self):
        # Reserved for continuously-held-key input; flapping is handled
        # in handle_event instead, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self.bird.update()

        if self.bird.y - self.bird.radius <= 0 or self.bird.y + self.bird.radius >= self.height:
            self.game_over = True
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0
            self.pipes.append(Pipe(self.width, self.height, speed=self.pipe_speed))

        for pipe in self.pipes:
            pipe.move()

            # Collision uses the bird's full circular body (not just its
            # center point), so clipping a pipe edge is always detected.
            if self.bird.collides_with_rect(pipe.top_rect()) or self.bird.collides_with_rect(pipe.bottom_rect()):
                self.game_over = True

            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1

        self.pipes = [p for p in self.pipes if not p.off_screen()]

    def render(self, screen):
        for pipe in self.pipes:
            pygame.draw.rect(screen, GREEN, pipe.top_rect())
            pygame.draw.rect(screen, GREEN, pipe.bottom_rect())

        pygame.draw.circle(screen, WHITE, (int(self.bird.x), int(self.bird.y)), self.bird.radius)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            self._render_game_over(screen)

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        lines = [
            (self.big_font, "GAME OVER", (255, 80, 80), self.height // 2 - 80),
            (self.font, f"Final Score: {self.score}", WHITE, self.height // 2),
            (self.small_font, "Press ESC or Q to quit", WHITE, self.height // 2 + 60),
        ]
        for font, text, color, y in lines:
            surf = font.render(text, True, color)
            screen.blit(surf, surf.get_rect(center=(self.width // 2, y)))
