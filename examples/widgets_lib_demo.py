import decorator_lib
import handler_lib
import widget_lib
import pygame


class Handler(handler_lib.Handler):
    def handle_event(self, event):
        handler_lib.Handler.handle_event(self, event)

        global pressed

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                quit()

        elif event.type == pygame.MOUSEMOTION:
            box = self.window.find_name("box")

            if pressed is True or box.get_local_position(self.mouse_position, "bottomright").magnitude() <= 10:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZENWSE)

            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

            if pressed is None:
                pass

            elif pressed is True:
                size = box.get_local_position(self.mouse_position, "topleft")

                size.x = max(size.x, 40)
                size.y = max(size.y, 40)

                box.set_size(size)
                box.update_surface()

            else:
                box.set_full_position(self.mouse_position, pressed)

        elif event.type == pygame.MOUSEBUTTONUP:
            pressed = None

        elif event.type == pygame.MOUSEBUTTONDOWN:
            box = self.window.find_name("box")
            text = self.window.find_name("text")

            position = box.get_local_position(self.mouse_position)

            if box.get_local_position(self.mouse_position, "bottomright").magnitude() <= 10:
                pressed = True
                text.set_text((
                    "Resizing"
                ))

            elif box.is_position_on(self.mouse_position):
                pressed = position
                text.set_text(
                    (
                        f"Pressed: {position}"
                    )
                )


widget_lib.init(widget_lib.DEBUG_SURFACE_UPDATES)

box_decorators = (
    decorator_lib.RoundedSurface(
        radius={"topleft": 7, "topright": 7, "bottomleft": 7, "bottomright": 0},
    ),
)

basic_decorators = (
    decorator_lib.RoundedSurface(
        radius={"topleft": 7, "topright": 7, "bottomleft": 7, "bottomright": 7},
    ),
)

window = widget_lib.Window(
    children=(
        widget_lib.SinglePointAlignmentWidget(
            name="box",
            shift=(0, 0),
            background_color=(100, 100, 100),
            alignment="topleft",
            parent_alignment="center",
            decorators=box_decorators
        ),
        widget_lib.TextWidget(
            name="text",
            shift=(-10, 10),
            text="Cool\nHi!",
            separation=0,
            font=widget_lib.FontStyling(),
            background_color=(200, 200, 200, 100),
            alignment="topright",
            parent_alignment="topright",
            padding=pygame.Vector2(20, 20),
            text_alignment="left",
            decorators=basic_decorators
        ),
        widget_lib.SinglePointAlignmentWidget(
            size=(200, 80),
            shift=(10, 10),
            name="button",
            background_color=(200, 200, 200, 100),
            decorators=basic_decorators
        )
    ),
    size=(500, 500),
    background_color=(240, 240, 240),
    flags=pygame.RESIZABLE
)

print(window.get_tree())
window.find_name("box").set_size((100, 100))

handler = Handler(window)

pressed = None

while True:
    handler.check_events()

    window.render()
