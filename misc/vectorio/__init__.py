# ----------------------------------------------------------------------------
# This implementation emulates vectorio.Rectangle using the code from
# adafruit_display_shapes.rect.
#
# This is a workaround needed until Blinka-Displayio-PygameDisplay
# supports the current version of Blinka-Displayio, which already has
# a vectorio implementation.
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# ----------------------------------------------------------------------------

# SPDX-FileCopyrightText: 2019 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import displayio

try:
    from typing import Optional
except ImportError:
    pass


class Rectangle(displayio.TileGrid):
    def __init__(
        self,
        pixel_shader: displayio.Palette,
        x: int,
        y: int,
        width: int,
        height: int,
        *,
        color_index: int,
        outline: Optional[int] = None,
        stroke: int = 1,
    ) -> None:
        fill = pixel_shader[color_index]
        self._bitmap = displayio.Bitmap(width, height, 2)
        self._palette = displayio.Palette(2)

        if outline is not None:
            self._palette[1] = outline
            for w in range(width):
                for line in range(stroke):
                    self._bitmap[w, line] = 1
                    self._bitmap[w, height - 1 - line] = 1
            for _h in range(height):
                for line in range(stroke):
                    self._bitmap[line, _h] = 1
                    self._bitmap[width - 1 - line, _h] = 1

        if fill is not None:
            self._palette[0] = fill
            self._palette.make_opaque(0)
        else:
            self._palette[0] = 0
            self._palette.make_transparent(0)
        super().__init__(self._bitmap, pixel_shader=self._palette, x=x, y=y)

    @property
    def fill(self) -> Optional[int]:
        """The fill of the rectangle. Can be a hex value for a color or ``None`` for
        transparent."""
        return self._palette[0]

    @fill.setter
    def fill(self, color: Optional[int]) -> None:
        if color is None:
            self._palette[0] = 0
            self._palette.make_transparent(0)
        else:
            self._palette[0] = color
            self._palette.make_opaque(0)

    @property
    def outline(self) -> Optional[int]:
        """The outline of the rectangle. Can be a hex value for a color or ``None``
        for no outline."""
        return self._palette[1]

    @outline.setter
    def outline(self, color: Optional[int]) -> None:
        if color is None:
            self._palette[1] = 0
            self._palette.make_transparent(1)
        else:
            self._palette[1] = color
            self._palette.make_opaque(1)

    @property
    def width(self) -> int:
        """
        :return: the width of the rectangle in pixels
        """
        return self._bitmap.width

    @property
    def height(self) -> int:
        """
        :return: the height of the rectangle in pixels
        """
        return self._bitmap.height
