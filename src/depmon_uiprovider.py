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

import displayio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label as label
from vectorio import Rectangle

from settings import app_config
from ui_settings import UI_SETTINGS

# --- Depmon Class for layout   -------------------------------------------

class DepmonUIProvider:

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor: create ressources """

    # grid: time,delay,line,direction
    self._info   = None
    self._name   = None
    self._update = None
    
  # --- update data   --------------------------------------------------------

  def update_data(self,new_data):
    """ update data: callback for Application """

    # update model (only first station for now)
    station = app_config.stations[0][0]
    self._info   = new_data["departures"][station].info
    self._name   = new_data["departures"][station].name
    self._update = new_data["departures"][station].update

  # --- query footer text   --------------------------------------------------

  def _get_footer_text(self):
    """ pretty print update time """

    ts = time.localtime(self._update)
    return f"{UI_SETTINGS.FOOTER}: {ts.tm_hour:02}:{ts.tm_min:02}:{ts.tm_sec:02}"

  # --- query departure-text   -----------------------------------------------

  def _get_departure_text(self):
    """ get departure text """

    # get column-width for delay and line-name
    wmax_delay = 0
    wmax_line  = 0
    for index,d in enumerate(self._info):
      if index == UI_SETTINGS.ROWS:
        break
      wmax_delay = max(wmax_delay,len(str(d.delay)))
      wmax_line  = max(wmax_line,len(d.line))

    # create template
    template  = f"{{t}}{{s}}{{d:>{wmax_delay}.{wmax_delay}}}"
    template += f" {{n:<{wmax_line}.{wmax_line}}} {{dir}}"

    # create text
    txt_lines = []
    for index,d in enumerate(self._info):
      if index == UI_SETTINGS.ROWS:
        break
      if d.delay > 0:
        sign = '+'
        delay = str(d.delay)
      elif d.delay < 0:
        sign = '-'
        delay = str(-d.delay)
      else:
        sign = ' '
        delay = ' '
      txt_lines.append(template.format(t=d.plan,s=sign,
                                       d=delay,n=d.line,dir=d.dir))
    return "\n".join(txt_lines)

  # --- create complete content   --------------------------------------------

  def create_content(self,display):
    """ create content """

    g = displayio.Group()
    font = bitmap_font.load_font(UI_SETTINGS.FONT)

    g.append(Rectangle(pixel_shader=UI_SETTINGS.PALETTE,x=0,y=0,
                       width=display.width,
                       height=display.height,
                       color_index=UI_SETTINGS.BG_COLOR))

    # create title-label (top-center)
    t_label = label.Label(font=font,color=UI_SETTINGS.FG_PALETTE,
                          text=self._name,
                          anchor_point=(0.5,0))
    t_label.anchored_position = (display.width/2,UI_SETTINGS.MARGIN)
    g.append(t_label)

    # create departure label (left-middle)
    d_label = label.Label(font=font,color=UI_SETTINGS.FG_PALETTE,
                          tab_replacement=(2," "),
                          line_spacing=1,
                          text=self._get_departure_text(),
                          anchor_point=(0,0.5))
    d_label.anchored_position = (UI_SETTINGS.MARGIN,display.height/2)
    g.append(d_label)

    # create footer-label (left-bottom)
    f_label = label.Label(font=font,color=UI_SETTINGS.FG_PALETTE,
                          text=self._get_footer_text(),
                          anchor_point=(0,1))
    f_label.anchored_position = (UI_SETTINGS.MARGIN,
                                 display.height-UI_SETTINGS.MARGIN)
    g.append(f_label)
    return g

  # --- handle exception   ---------------------------------------------------

  def handle_exception(self,ex):
    """ handle exception """

    traceback.print_exception(ex)

    # optional:
    #   - save exception here
    #   - create different content in create_content() if exception occured
