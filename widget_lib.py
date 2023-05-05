import pygame
import typing

DEBUG_SURFACE_UPDATES = 2 ** 0
DEBUG_POSITION_UPDATES = 2 ** 1
DEBUG_SIZE_UPDATES = 2 ** 2
DEBUG_SHOW_RECTS = 2 ** 3
DEBUG_SHOW_TEXT_BOX = 2 ** 4

debug_flags = 0


def init(flags=0):
    global debug_flags

    pygame.init()
    debug_flags = flags


def debug_log(message):
    print(f"[DEBUG] {message}")


class Widget:
    visible = True

    surface: pygame.Surface = None
    is_expect_update_surface: bool = True

    size: pygame.Vector2 = pygame.Vector2()
    is_expect_update_size: bool = True

    primer_rect: pygame.Rect = None
    is_expect_update_primer_rect: bool = True

    seconder_rect: pygame.Rect = None
    is_expect_update_seconder_rect: bool = True

    full_rect: pygame.Rect = None
    is_expect_update_full_rect: bool = True

    name: str = "unnamed"
    tags: typing.Iterable[str] = ()

    background_color: typing.Iterable[int] = (200, 200, 200, 200)

    def __init__(
            self,
            decorators=(),
            **kwargs
    ):
        self.parent: SinglePointAlignmentParentWidget | None = None

        for decorator in decorators:
            decorator.overwrite(self)

        self.start(**kwargs)

    def start(self, **kwargs):
        self.update_attributes(attribute_names=(
            "name", "tags", "background_color"
        ), **kwargs)

        if "size" in kwargs:
            self.set_size(kwargs["size"])

    def set_background_color(self, new: typing.Iterable[int] | None):
        if new == self.background_color:
            return

        self.background_color = new

        self.expect_update_surface()

    def update_attributes(self, attribute_names, **kwargs):
        for key in attribute_names:
            if key not in kwargs:
                continue

            self.__setattr__(key, kwargs[key])

    def set_visible(self, visible):
        self.visible = visible

        self.parent_expect_update_surface()

    def show(self):
        self.set_visible(True)

    def hide(self):
        self.set_visible(False)

    def get_local_position(self, full_position):
        raise ValueError("Should not be called without overwrite")

    def get_info(self):
        return f"{self.__class__.__name__} '{self.name}'"

    def __repr__(self):
        return f"<{self.get_info()}>"

    def get_tree(self, last=True, indent=0):
        return indent * " │ " + f" {'└' if last else '├'}─ <{self.__class__.__name__} {self.name}>"

    @property
    def is_root(self):
        return self.parent is None

    def reset_surface(self):
        self.update_size()
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)

        if self.background_color is not None:
            self.surface.fill(self.background_color)

        if debug_flags & DEBUG_SHOW_RECTS:
            pygame.draw.rect(self.surface, (0, 0, 0), ((0, 0), self.surface.get_size()), width=1)

    def update_size(self):
        if not self.is_expect_update_size:
            return

        self.updated_size()

    def update_surface(self):
        if not self.is_expect_update_surface:
            return

        self.reset_surface()

        self.updated_surface()

    def get_primer_position(self, alignment: str):
        self.update_primer_rect()
        return pygame.Vector2(getattr(self.primer_rect, alignment))

    def get_seconder_position(self, alignment: str):
        self.update_seconder_rect()
        return pygame.Vector2(getattr(self.seconder_rect, alignment))

    def get_full_position(self, alignment: str):
        self.update_full_rect()
        return pygame.Vector2(getattr(self.full_rect, alignment))

    def find_name(self, name):
        return self if self.name == name else None

    def contains_tag(self, tag):
        return tag in self.tags

    def find_tag(self, tag):
        if self.contains_tag(tag):
            yield self

    def blit(self, surface: pygame.Surface, rect: pygame.Rect):
        self.surface.blit(surface, rect)

    def ask_for_draw(self):
        if not self.visible:
            return

        self.update_surface()
        self.update_seconder_rect()

        self.parent.blit(self.surface, self.seconder_rect)

    def update_primer_rect(self):
        if not self.is_expect_update_primer_rect:
            return

    def update_seconder_rect(self):
        if not self.is_expect_update_seconder_rect:
            return

    def update_full_rect(self):
        if not self.is_expect_update_full_rect:
            return

    def fill_surface(self, color: typing.Iterable[int]):
        self.surface.fill(color)

    def set_parent(self, parent):
        if self.parent is not None:
            raise ValueError(f"Tried to bind {self} to {parent}, but it was already bound to {self.parent}.")

        if not ParentWidget.__instancecheck__(parent):
            raise ValueError(f"Tried to bind {self} to {parent}, but it was not a ParentWidget.")

        self.parent = parent

    def reset_parent(self):
        if self.parent is None:
            raise ValueError(f"Tried to unbind {self} from its parent, but it does not have one.")

        self.parent = None

    @property
    def delta(self):
        return pygame.Vector2(self.full_rect.topleft) - pygame.Vector2(self.primer_rect.topleft)

    def is_position_on(self, position: pygame.Vector2):
        self.update_full_rect()

        return self.full_rect.collidepoint(tuple(position))

    @property
    def full_visible(self):
        return self.visible and self.parent.full_visible

    @property
    def root_widget(self):
        return self if self.is_root else self.parent.root_widget

    def get(self, key):
        """
        % finds the child
        $ finds the attribute
        """
        first, other = key.split(".", 1)

        start = first[0]
        name = first[1:]

        match start:
            case "%":
                return self.find_name(name).get(other)

            case "$":
                return getattr(self, name)

            case _:
                return None

    def set(self, key, value):
        """
        % finds the child
        $ finds the attribute
        """
        first, other = key.split(".", 1)

        start = first[0]
        name = first[1:]

        match start:
            case "%":
                self.find_name(name).set(other, value)

            case "$":
                setattr(self, start, value)

            case _:
                return None

    def expect_update_size(self):
        self.is_expect_update_size = True
        self.expect_update_primer_rect()
        self.expect_update_surface()

    def expect_update_surface(self):
        self.is_expect_update_surface = True
        self.parent_expect_update_surface()

    def expect_update_primer_rect(self):
        self.is_expect_update_primer_rect = True
        self.expect_update_seconder_rect()

    def expect_update_seconder_rect(self):
        self.is_expect_update_seconder_rect = True
        self.expect_update_full_rect()

    def expect_update_full_rect(self):
        self.is_expect_update_full_rect = True
        self.parent_expect_update_surface()

    def parent_expect_update_surface(self):
        if not self.is_root:
            self.parent.expect_update_surface()

    def updated_size(self):
        self.is_expect_update_size = False
        self.expect_update_surface()
        self.expect_update_primer_rect()

        if debug_flags & DEBUG_SIZE_UPDATES:
            debug_log(f"size update: {self}")

    def updated_surface(self):
        self.is_expect_update_surface = False
        self.parent_expect_update_surface()

        if debug_flags & DEBUG_SURFACE_UPDATES:
            debug_log(f"surface update: {self}")

    def set_size(self, size):
        self.size = pygame.Vector2(size)

        self.updated_size()


