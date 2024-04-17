# ----------------------------------------------------------------------------
# HalBase: Hardware-Abstraction-Layer base-class.
#
# This class implements standard methods. If necessary, some of them must be
# overridden by board-specific sub-classes.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-weather
# ----------------------------------------------------------------------------

import board
import time
try:
  import alarm
except:
  pass
from digitalio import DigitalInOut, Direction

try:
  from settings import hw_config
except:
  pass

class HalBase:
  def __init__(self):
    """ constructor """
    self._display = None
    self.I2C  = self._get_attrib('I2C')
    self.SDA  = self._get_attrib('SDA')
    self.SCL  = self._get_attrib('SCL')
    self.SPI  = self._get_attrib('SPI')
    self.SCK  = self._get_attrib('SCK')
    self.MOSI = self._get_attrib('MOSI')
    self.MISO = self._get_attrib('MISO')

  def _get_attrib(self,attrib):
    """ get attribute from board or from settings """
    value = getattr(board,attrib,None)
    if value is None:
      try:
        value = getattr(hw_config,attrib,None)
      except:
        pass
    return value

  def _init_led(self):
    """ initialize LED/Neopixel """
    if hasattr(board,'NEOPIXEL'):
      if not hasattr(self,'_pixel'):
        if hasattr(board,'NEOPIXEL_POWER'):
          # need to do this first,
          # https://github.com/adafruit/Adafruit_CircuitPython_MagTag/issues/75
          self._pixel_poweroff = DigitalInOut(board.NEOPIXEL_POWER)
          self._pixel_poweroff.direction = Direction.OUTPUT
        import neopixel
        self._pixel = neopixel.NeoPixel(board.NEOPIXEL,1,
                                        brightness=0.1,auto_write=False)
    else:
      led = self._get_attrib('LED')
      if led and not hasattr(self,'_led'):
        self._led = DigitalInOut(led)
        self._led.direction = Direction.OUTPUT

    # replace method with noop
    self._init_led = lambda: None

  def led(self,value,color=[255,0,0]):
    """ set status LED/Neopixel """
    self._init_led()
    if hasattr(self,'_pixel'):
      if hasattr(self,'_pixel_poweroff'):
        self._pixel_poweroff.value = not value
      if value:
        self._pixel.fill(color)
        self._pixel.show()
      elif not hasattr(self,'_pixel_poweroff'):
        self._pixel.fill(0)
        self._pixel.show()
    elif hasattr(self,'_led'):
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

  def wifi(self,debug=False):
    """ return wifi-interface """
    from wifi_helper_builtin import WifiHelper
    return WifiHelper(debug=debug)

  def get_display(self):
    """ return display """
    if not self._display:
      self._display = self._get_attrib('DISPLAY')
      if callable(self._display):
        # from hw_config!
        self._display = self._display()
    return self._display

  def show(self,content):
    """ show and refresh the display """

    self._display.root_group = content

    if hasattr(self._display,"time_to_refresh"):
      while self._display.time_to_refresh > 0.0:
        # ttr will be >0 only if system is on running on USB-power
        time.sleep(self._display.time_to_refresh)

    start = time.monotonic()
    while True:
      try:
        self._display.refresh()
        break
      except RuntimeError:
        pass
    duration = time.monotonic()-start

    if hasattr(self._display,"time_to_refresh"):
      update_time = self._display.time_to_refresh - duration
      if update_time > 0.0:
        # might running on battery-power: save some power using light-sleep
        time_alarm = alarm.time.TimeAlarm(
          monotonic_time=time.monotonic()+update_time)
        alarm.light_sleep_until_alarms(time_alarm)

  def get_rtc_ext(self):
    """ return external rtc, if available """
    try:
      return hw_config.get_rtc_ext()
    except:
      return None

  def shutdown(self):
    """ shutdown system """
    pass

  def reset_if_needed(self):
    """ reset device (workaround for MemoryError) """
    pass

  def sleep(self,duration):
    """ sleep for the given duration in seconds """
    time.sleep(duration)

  def get_keys(self):
    """ return list of pin-numbers for up, down, left, right """
    # format is (active-state,[key1,...])
    try:
      return hw_config.get_keys()
    except:
      return None
