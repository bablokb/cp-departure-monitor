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

  def led(self,value,color=None):
    """ set status LED (ignore color)"""
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

  def reset_if_needed(self):
    """ reset device (workaround for MemoryError) """
    import supervisor
    supervisor.reload()

  def get_keys(self):
    """ return list of pin-numbers for up, down, left, right """
    # format is (active-state,[key1,...])
    return (True,[board.SW_UP,board.SW_DOWN,board.SW_A,board.SW_C])

impl = HalBadger2040W()
