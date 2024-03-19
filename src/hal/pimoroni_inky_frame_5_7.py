# ----------------------------------------------------------------------------
# pimoroni_inky_frame_5_7.py: HAL for Pimoroni InkyFrame 5.7
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
# ----------------------------------------------------------------------------

import board

from digitalio import DigitalInOut, Direction

from hal.hal_base import HalBase

class HalInkyFrame57(HalBase):
  """ InkyFrame 5.7 specific HAL-class """

  def led(self,value,color=None):
    """ set status LED (ignore color)"""
    if not hasattr(self,"_led"):
      self._led = DigitalInOut(board.LED_ACT)
      self._led.direction = Direction.OUTPUT
    self._led.value = value

  def get_rtc_ext(self):
    """ return external rtc, if available """
    from rtc_ext.pcf85063a import ExtPCF85063A
    i2c = board.I2C()
    return ExtPCF85063A(i2c)

  def shutdown(self):
    """ turn off power by pulling enable pin low """
    board.ENABLE_DIO.value = 0

impl = HalInkyFrame57()
