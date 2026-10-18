import pygame

class Bird:
    def __init__(self, x, y, radius=15):
        self.x = x
        self.y = y
        self.radius = radius
        self.velocity = 0
        self.gravity = 0.5
        self.flap_strength = -8

    def flap(self):
        self.velocity = self.flap_strength

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity

    def center(self):
        return (self.x, self.y)

    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def collides_with_rect(self, rect):
        """Circle-vs-rectangle collision using the bird's full radius.

        Finds the point on the rectangle closest to the bird's center and
        checks whether it lies within one radius of the center.
        """
        closest_x = max(rect.left, min(self.x, rect.right))
        closest_y = max(rect.top, min(self.y, rect.bottom))
        dx = self.x - closest_x
        dy = self.y - closest_y
        return dx * dx + dy * dy <= self.radius * self.radius
