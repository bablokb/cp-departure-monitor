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

  def get_keys(self):
    """ return list of pin-numbers for up, down, left, right """
    # format is (active-state,[key1,...])
    return (False,[board.D14,board.D12,board.D15,board.D11])

impl = HalMagtag()
