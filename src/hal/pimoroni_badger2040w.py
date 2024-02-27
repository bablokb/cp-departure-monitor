# ----------------------------------------------------------------------------
# pimoroni_badger2040w.py: HAL for Pimoroni Badger2040W
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
# ----------------------------------------------------------------------------

import board

from digitalio import DigitalInOut, Direction

from hal.hal_base import HalBase

class HalBadger2040W(HalBase):
  """ Badger2040W specific HAL-class """

  def status_led(self,value):
    """ set status LED """
    if not hasattr(self,"_led"):
      self._led = DigitalInOut(board.USER_LED)
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

impl = HalBadger2040W()