class ParentWidget(Widget):
    children: list[Widget]

    def start(self, **kwargs):
        self.children = []

        self.set_children(kwargs.get("children", ()))

    def find_name(self, name):
        if self.name == name:
            return self

        for child in self.children:
            found = child.find_name(name)

            if found is not None:
                return found

    def find_tag(self, tag):
        if self.contains_tag(tag):
            yield self

        for child in self.children:
            yield from child.find_tag(tag)

    def get_info(self):
        match self.children:
            case []:
                return Widget.get_info(self)

            case [child]:
                return f"{Widget.get_info(self)} ({child})"

            case _:
                return f"{Widget.get_info(self)} ({len(self.children)} children)"

    def get_tree(self, last=True, indent=0):
        text = Widget.get_tree(self, last, indent)

        for child in self.children[:-1]:
            text += "\n" + child.get_tree(False, indent + 1)

        text += "\n" + self.children[-1].get_tree(True, indent + 1)

        return text

    def set_children(self, children: typing.Iterable[Widget]):
        self.kill_children()
        self.add_children(children)

    def add_children(self, children):
        for child in children:
            child.set_parent(self)

            self.children.append(child)

        self.expect_update_surface()

    def kill_children(self, children: list = None):
        if children is None:
            for child in self.children:
                child.reset_parent()

            self.children.clear()

        else:
            for child in children:
                child.reset_parent()

                self.children.remove(child)

        self.expect_update_surface()

    def expect_update_seconder_rect(self):
        Widget.expect_update_seconder_rect(self)

        self.children_expect_update_seconder_rect()

    def expect_update_full_rect(self):
        Widget.expect_update_full_rect(self)

        self.children_expect_update_full_rect()

    def expect_update_size(self):
        Widget.expect_update_size(self)

        self.children_expect_update_size()

    def children_expect_update_size(self):
        for child in self.children:
            child.expect_update_size()

    def children_expect_update_seconder_rect(self):
        for child in self.children:
            child.expect_update_seconder_rect()

    def children_expect_update_full_rect(self):
        for child in self.children:
            child.expect_update_full_rect()

    def updated_size(self):
        Widget.updated_size(self)
        self.children_expect_update_size()

    def update_surface(self):
        if not self.is_expect_update_surface:
            return

        self.reset_surface()

        self.update_primer_rect()

        for child in self.children:
            child.ask_for_draw()

        self.updated_surface()


