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
import re
import gc

import displayio

from settings import app_config
from ui_settings import UI_SETTINGS

# --- Depmon Class for layout   -------------------------------------------

class DepmonUIProvider:

  # --- constructor   --------------------------------------------------------

  def __init__(self,debug=False):
    """ constructor: create ressources """

    self._debug  = debug
    self._view   = None
    self._info   = None
    self._name   = None
    self._update = None

  # --- print debug-message   ------------------------------------------------

  def msg(self,text):
    """ print (debug) message """
    if self._debug:
      print(text)

  # --- update data   --------------------------------------------------------

  def update_ui(self,new_data):
    """ update data: callback for Application """

    # update model
    self._bat_level = new_data["bat_level"]
    c_index = new_data["station_index"]
    self._rindex = new_data["row"]
    self._info   = new_data["departures"][c_index].info
    self._name   = new_data["departures"][c_index].name
    self._update = new_data["departures"][c_index].update

    # update UI
    self._header.text  = self._replace(self._name)
    self._footerL.text = self._get_footerL_text()
    self._footerR.text = f"{self._bat_level:0.1f}V"
    self._dep.text     = self._replace(self._get_departure_text())

  # --- replace pre-defined strings   ----------------------------------------

  def _replace(self,text):
    """ replace predefined strings """

    patterns = getattr(app_config,'replace',[])
    result = text
    for src,dest in patterns:
      result = re.sub(src,dest,result)
    return result

  # --- query footer text   --------------------------------------------------

  def _get_footerL_text(self):
    """ pretty print update time """

    ltime = getattr(time,'gmtime',time.localtime) # use time.gmtime with CPython
    ts = ltime(self._update)
    return f"{UI_SETTINGS.FOOTER}: {ts.tm_hour:02}:{ts.tm_min:02}:{ts.tm_sec:02}"

  # --- query departure-text   -----------------------------------------------

  def _get_departure_text(self):
    """ get departure text """

    # get column-width for delay and line-name
    wmax_delay = 1
    wmax_line  = 0
    for index,d in enumerate(self._info):
      if index < self._rindex:
        continue
      elif index == self._rindex + UI_SETTINGS.ROWS:
        break
      wmax_delay = max(wmax_delay,len(str(d.delay)))
      wmax_line  = max(wmax_line,len(d.line))

    # create template
    template  = f"{{t}}{{s}}{{d:>{wmax_delay}.{wmax_delay}}}"
    template += f" {{n:<{wmax_line}.{wmax_line}}} {{dir}}"

    # create text
    txt_lines = []
    for index,d in enumerate(self._info):
      if index < self._rindex:
        continue
      elif index == self._rindex + UI_SETTINGS.ROWS:
        break
      if d.cancelled:
        sign = ' '
        delay = 'X'*wmax_delay
      elif d.delay > 0:
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

  # --- create complete UI   -------------------------------------------------

  def create_ui(self,display):
    """ create ui """

    from adafruit_bitmap_font import bitmap_font
    from adafruit_display_text import label as label
    from adafruit_display_shapes.line import Line
    from vectorio import Rectangle

    self._view = displayio.Group()
    font = bitmap_font.load_font(UI_SETTINGS.FONT)

    self._view.append(Rectangle(pixel_shader=UI_SETTINGS.PALETTE,x=0,y=0,
                       width=display.width,
                       height=display.height,
                       color_index=UI_SETTINGS.BG_INDEX))

    # create title-label (top-center)
    self._header = label.Label(font=font,color=UI_SETTINGS.FG_COLOR,
                          text="PLACEHOLDER",
                          anchor_point=(0.5,0))
    self._header.anchored_position = (display.width/2,UI_SETTINGS.MARGIN)
    self._view.append(self._header)

    h = self._header.height + 2
    sep = Line(0,h,display.width,h,color=UI_SETTINGS.FG_COLOR)
    self._view.append(sep)

    # create departure label (left-middle)
    self._dep = label.Label(font=font,color=UI_SETTINGS.FG_COLOR,
                            tab_replacement=(2," "),
                            line_spacing=1,
                            text="\n".join(
                              ["PLACEHOLDER" for _ in range(UI_SETTINGS.ROWS)]),
                            anchor_point=(0,0.5))
    self._dep.anchored_position = (UI_SETTINGS.MARGIN,display.height/2)
    self._view.append(self._dep)

    # create footer-label (update-time, left-bottom)
    self._footerL = label.Label(font=font,color=UI_SETTINGS.FG_COLOR,
                          text="PLACEHOLDER",
                          anchor_point=(0,1))
    self._footerL.anchored_position = (UI_SETTINGS.MARGIN,
                                 display.height-UI_SETTINGS.MARGIN)
    self._view.append(self._footerL)

    # create footer-label (voltage, right-bottom)
    self._footerR = label.Label(font=font,color=UI_SETTINGS.FG_COLOR,
                          text="0.0V",
                          anchor_point=(1,1))
    self._footerR.anchored_position = (display.width-UI_SETTINGS.MARGIN,
                                 display.height-UI_SETTINGS.MARGIN)
    self._view.append(self._footerR)

    h = display.height - max(self._footerL.height,self._footerR.height) - 2
    sep = Line(0,h,display.width,h,color=UI_SETTINGS.FG_COLOR)
    self._view.append(sep)

    return self._view

  # --- clear UI and free memory   --------------------------------------

  def clear_ui(self):
    """ clear UI """

    if self._view:
      for _ in range(len(self._view)):
        self._view.pop()
    self._view = None
    gc.collect()

  # --- handle exception   ---------------------------------------------------

  def handle_exception(self,ex):
    """ handle exception """

    traceback.print_exception(ex)

    # optional:
    #   - save exception here
    #   - create different content in create_content() if exception occured
