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
from hal.hal_base import HalBase

class HalPygame(HalBase):
  """ GENERIC_LINUX_PC specific HAL-class """

  def show(self,content):
    """ show and refresh the display """
    self._display.show(content)
    self._display.refresh()

  def bat_level(self):
    """ return battery level """
    return 3.6

  def led(self,value,color=None):
    """ set status LED (not-supported)"""
    pass

  def wifi(self,debug=False):
    """ return wifi-interface """
    from wifi_helper_generic import WifiHelper
    return WifiHelper(debug=debug)

  def shutdown(self):
    """ leave program """
    sys.exit(0)

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
