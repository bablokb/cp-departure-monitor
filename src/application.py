# -------------------------------------------------------------------------
# Generic application framework class.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# -------------------------------------------------------------------------

# --- imports   -----------------------------------------------------------

import builtins
import time
import board
import traceback

try:
  import alarm
except:
  pass

# Import HAL (hardware-abstraction-layer).
# This expects an object "impl" within the implementing hal_file.
# All hal implementations are within src/hal/. Filenames must be
# board.board_id.py, e.g. src/hal/pimoroni_inky_frame_5_7.py

try:
  hal_file = "hal."+board.board_id.replace(".","_")
  hal = builtins.__import__(hal_file,None,None,["impl"],0)
  print("using board-specific implementation")
except Exception as ex:
  print(f"!!! error or no board specific HAL: {ex}. Trouble ahead !!!")
  hal_file = "hal.hal_default"
  hal = builtins.__import__(hal_file,None,None,["impl"],0)
  print("using default implementation")

from settings import app_config

# --- application class   ----------------------------------------------------

class Application:

  # --- constructor   --------------------------------------------------------

  def __init__(self,dataprovider,uiprovider,with_rtc=True):
    """ constructor """

    self._setup(with_rtc)  # setup hardware
    if with_rtc and self._rtc_ext:
      self._rtc_ext.update_time(app_config.time_url)
    dataprovider.set_wifi(self.wifi)

    self._dataprovider = dataprovider
    self._uiprovider   = uiprovider

  # --- setup hardware   -----------------------------------------------------

  def _setup(self,with_rtc):
    """ setup hardware """
    
    self.display    = hal.impl.get_display()
    self.is_pygame  = hasattr(self.display,"check_quit")
    self.bat_level  = hal.impl.bat_level
    self._led       = hal.impl.status_led
    self.wifi       = hal.impl.wifi()
    self._shutdown  = hal.impl.shutdown
    if with_rtc:
      self._rtc_ext = hal.impl.get_rtc_ext()
      if self._rtc_ext:
        self._rtc_ext.set_wifi(self.wifi)

  # --- update data from server   --------------------------------------------

  def update_data(self):
    """ update data """

    self.data = {}
    self.data["bat_level"] = self.bat_level()

    start = time.monotonic()
    self._dataprovider.update_data(self.data)
    duration = time.monotonic()-start
    print(f"update_data (dataprovider): {duration:f}s")

    start = time.monotonic()
    self._uiprovider.update_data(self.data)
    duration = time.monotonic()-start
    print(f"update_data (uiprovider): {duration:f}s")

  # --- update display   -----------------------------------------------------

  def update_display(self,content):
    """ update display """

    start = time.monotonic()
    if self.is_pygame:
      self.display.show(content)
    else:
      self.display.root_group = content
    print(f"update_display (show): {time.monotonic()-start:f}s")
    start = time.monotonic()

    if not self.is_pygame and self.display.time_to_refresh > 0.0:
      # ttr will be >0 only if system is on USB-power (running...)
      print(f"time-to-refresh: {self.display.time_to_refresh}")
      time_alarm = alarm.time.TimeAlarm(
        monotonic_time=time.monotonic()+self.display.time_to_refresh)
      alarm.light_sleep_until_alarms(time_alarm)

    self.display.refresh()
    duration = time.monotonic()-start
    print(f"update_display (refreshed): {duration:f}s")

    if not self.is_pygame:
      update_time = self.display.time_to_refresh - duration
      if update_time > 0.0:
        print(f"update-time: {update_time} (sleeping...)")
        time_alarm = alarm.time.TimeAlarm(
          monotonic_time=time.monotonic()+update_time)
        alarm.light_sleep_until_alarms(time_alarm)
      print("update finished!")

  # --- blink status-led   ---------------------------------------------------

  def blink(self,duration):
    """ blink status-led once for the given duration """
    self._led(1)
    time.sleep(duration)
    self._led(0)

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self):
    """ turn off device """
    self._shutdown()

  # --- main application code   ----------------------------------------------

  def run(self):
    """ main application loop """

    try:
      self.update_data()
    except Exception as ex:
      try:
        self._uiprovider.handle_exception(ex)
      except Exception as ex2:
        # cannot do anything here
        traceback.print_exception(ex2)
    finally:
      content = self._uiprovider.create_content(self.display)
      self.update_display(content)
