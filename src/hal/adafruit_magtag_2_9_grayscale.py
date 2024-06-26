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
from digitalio import DigitalInOut, Direction

import neopixel

from hal.hal_base import HalBase

class HalMagtag(HalBase):
  """ Magtag specific HAL-class """

  def __init__(self):
    """ constructor """
    super().__init__()

  def bat_level(self):
    """ return battery level """
    from analogio import AnalogIn
    adc = AnalogIn(board.BATTERY)
    level = (adc.value / 65535.0) * 3.3 * 2
    adc.deinit()
    return level

  def get_keys(self):
    """ return list of pin-numbers for up, down, left, right """
    # format is (active-state,[key1,...])
    return (False,[board.D14,board.D12,board.D15,board.D11])

impl = HalMagtag()
