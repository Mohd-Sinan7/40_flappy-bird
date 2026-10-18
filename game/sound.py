import math
import array
import pygame


class SoundManager:
    """Generates and plays the game's sound effects.

    The sounds are synthesized in code (no asset files needed). If audio
    cannot be initialised (no sound device, etc.) every method becomes a
    silent no-op so the game still runs.
    """

    def __init__(self):
        self.enabled = False
        self.flap_sound = self.score_sound = self.die_sound = None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(22050, -16, 1)
            self.freq, fmt, self.channels = pygame.mixer.get_init()
            if fmt != -16:  # we only synthesize signed 16-bit samples
                return
            self.flap_sound = self._make([(400, 800, 0.08)], volume=0.35)
            self.score_sound = self._make([(880, 880, 0.07), (1320, 1320, 0.12)], volume=0.35)
            self.die_sound = self._make([(500, 120, 0.50)], volume=0.4)
            self.enabled = True
        except (pygame.error, NotImplementedError):
            self.enabled = False

    def _make(self, segments, volume=0.4):
        """Build a pygame Sound from (start_hz, end_hz, seconds) tone segments."""
        samples = array.array("h")
        phase = 0.0
        for start_hz, end_hz, seconds in segments:
            n = int(self.freq * seconds)
            for i in range(n):
                t = i / n
                hz = start_hz + (end_hz - start_hz) * t
                phase += 2 * math.pi * hz / self.freq
                envelope = 1.0 - t  # fade out to avoid clicks
                value = int(32767 * volume * envelope * math.sin(phase))
                for _ in range(self.channels):
                    samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _play(self, sound):
        if self.enabled and sound is not None:
            sound.play()

    def flap(self):
        self._play(self.flap_sound)

    def score(self):
        self._play(self.score_sound)

    def die(self):
        self._play(self.die_sound)
