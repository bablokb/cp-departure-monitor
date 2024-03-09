# ----------------------------------------------------------------------------
# GENERIC_LINUX_PC.py: HAL for simulation with PygameDisplay
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
# ----------------------------------------------------------------------------

# display-sizes
#   - Inky wHat:            400x300
#   - Inky-Impression 4":   640x400
#   - Inky-Impression 5.7": 600x448
#   - Inky-Frame 5.7":      600x448
#   - Badger2040W:          296x128

import sys
import time
import board
from blinka_displayio_pygamedisplay import PyGameDisplay
from hal.hal_base import HalBase

class HalPygame(HalBase):
  """ GENERIC_LINUX_PC specific HAL-class """

  def get_display(self):
    """ return display """
    if self._display:
      return self._display

    self._display = PyGameDisplay(width=296,height=128,
                                  native_frames_per_second=1)
    return self._display

  def show(self,content):
    """ show and refresh the display """
    self._display.show(content)
    self._display.refresh()

  def bat_level(self):
    """ return battery level """
    return 3.6

  def status_led(self,value):
    """ set status LED """
    pass

  def wifi(self):
    """ return wifi-interface """
    from wifi_helper_generic import WifiHelper
    return WifiHelper(debug=True)

  def shutdown(self):
    """ leave program (here: wait for quit)"""
    while True:
      if self._display.check_quit():
        sys.exit(0)
      time.sleep(0.1)

  def sleep(self,duration):
    if not self._display:
      super.sleep(duration)
      return

    start = time.monotonic()
    while time.monotonic()-start < duration:
      if self._display.check_quit():
        sys.exit(0)
      time.sleep(0.1)

impl = HalPygame()
