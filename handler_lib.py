import pygame

import widget_lib


class Handler:
    mouse_position: pygame.Vector2
    mouse_velocity: pygame.Vector2

    running: bool = False

    def __init__(self, window):
        self.window: widget_lib.Window = window

    def run(self):
        if self.running:
            raise ValueError("Handler was already running")

        self.running = True

        while self.running:
            self.frame()

    def frame(self):
        self.mouse_position = pygame.Vector2(pygame.mouse.get_pos())
        self.mouse_velocity = pygame.Vector2(pygame.mouse.get_rel())

        self.check_events()

        self.window.render()

    def check_events(self):
        for event in pygame.event.get():
            self.handle_event(event)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == pygame.WINDOWRESIZED:
            self.window.set_size(pygame.Vector2(event.x, event.y))
