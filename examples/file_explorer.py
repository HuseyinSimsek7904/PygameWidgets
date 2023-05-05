import decorator_lib
import handler_lib
import widget_lib
import pygame
import os


class FileExplorer(handler_lib.Handler):
    old_button: widget_lib.TextWidget = None

    def __init__(self):
        handler_lib.Handler.__init__(
            self, widget_lib.Window(
                size=(1, 1),
                background_color=(50, 50, 50),
                flags=pygame.RESIZABLE,
                children=(
                    widget_lib.DoublePointAlignmentParentWidget(
                        name="path menu",
                        background_color=(100, 100, 100),
                        children=(
                            widget_lib.TextWidget(
                                name="path text",
                                shift=pygame.Vector2(PADDING, 0),
                                alignment="midleft",
                                parent_alignment="midleft",
                                text_alignment="topleft",
                                font=FONT,
                                text=()
                            ),
                        ),
                        decorators=ROUNDED_DECORATOR,
                        p1_shift=pygame.Vector2(PADDING, PADDING),
                        p1_alignment="topleft",
                        p1_parent_alignment="topleft",

                        p2_shift=pygame.Vector2(-PADDING, PATH_MENU_HEIGHT + PADDING),
                        p2_alignment="topright",
                        p2_parent_alignment="topright",
                    ),
                    widget_lib.DoublePointAlignmentParentWidget(
                        name="pinned menu",

                        p1_shift=pygame.Vector2(PADDING, PATH_MENU_HEIGHT + 2 * PADDING),
                        p1_alignment="topleft",
                        p1_parent_alignment="topleft",

                        p2_shift=pygame.Vector2(PINNED_MENU_WIDTH - PADDING - LINE_WIDTH, -PADDING),
                        p2_alignment="bottomleft",
                        p2_parent_alignment="bottomleft",

                        background_color=None,

                        children=(
                            widget_lib.TextWidget(
                                name="pinned files",
                                shift=(PADDING, PADDING),
                                font=FONT,
                                text=(
                                )
                            ),
                        )
                    ),
                    widget_lib.DoublePointAlignmentWidget(
                        p1_shift=pygame.Vector2(PINNED_MENU_WIDTH - LINE_WIDTH, PATH_MENU_HEIGHT + 2 * PADDING),
                        p1_alignment="topleft",
                        p1_parent_alignment="topleft",

                        p2_shift=pygame.Vector2(PINNED_MENU_WIDTH, -PADDING),
                        p2_alignment="bottomleft",
                        p2_parent_alignment="bottomleft",

                        background_color=(100, 100, 100)
                    ),
                    widget_lib.DoublePointAlignmentParentWidget(
                        name="folder menu",

                        p1_shift=pygame.Vector2(PINNED_MENU_WIDTH + LINE_WIDTH + PADDING,
                                                PATH_MENU_HEIGHT + 2 * PADDING),
                        p1_alignment="topleft",
                        p1_parent_alignment="topleft",

                        p2_shift=pygame.Vector2(-PADDING, -PADDING),
                        p2_alignment="bottomright",
                        p2_parent_alignment="bottomright",

                        background_color=None,
                    )
                ),
            )
        )

        self.window.set_size(pygame.Vector2(720, 480))

        self.handler = self

        os.chdir("C:/")

        self.refresh_path()
        self.refresh_folder_menu()

        self.selected_paths = []

    def handle_event(self, event) -> None:
        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == pygame.WINDOWRESIZED:
            self.window.set_size(pygame.Vector2(event.x, event.y))

        elif event.type == pygame.MOUSEMOTION:
            new_button = self.get_button_under_mouse()

            if self.old_button is not new_button:
                if self.old_button is not None:
                    self.old_button.set_background_color(DESELECTED_COLOR)

                self.old_button = new_button

                if self.old_button is not None:
                    self.old_button.set_background_color(SELECTED_COLOR)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                path = self.get_button_under_mouse()

                if path is None:
                    return

                path = path.items[0][0]

                if os.path.isdir(path):
                    try:
                        os.chdir(path)

                    except PermissionError:
                        pass

                    self.refresh_path()
                    self.refresh_folder_menu()

        elif event.type == pygame.MOUSEWHEEL:
            folder = self.window.find_name("folder menu")

            folder.primer_rect.topleft += pygame.Vector2(-event.x, event.y) * 30

            folder.primer_rect.top = min(folder.primer_rect.top, 0)
            folder.primer_rect.left = min(folder.primer_rect.left, 0)

            folder.expect_update_seconder_rect()

    def get_button_under_mouse(self):
        for button in self.window.find_tag("folder"):
            if button.is_position_on(self.mouse_position):
                return button

    def get_buttons_under_mouse(self):
        for button in self.window.find_tag("button"):
            if button.is_position_on(self.mouse_position):
                yield button

    def refresh_path(self):
        self.window.find_name("path text").set_text((os.getcwd(),))

    def refresh_folder_menu(self):
        folder = self.window.find_name("folder menu")

        new_children = [
            widget_lib.TextWidget(
                tags=("folder", "button"),
                text=("..",),
                font=FONT,
                shift=(0, 0),
                separation=pygame.Vector2(300, 0),
                min_size=pygame.Vector2()
            )
        ]

        try:
            paths = os.listdir()

        except PermissionError:
            pass

        else:
            for no, path in enumerate(paths, start=1):
                if os.path.isfile(path):
                    text = (path, get_bytes(os.path.getsize(path)))

                else:
                    text = (path,)

                new_children.append(
                    widget_lib.TextWidget(
                        tags=("folder", "button"),
                        text=text,
                        font=FONT,
                        shift=(0, no * FOLDER_SEPARATION),
                        separation=pygame.Vector2(300, 0),
                        min_size=pygame.Vector2()
                    )
                )

        folder.set_children(new_children)


def get_bytes(x):
    i = (len(str(x)) - 1) // 3
    x = (x * 10) // 10 ** (3 * i) / 10

    mod = MODIFIERS[i]

    return f"{x} {mod}"


def main():
    explorer = FileExplorer()

    explorer.handler.run()


MODIFIERS = "B", "kB", "MB", "GB", "TB", "PB"

LINE_WIDTH = 2
PADDING = 5
PATH_MENU_HEIGHT = 20
PINNED_MENU_WIDTH = 200

FOLDER_SEPARATION = 18

ROUNDED_DECORATOR = (decorator_lib.RoundedSurface({
    "topleft": 7,
    "topright": 7,
    "bottomleft": 7,
    "bottomright": 7,
}),
)

FONT = widget_lib.FontStyling(color=(255, 255, 255), background_color=None)

SELECTED_COLOR = 120, 120, 120
DESELECTED_COLOR = None

widget_lib.init()

if __name__ == '__main__':
    main()
