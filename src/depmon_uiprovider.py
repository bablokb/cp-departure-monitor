# -------------------------------------------------------------------------
# UI provider for the Departure Monitor.
#
# This class implements the actual layout of all items on the display.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# -------------------------------------------------------------------------

import time
import traceback

from dataviews.Base import Justify
from dataviews.DataView  import DataView
from dataviews.DataPanel import DataPanel, PanelText

from settings import app_config
from ui_settings import UI_SETTINGS

# --- Depmon Class for layout   -------------------------------------------

class DepmonUIProvider:

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor: create ressources """

    # grid: time,delay,line,direction
    self._dim    = (UI_SETTINGS.ROWS,4)
    self._view   = None
    self._panel  = None
    self._model  = None
    self._name   = None
    self._update = None
    
  # --- update data   --------------------------------------------------------

  def update_data(self,new_data):
    """ update data: callback for Application """

    # update model (only first station for now)
    station = app_config.stations[0][0]
    info         = new_data["departures"][station].info
    self._name   = new_data["departures"][station].name
    self._update = new_data["departures"][station].update
    self._model  = []
    for index,record in enumerate(info):
      if index == UI_SETTINGS.ROWS:
        # use at most ROWS records until we support paging
        break
      for i in range(4):
        self._model.append(record[i])
    if len(info) < self._dim[0]:
      for _ in range(4*(self._dim[0]-len(info))):
        self._model.append("")

  # --- pretty print update   ------------------------------------------------

  def _get_upd_time(self):
    """ pretty print update time """

    ts = time.localtime(self._update)
    return f"{ts.tm_hour}:{ts.tm_min}:{ts.tm_sec}"

  # --- create complete content   --------------------------------------------

  def create_content(self,display):
    """ create content """

    if self._panel:
      self._title.text = self._name
      self._footer.text = text=UI_SETTINGS.FOOTER + self._get_upd_time()
      self._view.set_values(self._model)
      return self._panel

    border  = 1
    offset  = 1    # keep away from border-pixels
    divider = 1
    padding = UI_SETTINGS.PADDING
    self._view = DataView(
      dim=self._dim,
      width=display.width-2*(border+padding+offset)-(self._dim[1]-1)*divider,
      height=int(0.6*display.height),
      justify=Justify.LEFT,
      fontname=UI_SETTINGS.FONT,
      border=border,
      divider=divider,
      color=UI_SETTINGS.FOREGROUND,
      bg_color=UI_SETTINGS.BACKGROUND
    )

    # create DataPanel
    self._title = PanelText(text=self._name,
                      fontname=UI_SETTINGS.FONT,
                      justify=Justify.CENTER)

    self._footer = PanelText(text=UI_SETTINGS.FOOTER + self._get_upd_time(),
                             fontname=UI_SETTINGS.FONT,
                             justify=Justify.LEFT)
    self._panel = DataPanel(
      x = offset,
      y = offset,
      width=display.width-2*offset,
      height=display.height-2*offset,
      view=self._view,
      title=self._title,
      footer=self._footer,
      border=border,
      padding=UI_SETTINGS.PADDING,
      justify=Justify.CENTER,
      color=UI_SETTINGS.FOREGROUND,
      bg_color=UI_SETTINGS.BACKGROUND
    )

    self._view.set_values(self._model)
    return self._panel

  # --- handle exception   ---------------------------------------------------

  def handle_exception(self,ex):
    """ handle exception """

    traceback.print_exception(ex)

    # optional:
    #   - save exception here
    #   - create different content in create_content() if exception occured
