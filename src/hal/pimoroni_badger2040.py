# ----------------------------------------------------------------------------
# pimoroni_badger2040.py: HAL for Pimoroni Badger2040
# (using ESP32Cx as wifi co-processor).
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
# ----------------------------------------------------------------------------

import board

from digitalio import DigitalInOut, Direction
from analogio import AnalogIn

from hal.hal_base import HalBase

class HalBadger2040(HalBase):
  """ Badger2040 specific HAL-class """

  def led(self,value,color=None):
    """ set status LED (ignore color)"""
    if not hasattr(self,"_led"):
      self._led = DigitalInOut(board.USER_LED)
      self._led.direction = Direction.OUTPUT
    self._led.value = value

  def bat_level(self):
    """ return battery level """
    bat_mon = AnalogIn(board.VBAT_SENSE)
    ref_1V2 = AnalogIn(board.REF_1V2)
    ref_pow = DigitalInOut(board.VREF_POWER)
    ref_pow.direction = Direction.OUTPUT

    ref_pow.value = 1
    vdd   = 1.24*65535/ref_1V2.value
    level = bat_mon.value/65535*vdd*3
    ref_pow.value = 0

    ref_pow.deinit()
    ref_1V2.deinit()
    bat_mon.deinit()
    return level

  def wifi(self,debug=False):
    """ return wifi-interface """
    import busio
    import wifi
    uart = busio.UART(board.TX, board.RX, baudrate=115200,
                      receiver_buffer_size=2048)
    wifi.init(uart=uart)
    wifi.radio.tx_power = 15
    return super().wifi(debug)

  def get_rtc_ext(self):
    """ return external rtc, if available """
    None

  def shutdown(self):
    """ turn off power by pulling enable pin low """
    board.ENABLE_DIO.value = 0

  def get_keys(self):
    """ return list of pin-numbers for up, down, left, right """
    # format is (active-state,[key1,...])
    return (True,[board.SW_UP,board.SW_DOWN,board.SW_A,board.SW_C])

impl = HalBadger2040()
