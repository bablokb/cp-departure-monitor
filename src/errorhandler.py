# -------------------------------------------------------------------------
# This class implements a simple error handler
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# -------------------------------------------------------------------------

import time
import traceback
import displayio
from vectorio import Rectangle

from ui_settings import UI_SETTINGS, UI_PALETTE, COLORS

class ErrorHandler:

  # --- constructor   ------------------------------------------------------

  def __init__(self):
    """ constructor: create ressources """

  # --- set display   --------------------------------------------------------

  def set_display(self,display):
    """ set display """
    self._display = display

  # --- exception-handler   ------------------------------------------------

  def on_exception(self,ex):
    """ save exception for later processing """
    self._ex = ex
    traceback.print_exc()

  # --- provide content   --------------------------------------------------

  def get_content(self):
    """ provide content in relation to exeception """

    # TODO: implement...

    g = displayio.Group()
    background = Rectangle(pixel_shader=UI_PALETTE,x=0,y=0,
                           width=self._display.width,
                           height=self._display.height,
                           color_index=COLORS.WHITE)
    g.append(background)

    f = open(UI_SETTINGS.NO_NETWORK, "rb")
    pic = displayio.OnDiskBitmap(f)
    x = int((self._display.width-pic.width)/2)
    y = int((self._display.height-pic.height)/2)
    t = displayio.TileGrid(pic, x=x,y=y, pixel_shader=UI_PALETTE)
    g.append(t)
    return g
