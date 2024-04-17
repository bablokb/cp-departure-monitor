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

import gc
import builtins
import time
import board
import traceback

from settings import app_config

# --- application class   ----------------------------------------------------

class Application:

  RED   = [255,0,0]
  GREEN = [0,255,0]

  # --- constructor   --------------------------------------------------------

  def __init__(self,dataprovider,uiprovider,with_rtc=True,debug=False):
    """ constructor """

    self._debug = debug
    self._setup(with_rtc)  # setup hardware
    if with_rtc and self._rtc_ext:
      self._rtc_ext.update_time(app_config.time_url)
    dataprovider.set_wifi(self.wifi)

    self._dataprovider = dataprovider
    self._uiprovider   = uiprovider
    self.data = {}

  # --- get HAL   ------------------------------------------------------------

  # Import HAL (hardware-abstraction-layer).
  # This expects an object "impl" within the implementing hal_file.
  # All hal implementations are within src/hal/. Filenames must be
  # board.board_id.py, e.g. src/hal/pimoroni_inky_frame_5_7.py

  def _get_hal(self):
    """ read and return hal-object """

    try:
      hal_file = "hal."+board.board_id.replace(".","_")
      hal = builtins.__import__(hal_file,None,None,["impl"],0)
      self.msg("using board-specific implementation")
    except Exception as ex:
      self.msg(f"info: no board specific HAL")
      hal_file = "hal.hal_default"
      hal = builtins.__import__(hal_file,None,None,["impl"],0)
      self.msg("info: using default implementation from HalBase")
    return hal

  # --- hardware setup   -----------------------------------------------------

  def _setup(self,with_rtc):
    """ setup hardware """

    hal = self._get_hal()
    
    self.display    = hal.impl.get_display()
    self.is_pygame  = hasattr(self.display,"check_quit")
    self.bat_level  = hal.impl.bat_level
    self.led        = hal.impl.led
    self.keys       = hal.impl.get_keys()
    self.wifi       = hal.impl.wifi(self._debug)
    self._shutdown  = hal.impl.shutdown
    self.sleep      = hal.impl.sleep
    self._show      = hal.impl.show
    self.reset      = hal.impl.reset_if_needed
    if with_rtc:
      self._rtc_ext = hal.impl.get_rtc_ext()
      if self._rtc_ext:
        self._rtc_ext.set_wifi(self.wifi)

    gc.collect()

  # --- print debug-message   ------------------------------------------------

  def msg(self,text):
    """ print (debug) message """
    if self._debug:
      print(text)

  # --- update data from server   --------------------------------------------

  def update_data(self):
    """ update data """

    self.blink(0.3,color=Application.RED)
    self.data["bat_level"] = self.bat_level()

    start = time.monotonic()
    self._dataprovider.update_data(self.data)
    duration = time.monotonic()-start
    self.blink(0.3,color=Application.GREEN)
    self.msg(f"update_data (dataprovider): {duration:f}s")

  # --- create ui   ----------------------------------------------------------

  def create_ui(self):
    """ create UI. UI-provider might buffer UI for performance """

    start = time.monotonic()
    self._ui = self._uiprovider.create_ui(self.display)
    duration = time.monotonic()-start
    self.msg(f"create_content (uiprovider): {duration:f}s")

  # --- update display   -----------------------------------------------------

  def update_display(self):
    """ update display """

    # update UI with current model
    start = time.monotonic()
    self._uiprovider.update_ui(self.data)
    duration = time.monotonic()-start
    self.msg(f"update_ui (uiprovider): {duration:f}s")

    # and show content on screen
    start = time.monotonic()
    self._show(self._ui)
    duration = time.monotonic()-start
    self.msg(f"show (HAL): {duration:f}s")

  # --- free memory from UI   ------------------------------------------------

  def free_ui_memory(self):
    """ free memory used by UI and display """

    if not self.is_pygame:
      self.msg(f"free memory before clear of UI: {gc.mem_free()}")
      self.display.root_group = None
      self._uiprovider.clear_ui()
      #gc.collect()
      self.msg(f"free memory after clear of UI: {gc.mem_free()}")

  # --- blink status-led   ---------------------------------------------------

  def blink(self,duration,color=RED):
    """ blink status-led once for the given duration """
    self.led(1,color=color)
    time.sleep(duration)
    self.led(0,color=color)

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self):
    """ turn off device """
    self._shutdown()

  # --- main application code   ----------------------------------------------

  def run(self):
    """ main application logic usually called in a loop """

    try:
      self.update_data()    # update data before UI is created
      self.create_ui()      # ui-provider should buffer this for performance
      self.update_display()
    except Exception as ex:
      raise