class SinglePointAlignmentWidget(Widget):
    shift: pygame.Vector2 = pygame.Vector2()
    alignment: str = "topleft"
    parent_alignment: str = "topleft"

    def start(self, **kwargs):
        Widget.start(self, **kwargs)

        self.update_attributes(attribute_names=(
            "shift", "alignment", "parent_alignment"
        ), **kwargs)

    def get_local_position(self, position: pygame.Vector2, alignment: str = None):
        if alignment is None:
            alignment = self.alignment

        return position - self.get_full_position(alignment)

    def update_primer_rect(self):
        if not self.is_expect_update_primer_rect:
            return

        self.update_size()

        self.primer_rect = pygame.Rect((0, 0), self.size)

        self.is_expect_update_primer_rect = False

    def update_seconder_rect(self):
        if not self.is_expect_update_seconder_rect:
            return

        self.update_primer_rect()

        self.seconder_rect = self.primer_rect.copy()

        position = self.parent.get_primer_position(self.parent_alignment) + self.shift
        setattr(self.seconder_rect, self.alignment, position)

        self.is_expect_update_seconder_rect = False

    def update_full_rect(self):
        if not self.is_expect_update_full_rect:
            return

        self.update_seconder_rect()
        self.parent.update_full_rect()

        self.full_rect = self.primer_rect.copy()

        position = self.parent.get_full_position(self.parent_alignment) + \
            self.parent.get_primer_position(self.parent_alignment) + \
            self.shift
        setattr(self.full_rect, self.alignment, position)

        self.is_expect_update_full_rect = False

    def set_shift(self, new: pygame.Vector2 | typing.Iterable[int]):
        self.shift = pygame.Vector2(new)

        self.expect_update_seconder_rect()

    def add_shift(self, add: pygame.Vector2):
        self.set_shift(self.shift + add)

    def set_full_position(self, full_position: pygame.Vector2, local_position: pygame.Vector2):
        old_position = self.get_local_position(full_position)
        self.add_shift(old_position - local_position)


class DoublePointAlignmentWidget(Widget):
    p1_shift: pygame.Vector2 = pygame.Vector2()
    p1_alignment: str = "topleft"
    p1_parent_alignment: str = "topleft"

    p2_shift: pygame.Vector2 = pygame.Vector2()
    p2_alignment: str = "topleft"
    p2_parent_alignment: str = "topleft"

    def start(self, **kwargs):
        Widget.start(self, **kwargs)

        self.update_attributes(attribute_names=(
            "p1_shift",
            "p1_alignment",
            "p1_parent_alignment",

            "p2_shift",
            "p2_alignment",
            "p2_parent_alignment",
        ), **kwargs)

    def get_local_position(self, position: pygame.Vector2, alignment: str = None):
        if alignment is None:
            alignment = self.p1_alignment

        return position - self.get_full_position(alignment)

    def update_primer_rect(self):
        if not self.is_expect_update_primer_rect:
            return

        self.primer_rect = pygame.Rect((0, 0), self.size)

        self.is_expect_update_primer_rect = False

    def update_seconder_rect(self):
        if not self.is_expect_update_seconder_rect:
            return

        self.update_primer_rect()

        self.seconder_rect = self.primer_rect.copy()

        # Could also use p2, but nothing will change

        position = self.parent.get_primer_position(self.p1_parent_alignment) + self.p1_shift
        setattr(self.seconder_rect, self.p1_alignment, position)

        self.is_expect_update_seconder_rect = False

    def update_full_rect(self):
        if not self.is_expect_update_full_rect:
            return

        self.update_seconder_rect()
        self.parent.update_full_rect()

        self.full_rect = self.primer_rect.copy()

        position = self.parent.get_full_position(self.p1_parent_alignment) + self.p1_shift
        setattr(self.full_rect, self.p1_alignment, position)

        self.is_expect_update_full_rect = False

    def add_shift(self, add: pygame.Vector2):
        self.p1_shift += add
        self.p2_shift += add

    def update_size(self):
        if not self.is_expect_update_size:
            return

        p1 = getattr(self.parent.primer_rect, self.p1_parent_alignment) + self.p1_shift
        p2 = getattr(self.parent.primer_rect, self.p2_parent_alignment) + self.p2_shift

        self.size = p2 - p1

        self.updated_size()

    def set_full_position(self, full_position: pygame.Vector2, local_position: pygame.Vector2):
        old_position = self.get_local_position(full_position)
        self.add_shift(old_position - local_position)


class SinglePointAlignmentParentWidget(ParentWidget, SinglePointAlignmentWidget):
    def start(self, **kwargs):
        ParentWidget.start(self, **kwargs)
        SinglePointAlignmentWidget.start(self, **kwargs)


