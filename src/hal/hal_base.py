# ----------------------------------------------------------------------------
# HalBase: Hardware-Abstraction-Layer base-class.
#
# This class implements standard methods. If necessary, some of them must be
# overridden by board-specific sub-classes.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
# ----------------------------------------------------------------------------

import board
import time
try:
  import alarm
except:
  pass
from digitalio import DigitalInOut, Direction

class HalBase:
  def __init__(self):
    """ constructor """
    self._display = None

  def status_led(self,value):
    """ set status LED """
    if not hasattr(self,"_led"):
      self._led = DigitalInOut(board.LED)
      self._led.direction = Direction.OUTPUT
    self._led.value = value

  def bat_level(self):
    """ return battery level """
    if hasattr(board,"VOLTAGE_MONITOR"):
      from analogio import AnalogIn
      adc = AnalogIn(board.VOLTAGE_MONITOR)
      level = adc.value *  3 * 3.3 / 65535
      adc.deinit()
      return level
    else:
      return 0.0

  def wifi(self):
    """ return wifi-interface """
    from wifi_helper_builtin import WifiHelper
    return WifiHelper(debug=True)

  def get_display(self):
    """ return display """
    if not self._display:
      self._display = getattr(board,'DISPLAY',None)
    return self._display

  def show(self,content):
    """ show and refresh the display """

    self._display.root_group = content

    if self._display.time_to_refresh > 0.0:
      # ttr will be >0 only if system is on running on USB-power
      time.sleep(self._display.time_to_refresh)
    self.display.refresh()

    duration = time.monotonic()-start
    update_time = self.display.time_to_refresh - duration
    if update_time > 0.0:
      # might running on battery-power: save some power using light-sleep
      time_alarm = alarm.time.TimeAlarm(
        monotonic_time=time.monotonic()+update_time)
      alarm.light_sleep_until_alarms(time_alarm)

  def get_rtc_ext(self):
    """ return external rtc, if available """
    return None

  def shutdown(self):
    """ shutdown system """
    pass

  def sleep(self,duration):
    """ sleep for the given duration in seconds """
    time.sleep(duration)

  def get_keys(self):
    """ return list of pin-numbers for up, down, left, right """
    # format is (active-state,[key1,...])
    return None
