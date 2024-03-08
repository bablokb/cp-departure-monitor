# ----------------------------------------------------------------------------
# adafruit_magtag_2_9_grayscale.py: board-specific setup for Magtag
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# ----------------------------------------------------------------------------

import board
from analogio import AnalogIn

from hal.hal_base import HalBase

class HalMagtag(HalBase):
  """ Magtag specific HAL-class """
  
  def __init__(self):
    """ constructor """
    self._bat_mon = AnalogIn(board.BATTERY)

  def bat_level(self):
    """ return battery level """
    return (self._bat_mon.value / 65535.0) * 3.3 * 2

impl = HalMagtag()