class DoublePointAlignmentParentWidget(ParentWidget, DoublePointAlignmentWidget):
    def start(self, **kwargs):
        ParentWidget.start(self, **kwargs)
        DoublePointAlignmentWidget.start(self, **kwargs)


class Window(SinglePointAlignmentParentWidget):
    window: pygame.Surface = None

    flags: int = 0

    def start(self, **kwargs):
        SinglePointAlignmentParentWidget.start(self, **kwargs)

        self.update_attributes(attribute_names=(
            "flags",
            "event_handler"
        ), **kwargs)

    def updated_size(self):
        SinglePointAlignmentParentWidget.updated_size(self)
        self.window = pygame.display.set_mode(self.size, self.flags)

    def render(self):
        self.update_surface()
        self.window.blit(self.surface, (0, 0))

        pygame.display.update()

    def update_seconder_rect(self):
        if not self.is_expect_update_seconder_rect:
            return

        self.is_expect_update_seconder_rect = False

    def update_full_rect(self):
        if not self.is_expect_update_full_rect:
            return

        self.update_primer_rect()

        self.full_rect = self.primer_rect.copy()

        self.is_expect_update_full_rect = False

    @property
    def full_visible(self):
        return self.visible


class FontStyling:
    font: pygame.font.Font = None
    expect_update_font: bool = True

    name: str
    size: int

    bold: bool
    italic: bool

    def __init__(
            self,
            name: str | bytes = "Consolas",
            size: int = 16,
            bold: bool = False,
            italic: bool = False,
            color: typing.Iterable[int] = (0, 0, 0),
            background_color: typing.Iterable[int] = None
    ):
        self.set_properties(name, size, bold, italic)

        self.color = color
        self.background_color = background_color

    def set_properties(self, name=None, size=None, bold=None, italic=None):
        if name is not None:
            self.name = name

        if size is not None:
            self.size = size

        if bold is not None:
            self.bold = bold

        if italic is not None:
            self.italic = italic

        self.expect_update_font = True

    def update_font(self):
        if not self.expect_update_font:
            return

        self.font = pygame.font.SysFont(self.name, self.size, self.bold, self.italic)

    def render(self, text):
        self.update_font()

        return self.font.render(text, True, self.color, self.background_color)

    @property
    def height(self):
        self.update_font()

        return self.font.get_height()


class TextWidget(SinglePointAlignmentWidget):
    items: list[tuple[str, pygame.Surface, pygame.Rect]]
    font: FontStyling = FontStyling()
    text_alignment: str = "topleft"

    separation: pygame.Vector2 = None
    padding: pygame.Vector2 = pygame.Vector2()
    min_size: pygame.Vector2 = pygame.Vector2()

    background_color = None

    def start(self, **kwargs):
        SinglePointAlignmentWidget.start(self, **kwargs)

        self.update_attributes(attribute_names=(
            "font", "separation", "text_alignment", "padding", "min_size"
        ), **kwargs)

        self.items = []

        self.font = kwargs.get("font", FontStyling())

        if self.separation is None:
            self.separation = pygame.Vector2(0, self.font.height)

        self.set_text(kwargs.get("text", ()))

    def __getitem__(self, item):
        return self.items[item]

    def set_text(self, text):
        self.items.clear()

        if type(text) is str:
            text = text.split("\n")

        for line_no, line in enumerate(text):
            self.items.append(self.create_item(line_no, line))

        self.expect_update_size()

    def set_at(self, line_no, text):
        self.items[line_no] = self.create_item(line_no, text)

    def get_table(self):
        result = ""

        for text, _, _ in self.items:
            result += text + "\n"

        return result

    def create_item(self, index: int, text: str | bytes):
        surface = self.font.render(text)
        rect = surface.get_rect()
        setattr(rect, self.text_alignment, self.separation * index)

        return text, surface, rect

    def update_size(self):
        if not self.is_expect_update_size:
            return

        lt = 0
        r = 0
        t = 0
        b = 0

        for _, _, rect in self.items:
            lt = min(lt, rect.left)
            r = max(r, rect.right)
            t = min(t, rect.top)
            b = max(b, rect.bottom)

        self.set_size(2 * self.padding + pygame.Vector2(max(r - lt, self.min_size.x), max(b - t, self.min_size.y)))

    def update_surface(self):
        if not self.is_expect_update_surface:
            return

        self.update_primer_rect()
        self.reset_surface()

        for _, surface, rect in self.items:
            self.surface.blit(surface, rect)

        self.updated_surface()

    def render_items(self):
        for line_no, (text, _, _) in enumerate(self.items):
            self.items[line_no] = self.create_item(line_no, text)

    def set_font(self, new_font):
        if self.font == new_font:
            return

        self.font = new_font
        self.render_items()

        self.expect_update_size()
        self.expect_update_surface()
