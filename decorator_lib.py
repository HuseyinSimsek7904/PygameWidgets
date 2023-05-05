import typing

import pygame

import widget_lib


class Decorator:
    def overwrite(self, widget):
        for method_name in self.__dir__():
            if not method_name.startswith("overwrite_"):
                continue

            function = getattr(self, method_name)
            options = self.__dict__

            setattr(widget, method_name[10:], lambda: function(widget, **options))


class RectAlignment(Decorator):
    """
    Works with all the widgets since all of them contain primer, seconder and full rect attributes.
    """

    def __init__(self, alignments):
        print(alignments.keys())


class RoundedSurface(Decorator):
    """
    Works with all the widgets since all of them contain surface and size attributes.
    Adds basic decorations for widgets.
    """

    def __init__(
            self,
            radius: int | dict = 10,
    ):
        if type(radius) is int:
            self.topleft_radius = radius
            self.topright_radius = radius
            self.bottomleft_radius = radius
            self.bottomright_radius = radius

        elif type(radius) is dict:
            self.topleft_radius = radius["topleft"]
            self.topright_radius = radius["topright"]
            self.bottomleft_radius = radius["bottomleft"]
            self.bottomright_radius = radius["bottomright"]

        else:
            raise ValueError("Invalid radius parameters")

    @staticmethod
    def overwrite_reset_surface(self, topleft_radius, topright_radius, bottomleft_radius, bottomright_radius, **kwargs):
        self.update_size()
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0))

        if self.background_color is not None:
            pygame.draw.circle(self.surface, self.background_color, (topleft_radius, topleft_radius),
                               topleft_radius)
            pygame.draw.circle(self.surface, self.background_color,
                               (self.size.x - topright_radius, topright_radius),
                               topright_radius)
            pygame.draw.circle(self.surface, self.background_color,
                               (bottomleft_radius, self.size.y - bottomleft_radius), bottomleft_radius)
            pygame.draw.circle(self.surface, self.background_color,
                               (self.size.x - bottomright_radius, self.size.y - bottomright_radius),
                               bottomright_radius)

            pygame.draw.polygon(self.surface, self.background_color, (
                (topleft_radius, 0),
                (self.size.x - topright_radius, 0),
                (self.size.x, topright_radius),
                (self.size.x, self.size.y - bottomright_radius),
                (self.size.x - bottomright_radius, self.size.y),
                (bottomleft_radius, self.size.y),
                (0, self.size.y - bottomleft_radius),
                (0, topleft_radius)
            ))


class SurfaceLoader(Decorator):
    def __init__(
            self,
            surface
    ):
        self.surface = surface

    @staticmethod
    def overwrite_reset_surface(self, surface, **kwargs):
        self.update_size()
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)

        if self.background_color is not None:
            self.surface.fill(self.background_color)

        if widget_lib.debug_flags & widget_lib.DEBUG_SURFACE_UPDATES:
            pygame.draw.rect(self.surface, (0, 0, 0), ((0, 0), self.surface.get_size()), width=1)


class ImageLoader(SurfaceLoader):
    def __init__(
            self,
            source
    ):
        SurfaceLoader.__init__(self, pygame.image.load(source))
